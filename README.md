# 🛡️ AEGIS VOICE
###### *Aegis: Protection, backing, and guidance. Aegis Voice acts as your intelligent digital sponsor, operating silently in the background to protect, guide, and shield your real-time conversations from modern social engineering.*

**Team Name:** Dhvani  
**Team Members:** Dhvani (Solo Developer)  

---

## 🚨 The Problem: The Screen-First Reality
The world has fundamentally shifted. Today, our reliance on online activity is absolute banking, corporate negotiations, healthcare, and socializing are all conducted through a screen. As our lives moved online, so did the criminals. 

In 2026, scammers have evolved beyond simple phishing emails and cellular phone calls. They now heavily exploit desktop VoIP applications to execute high-stakes social engineering. **Business Email Compromise (BEC)** and **CEO Fraud** now happen live on video calls, where deepfakes and psychological coercion are used to pressure employees into urgent wire transfers. Furthermore, existing cloud-based AI transcription tools require sending your sensitive, real-time audio to external servers. For enterprises and privacy-conscious individuals, this creates a massive security risk. Standard LLMs also suffer from "hallucinations," flagging innocent conversations as threats and causing users to ignore actual warnings.

## 💡 The Solution: Real-Time, Local-First Protection
**Aegis Voice** is a 100% local, zero-cloud, real-time scam interceptor for desktop VoIP applications. It acts as an invisible bodyguard for your system audio. By analyzing conversations locally in real-time, it provides non-intrusive, tiered visual warnings before you fall victim to coercion, ensuring your data never leaves your machine.

###  Core Capabilities & Impact
*   **Hybrid AI Engine:** Pioneers a two-tier detection system combining instant Regex "reflexes" (Tier 1) with deep semantic LLM analysis (Tier 2). Features custom **Python Anti-Hallucination Guardrails** to aggressively block false positives.
*   **Zero-Trust Privacy Architecture:** Guarantees **Zero Data Leakage**. Audio is captured, transcribed, evaluated, and discarded in RAM within milliseconds. Nothing is ever written to the hard drive or sent to the cloud.
*   **Psychologically Calibrated UX:** Features a **Glassmorphic, Click-Through Transparent Overlay**. Introduces a **Tiered Alert System** (Yellow Advisory ➔ Orange Warning ➔ Red Critical) to prevent panic and alert fatigue.
*   **Universal Desktop Protection:** Closes the desktop VoIP gap. Because it hooks into OS-level audio, it protects users across any platform where modern scams happen.

---

##  User Experience: The Tiered Alert System
Instead of blinding the user with constant red alarms, Aegis Voice uses a psychologically calibrated, color-coded overlay system in real-time:
*   🟡 **Yellow (10-25 Score):** *Low Risk Advisory* (Bell Icon). Subtle yellow screen pulse. Indicates suspicious keywords detected.
*   🟠 **Orange (26-49 Score):** *Medium Risk Warning* (Exclamation Icon). Orange screen pulse. Indicates psychological coercion or urgency detected.
*   🔴 **Red (50+ Score):** *High Risk Scam Detected* (Hazard Icon). Red screen pulse. Indicates confirmed financial threat.
*   *Note: The UI is completely click-through, ensuring it never interferes with the user's actual workflow or video call.*

---

##  Architecture & Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Audio Capture** | Python `soundcard` (WASAPI) | OS-level system audio loopback |
| **Voice Activity** | `webrtcvad` | Filters silence to save CPU |
| **Transcription (STT)** | `faster-whisper` (small.int8) | Local, blazing-fast speech-to-text |
| **Semantic Brain** | `Ollama` + `Qwen2:1.5b` | Local LLM for intent & coercion analysis |
| **Bridge** | `websockets` (Asyncio) | Real-time, non-blocking UI communication |
| **Desktop Shell** | `Electron` | Transparent, always-on-top overlay |
| **Frontend** | `React` + `Vite` | Glassmorphic, tiered alert UI |

---

## 🚀 How to Run on Your PC

*Note: The current MVP is optimized for **Windows 10/11** to utilize WASAPI loopback audio capture. The underlying Python/Electron architecture is cross-platform and can be adapted for macOS (via BlackHole) and Linux (via PulseAudio) in future iterations.*

### Prerequisites
1. **Python 3.12+** installed and added to PATH.
2. **Node.js 18+** (LTS recommended) installed.
3. **Ollama** installed ([Download here](https://ollama.com)).
4. **Windows 10/11** (Required for WASAPI Loopback audio capture).

Step 1: Clone the Repository
```bash
git clone https://github.com/Dhvani30/AegisVoice.git
cd AegisVoice
```

Step 2: Setup the Local AI (Ollama)
Open your terminal and pull the lightweight local LLM used for semantic analysis:
```bash
ollama pull qwen2:1.5b
```

Step 3: Setup Python Backend
Create a virtual environment and install the audio/AI dependencies:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install soundcard faster-whisper webrtcvad websockets numpy requests
```

Step 4: Setup React/Electron Frontend
Navigate to the UI folder and install Node dependencies:
```bash
cd aegis-ui
npm install
cd ..
```

Step 5: Launch Aegis Voice
You can run the app using the provided batch script, or manually:
Option A: One-Click Launcher (Recommended)
```bash
.\run_aegis.bat
```

(This automatically handles port clearing, starts the Python backend, and launches the Electron overlay).
Option B: Manual Launch
Terminal 1 (Backend):
```bash
.\venv\Scripts\activate
python aegis_engine.py
```

Terminal 2 (Frontend):
```bash
cd aegis-ui
npm run start
```

## 🧪 Testing the Demo
Ensure the app is running and the transparent overlay is active.
Universal Compatibility: Because Aegis Voice hooks directly into your OS-level system audio, it works universally across any desktop application. Whether you are on a Google Meet pitch, a Zoom corporate sync, a Discord gaming call, or a Microsoft Teams interview, Aegis Voice is listening and protecting in real-time.
Open YouTube and play a known scam recording (Search: "IRS scam call recording").
Watch as the system transcribes locally and triggers the Yellow ➔ Orange ➔ Red alerts on your screen without interrupting your video player!

## Submission Links
* 📂 GitHub Repository: https://github.com/Dhvani30/AegisVoice
* 🎥 Demo Video (2-5 Mins): https://drive.google.com/drive/folders/1Bp6uH_ZvXk_B8aTXovwYk3zGM5ZGP7CT?usp=sharing


## 🔮 Future Scope & Scalability
* Phase 1: Multi-Language & Browser Extension: Adding Hindi/Tamil Whisper models and a Chrome Extension for WebRTC-based VoIP.
* Phase 2: Voice Biometrics: Integrating deepfake voice detection to verify if the caller is actually human.
* Phase 3: Enterprise CISO Dashboard: Aggregating anonymized threat intelligence for corporate security teams to track live BEC attempts across an organization.
