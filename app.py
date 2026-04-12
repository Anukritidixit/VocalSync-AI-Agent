import streamlit as st
import json
import time
from groq import Groq
from actions import create_local_file, summarize_content

# --- 1. PAGE SETUP & CUSTOM CSS ---
st.set_page_config(page_title="VocalSync AI", page_icon="✨", layout="wide")

# Sleek Custom CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stChatMessage {
        border-radius: 12px !important;
        padding: 10px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent !important;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# API Config
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
client = Groq(api_key=GROQ_API_KEY)

# Init session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_actions" not in st.session_state:
    st.session_state.pending_actions = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0 

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("✨ VocalSync")
    st.caption("Agent Pro Edition")
    st.divider()
    
    st.subheader("⚙️ Settings")
    human_in_loop = st.toggle("Human-in-the-Loop", value=True, help="Review code before saving.")
    
    st.divider()
    st.subheader("⏱️ Telemetry")
    stt_placeholder = st.empty()
    llm_placeholder = st.empty()
    
    st.divider()
    if st.button("🗑️ Clear Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_actions = []
        st.session_state.audio_key += 1 
        st.rerun()

# --- 3. MAIN UI LAYOUT ---
st.title("🎙️ VocalSync Workspace")

# A. The "Action Center"
if st.session_state.pending_actions:
    st.warning("⚡ **Action Required:** Review generated code before execution.")
    for i, action in enumerate(st.session_state.pending_actions):
        filename = action.get('filename', 'untitled.txt')
        original_content = action.get('content', '')
        
        with st.container(border=True):
            st.write(f"📄 **{filename}**")
            edited_content = st.text_area("Source Code", value=original_content, height=150, key=f"edit_code_{i}", label_visibility="collapsed")
            
            col1, col2, _ = st.columns([1, 1, 4])
            if col1.button("✅ Save File", key=f"approve_{i}", type="primary"):
                res = create_local_file(filename, edited_content)
                st.success(res)
                st.session_state.messages.append({"role": "assistant", "content": f"Executed: {res}"})
                st.session_state.pending_actions.pop(i)
                st.rerun()
            if col2.button("❌ Discard", key=f"reject_{i}"):
                st.session_state.pending_actions.pop(i)
                st.rerun()

# B. The Locked Chat Window
chat_window = st.container(height=450, border=True)

with chat_window:
    if not st.session_state.messages:
        st.markdown("<br><br><br><div style='text-align: center; color: #888;'><h3>Workspace is empty</h3><p>Use the Command Center below to start building.</p></div>", unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

st.write("<br>", unsafe_allow_html=True)

# C. The Tabbed Command Center
with st.container(border=True):
    tab_text, tab_voice = st.tabs(["⌨️ Text Command", "🎙️ Voice Command"])
    
    submit_pressed = False
    user_text_input = ""
    audio_file = None

    with tab_text:
        col1, col2 = st.columns([5, 1])
        with col1:
            user_text_input = st.text_input("Text Input", key=f"text_{st.session_state.audio_key}", placeholder="E.g., Write a python script to calculate fibonacci...", label_visibility="collapsed")
        with col2:
            if st.button("🚀 Send", key="submit_text", use_container_width=True, type="primary"):
                submit_pressed = True

    with tab_voice:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            recorded_audio = st.audio_input("Record", key=f"mic_{st.session_state.audio_key}", label_visibility="collapsed")
        with col2:
            uploaded_audio = st.file_uploader("Upload", type=["wav", "mp3", "m4a"], key=f"upload_{st.session_state.audio_key}", label_visibility="collapsed")
        with col3:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("🚀 Process", key="submit_audio", use_container_width=True, type="primary"):
                audio_file = recorded_audio or uploaded_audio
                submit_pressed = True

# --- 4. EXECUTION LOGIC ---
if submit_pressed and not st.session_state.pending_actions:
    user_text = ""
    try:
        if user_text_input.strip():
            user_text = user_text_input.strip()
            st.session_state.messages.append({"role": "user", "content": f"**User:** {user_text}"})
            
        elif audio_file:
            start_time = time.time()
            with st.spinner("Transcribing audio..."):
                with open("temp.wav", "wb") as f:
                    f.write(audio_file.read())
                with open("temp.wav", "rb") as file:
                    transcription = client.audio.transcriptions.create(
                      file=("temp.wav", file.read()),
                      model="whisper-large-v3",
                    )
            stt_placeholder.metric("Whisper Large v3", f"{time.time() - start_time:.2f}s")
            user_text = transcription.text.strip()
            
            if not user_text:
                st.error("Audio unclear. Please try again.")
                st.stop()
                
            st.session_state.messages.append({"role": "user", "content": f"🎤 *Voice:* {user_text}"})
        
        else:
            st.warning("⚠️ Please provide input first.")
            st.stop()

        start_time = time.time()
        with st.spinner("Processing Intent..."):
            system_prompt = """
            You are a local AI assistant. Break down the request into an array of actions.
            Allowed intents: [CREATE_FILE, WRITE_CODE, SUMMARIZE, CHAT].
            STRICT RULES:
            1. NEVER create a separate action just for a folder. Folders are created automatically if you include them in the filename.
            2. Output exactly ONE action per file. Do not repeat the same file.
            Return ONLY JSON format: { "actions": [ {"intent": "CATEGORY", "filename": "name.txt", "content": "data or response"} ] }
            """
            
            # --- THE MEMORY FIX: Passing the chat history to the LLM ---
            llm_messages = [{"role": "system", "content": system_prompt}]
            
            # Feed the last 10 messages into the AI's "brain" so it remembers the context
            for msg in st.session_state.messages[-10:]:
                llm_messages.append({"role": msg["role"], "content": msg["content"]})
            
            chat_completion = client.chat.completions.create(
                messages=llm_messages,
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
        llm_placeholder.metric("Llama 3.3 70B", f"{time.time() - start_time:.2f}s")
        
        data = json.loads(chat_completion.choices[0].message.content)
        actions = data.get("actions", [])

        seen_filenames = set()

        for action in actions:
            intent = action.get('intent', 'UNKNOWN')
            content = action.get('content', '')
            filename = action.get('filename', 'untitled.txt')
            
            if filename in seen_filenames or content.strip() == "" or intent == "CREATE_FOLDER":
                continue
            
            with st.chat_message("assistant"):
                st.caption(f"↳ Action: {intent}")

                if intent == "CHAT":
                    st.write(content)
                    st.session_state.messages.append({"role": "assistant", "content": content})
                elif intent == "SUMMARIZE":
                    st.info(f"Summary: {content}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Summary: {content}"})
                elif intent in ["CREATE_FILE", "WRITE_CODE"]:
                    seen_filenames.add(filename)
                    if human_in_loop:
                        is_already_pending = any(p.get('filename') == filename for p in st.session_state.pending_actions)
                        if not is_already_pending:
                            st.session_state.pending_actions.append(action)
                    else:
                        res = create_local_file(filename, content)
                        st.success(res)
                        st.session_state.messages.append({"role": "assistant", "content": res})

        st.session_state.audio_key += 1
        time.sleep(0.5) 
        st.rerun()

    except json.JSONDecodeError:
        st.error("JSON formatting error. Please try again.")
    except Exception as e:
        st.error(f"System error: {str(e)}")