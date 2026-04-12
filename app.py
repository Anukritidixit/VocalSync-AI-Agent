import streamlit as st
import json
import time
from groq import Groq
from actions import create_local_file, summarize_content

# --- CONFIGURATION ---
st.set_page_config(page_title="VocalSync", layout="wide")

# ---> REPLACE THIS WITH YOUR REAL KEY FOR TESTING <---
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
client = Groq(api_key=GROQ_API_KEY)

# --- INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_actions" not in st.session_state:
    st.session_state.pending_actions = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0 # Used to reset the mic and prevent the error bug

# --- SIDEBAR (SETTINGS & CLEAR CHAT) ---
with st.sidebar:
    st.header("⚙️ Agent Settings")
    human_in_loop = st.toggle("Human-in-the-Loop", value=True, help="Review and edit files before saving.")
    
    st.divider()
    st.header("⏱️ Model Benchmarks")
    stt_placeholder = st.empty()
    llm_placeholder = st.empty()
    
    st.divider()
    # THIS CLEARS THE CHAT
    if st.button("🗑️ Clear Chat / Start New", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_actions = []
        st.session_state.audio_key += 1 # Resets the mic widget
        st.rerun()

# --- MAIN UI ---
st.title("🎙️ VocalSync AI Agent - Pro Edition")
st.caption("Compound Commands | Editable Code | Live Benchmarking")

# --- 1. PENDING ACTIONS (EDITABLE APPROVAL UI) ---
if st.session_state.pending_actions:
    st.warning("⚠️ Pending operations require your approval.")
    for i, action in enumerate(st.session_state.pending_actions):
        filename = action.get('filename', 'untitled.txt')
        original_content = action.get('content', '# No code generated')
        
        with st.expander(f"Review & Edit: {filename}", expanded=True):
            #  This makes the code editable by the user!
            edited_content = st.text_area("Edit Code before saving:", value=original_content, height=200, key=f"edit_code_{i}")
            
            col1, col2 = st.columns(2)
            if col1.button("✅ Approve & Save", key=f"approve_{i}"):
                # Notice we are passing the edited_content now!
                res = create_local_file(filename, edited_content)
                st.success(res)
                st.session_state.messages.append({"role": "assistant", "content": f"Executed: {res}"})
                st.session_state.pending_actions.pop(i)
                st.rerun()
            if col2.button("❌ Reject", key=f"reject_{i}"):
                st.error("Operation cancelled.")
                st.session_state.pending_actions.pop(i)
                st.rerun()

# --- 2. DISPLAY CHAT HISTORY ---
st.divider()
st.subheader("💬 Chat History")
if not st.session_state.messages:
    st.info("No messages yet. Speak a command below to start!")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# --- 3. INPUT SECTION ---
st.divider()
st.write("### 🎤 Provide your command:")
col1, col2 = st.columns(2)
with col1:
    # Adding the dynamic key here fixes the Streamlit "error has occurred" bug
    recorded_audio = st.audio_input("Record from mic", key=f"mic_{st.session_state.audio_key}")
with col2:
    uploaded_audio = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a"], key=f"upload_{st.session_state.audio_key}")

audio_file = recorded_audio or uploaded_audio

# Process only if there's audio and no pending approvals
if audio_file and not st.session_state.pending_actions:
    try:
        # Step 1: STT
        start_time = time.time()
        with st.spinner("🎧 Transcribing audio..."):
            with open("temp.wav", "wb") as f:
                f.write(audio_file.read())
            with open("temp.wav", "rb") as file:
                transcription = client.audio.transcriptions.create(
                  file=("temp.wav", file.read()),
                  model="whisper-large-v3",
                )
        stt_placeholder.metric("Whisper Latency", f"{time.time() - start_time:.2f}s")
        
        user_text = transcription.text.strip()
        if not user_text:
            st.error("Could not hear speech.")
            st.stop()
            
        st.session_state.messages.append({"role": "user", "content": f"🎤 *Audio Input:* {user_text}"})

        # Step 2: Intent
        start_time = time.time()
        with st.spinner("🧠 Analyzing Intent..."):
            system_prompt = """
            You are a local AI assistant. Break down the request into an array of actions.
            Allowed intents: [CREATE_FILE, WRITE_CODE, SUMMARIZE, CHAT].
            Return ONLY JSON format:
            { "actions": [ {"intent": "CATEGORY", "filename": "name.txt", "content": "data or response"} ] }
            """
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
        llm_placeholder.metric("Llama 3.3 Latency", f"{time.time() - start_time:.2f}s")
        
        data = json.loads(chat_completion.choices[0].message.content)
        actions = data.get("actions", [])

        # Step 3: Execution
        for action in actions:
            intent = action.get('intent', 'UNKNOWN')
            content = action.get('content', '')
            filename = action.get('filename', 'untitled.txt')
            
            if intent in ["CREATE_FILE", "WRITE_CODE"]:
                if human_in_loop:
                    st.session_state.pending_actions.append(action)
                else:
                    res = create_local_file(filename, content)
                    st.session_state.messages.append({"role": "assistant", "content": res})
            elif intent == "SUMMARIZE":
                st.session_state.messages.append({"role": "assistant", "content": f"**Summary:** {content}"})
            elif intent == "CHAT":
                st.session_state.messages.append({"role": "assistant", "content": content})
        
        # Reset the audio widget to prevent the Streamlit crash bug
        st.session_state.audio_key += 1
        st.rerun()

    except json.JSONDecodeError:
        st.error("❌ The AI model returned an invalid format. Please try again.")
    except Exception as e:
        st.error(f"❌ System error: {str(e)}")