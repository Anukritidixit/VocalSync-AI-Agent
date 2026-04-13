# VocalSync: Voice-Controlled AI Agent

VocalSync is a voice-activated AI agent that translates natural speech into secure, local system actions. I built this to bridge the gap between verbal commands and everyday developer tasks, allowing users to create files, write code, and summarize text completely hands-free.

Under the hood, it uses an LLM to parse intent and securely execute Python actions on your local machine, wrapped in a clean Streamlit interface.

## What It Does (Core Features)
* **Flexible Audio Input:** Speak directly into your microphone or upload pre-recorded `.wav`/`.mp3` files.
* **Fast Transcription:** Uses the Whisper Large v3 model for highly accurate, sub-second Speech-to-Text.
* **Dynamic Intent Mapping:** Powered by Llama 3.3, the system doesn't rely on basic keyword matching. It actually understands what you want to do (e.g., Create File, Write Code, Summarize, or just Chat).
* **Sandboxed Execution:** Security is a priority. All file operations and code generation are strictly locked to a dedicated `output/` directory using `os.path.basename` to prevent accidental overwrites.

##  Advanced Features 
To make the agent more robust, I implemented a few extra layers:
* **Compound Commands:** You can string multiple tasks together in one sentence (e.g., *"Summarize this text and write a Python file with a loop"*). The system breaks it down and handles them sequentially.
* **Human-in-the-Loop (Safety First):** Before the agent writes anything to your local disk, execution pauses. The UI shows you the proposed code/file, and you must explicitly click "Approve" or "Reject."
* **Session Memory:** The UI behaves like a continuous chat, remembering previous context and actions.
* **Live Benchmarking:** A sidebar tracker monitors the latency of the STT and LLM API calls in real-time.
* **Graceful Degradation:** Built-in error handling ensures that garbled audio or unmapped intents return a friendly prompt rather than crashing the app.

##  Architecture & Engineering Decisions
**The Pipeline:** `Audio` ➔ `Whisper (STT)` ➔ `Llama 3.3 (Intent JSON)` ➔ `Local Python Execution`

**The Hardware Pivot:** My original architecture relied on running Whisper and Ollama entirely locally. However, during development on a Windows machine, I ran into persistent `[WinError 2]` pathing issues regarding how the local Whisper library interacts with underlying FFmpeg binaries. 

Because system reliability and speed are critical for voice agents, I pivoted to utilizing the **Groq API** for both transcription and intent routing. This hardware workaround bypassed the local binary bottlenecks, delivering incredibly fast cloud-inference while keeping the actual tool execution (the "hands" of the agent) safely on the local machine.

##  Quick Start Setup
1. **Clone the repository**
   ```bash
   git clone [https://github.com/Anukritidixit/VocalSync-AI-Agent.git](https://github.com/Anukritidixit/VocalSync-AI-Agent.git)
   cd VocalSync-AI-Agent
