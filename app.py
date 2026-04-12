import streamlit as st
import json
import os
from groq import Groq
from actions import create_local_file, summarize_content

# --- CONFIGURATION ---
st.set_page_config(page_title="AI Voice Agent", page_icon="🎙️", layout="centered")

# Paste your copied key inside the quotes below
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
client = Groq(api_key=GROQ_API_KEY)

# --- UI HEADER ---
st.title("🎙️ Voice-Controlled AI Agent")
st.caption("Built for robust execution using Whisper API and Llama 3.")

# --- MAIN LOGIC ---
st.write("### Choose how to provide your command:")
col1, col2 = st.columns(2)

with col1:
    recorded_audio = st.audio_input("🎙️ Record from mic")
with col2:
    uploaded_audio = st.file_uploader("📁 Or upload an audio file", type=["wav", "mp3", "m4a"])

# Use whichever one the user provided
audio_file = recorded_audio or uploaded_audio

if audio_file:
    try:
        # 1. Process Audio
        with st.status("🎧 Processing Audio...", expanded=True) as status:
            st.write("Saving temporary audio file...")
            with open("temp.wav", "wb") as f:
                f.write(audio_file.read())
            
            st.write("Transcribing with Groq Whisper...")
            with open("temp.wav", "rb") as file:
                transcription = client.audio.transcriptions.create(
                  file=("temp.wav", file.read()),
                  model="whisper-large-v3",
                )
            user_text = transcription.text.strip()
            
            if not user_text:
                st.error("Could not hear any speech. Please try again.")
                st.stop()
                
            st.success(f"**Transcription:** {user_text}")
            status.update(label="Audio Processed!", state="complete", expanded=False)

        # 2. Intent Classification (The Brain)
        with st.status("🧠 Analyzing Intent...", expanded=True) as status:
            system_prompt = """
            You are a local AI assistant. Classify the user's intent into ONE of these categories:
            [CREATE_FILE, WRITE_CODE, SUMMARIZE, CHAT].
            
            Return ONLY a raw JSON object with no markdown formatting or extra text.
            Format: {"intent": "CATEGORY", "filename": "example.txt", "content": "data to write or chat response"}
            """
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            
            raw_json = chat_completion.choices[0].message.content
            data = json.loads(raw_json)
            st.json(data) 
            status.update(label="Intent Analyzed!", state="complete", expanded=False)

       # 3. Tool Execution (The Hands)
        st.subheader("⚙️ Execution Result")
        intent = data.get('intent', 'UNKNOWN')
        content = data.get('content', '')  # <--- Moved this up so CHAT can see it!
        
        if intent in ["CREATE_FILE", "WRITE_CODE"]:
            filename = data.get('filename', 'untitled.txt')
            result_msg = create_local_file(filename, content)
            
            if "✅" in result_msg:
                st.success(result_msg)
                with st.expander("View Generated File Content"):
                    st.code(content)
            else:
                st.error(result_msg)
                
        elif intent == "SUMMARIZE":
            st.info(summarize_content(user_text))
            
        elif intent == "CHAT":
            st.write("🗣️ **Agent Response:**")
            st.info(content)
            
        else:
            st.warning("Command not recognized. Try asking me to create a file or write code.")

    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")