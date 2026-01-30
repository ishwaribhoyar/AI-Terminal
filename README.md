<div align="center">

# 🤖 IVERI

### Voice-Controlled AI Assistant for Raspberry Pi

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5--nano-412991.svg?logo=openai&logoColor=white)](https://openai.com)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4-C51A4A.svg?logo=raspberrypi&logoColor=white)](https://raspberrypi.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<br>

**IVERI** is a voice-controlled AI assistant that runs on Raspberry Pi and Windows. Say "Jarvis" to activate, then control your system, get information, or have a conversation — all through voice.

<br>

[What It Does](#-what-iveri-does) • [Features](#-features-59-commands) • [Installation](#-installation) • [Skills Used](#-skills-demonstrated)

</div>

---

## 🎯 What IVERI Does

IVERI is a **voice assistant** that:

✅ **Listens** for wake word "Jarvis" (or keyboard trigger)  
✅ **Understands** voice commands using speech recognition  
✅ **Executes** 59 different commands (open apps, search, control system)  
✅ **Answers** questions using OpenAI's GPT-5-nano  
✅ **Speaks** responses using text-to-speech  
✅ **Remembers** things you tell it (persistent storage)  
✅ **Controls** GPIO LEDs on Raspberry Pi  

### What Makes It Different from Alexa/Google?

| Feature | Alexa/Google | IVERI |
|---------|--------------|-------|
| Opens local apps (Calculator, Notepad) | ❌ No | ✅ Yes |
| Controls system (volume, screenshot) | ❌ Limited | ✅ Yes |
| Opens any website you want | ❌ Limited | ✅ Yes |
| Works with Raspberry Pi GPIO | ❌ No | ✅ Yes |
| Open source / customizable | ❌ No | ✅ Yes |
| Free (no subscription) | ❌ No | ✅ Yes |

---

## 📊 Features (59 Commands)

### Actually Implemented & Tested ✅

| Category | Commands | What It Does |
|----------|----------|--------------|
| **Websites** | 12 | Opens YouTube, Google, Gmail, Netflix, Spotify, etc. |
| **Search** | 4 | Google search, YouTube search, Wikipedia |
| **Apps** | 5 | Opens Calculator, Notepad, Terminal, File Manager, Settings |
| **Folders** | 3 | Opens Downloads, Documents, Desktop folders |
| **Time/Date** | 3 | Tells current time, date, day |
| **Screenshot** | 1 | Takes screenshot, saves to Pictures |
| **Lock Screen** | 1 | Locks computer |
| **Volume** | 4 | Volume up/down, mute/unmute |
| **System Info** | 3 | IP address, battery status, CPU temp |
| **Memory** | 4 | Remember things, recall, forget, list |
| **Notes** | 3 | Add notes, show notes, clear notes |
| **Weather** | 1 | Gets weather for any city (needs API key) |
| **News** | 5 | General, tech, sports, business news (needs API key) |
| **LED Control** | 4 | LED on/off/blink (Raspberry Pi only) |
| **Chat** | 3 | Help, clear history, goodbye |
| **AI Chat** | ∞ | Any question → GPT-5-nano answers |

**Total: 59 specific commands + unlimited AI conversation**

---

## 🛠️ How It Works

```
┌─────────────────────────────────────────────────────────┐
│                     IVERI Assistant                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   You speak                                              │
│       ↓                                                  │
│   [Microphone] → [Wake Word: "Jarvis"] → [Listen]       │
│       ↓                                                  │
│   [Google Speech-to-Text] → Converts to text            │
│       ↓                                                  │
│   [Command Check] → Is it one of 59 commands?           │
│       ↓                                                  │
│   YES → Execute command (open app, search, etc.)        │
│   NO  → Send to GPT-5-nano for AI answer                │
│       ↓                                                  │
│   [Text-to-Speech] → IVERI speaks the response          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Actual Technology Used

| Component | Technology | Notes |
|-----------|------------|-------|
| Speech Recognition | Google Speech-to-Text API | Requires internet |
| Wake Word | Picovoice Porcupine | Works offline |
| AI Answers | OpenAI GPT-5-nano API | Requires internet + API key |
| Text-to-Speech | pyttsx3 (offline) | Works offline |
| Memory Storage | JSON files | Saved locally |
| LED Control | RPi.GPIO | Raspberry Pi only |

---

## 💼 Skills Demonstrated

*Skills used to build this project:*

| Skill | How It's Used |
|-------|---------------|
| **Python Programming** | All code is Python 3.8+ |
| **API Integration** | OpenAI, Google STT, Weather API, News API |
| **Speech Processing** | Speech recognition + text-to-speech |
| **Cross-Platform Dev** | Works on Windows + Linux (Raspberry Pi) |
| **Hardware Control** | GPIO for LED control on Pi |
| **Modular Design** | Separate modules for each function |
| **Error Handling** | Graceful fallbacks when services fail |
| **Linux/Systemd** | Auto-start service for Pi |
| **Git/GitHub** | Version control |

### Technology Stack

```
Language:     Python 3.8+
AI:           OpenAI GPT-5-nano
Speech:       Google Speech-to-Text, pyttsx3
Wake Word:    Picovoice Porcupine
Hardware:     Raspberry Pi 4, GPIO
APIs:         OpenAI, OpenWeatherMap, NewsAPI
```

---

## 🚀 Installation

### Windows

```bash
git clone https://github.com/Nishant-aiml/Iveri-AI-.git
cd Iveri-AI-
pip install -r requirements.txt
copy .env.example .env   # Add your API keys
python main.py
```

### Raspberry Pi

```bash
git clone https://github.com/Nishant-aiml/Iveri-AI-.git
cd Iveri-AI-
chmod +x setup_pi.sh && ./setup_pi.sh
nano .env   # Add your API keys
python3 main.py
```

### Bluetooth Headset (Optional)

```bash
./setup_bluetooth.sh
```

---

## 🔑 API Keys Needed

```env
OPENAI_API_KEY=sk-...          # Required - for AI answers
PICOVOICE_ACCESS_KEY=...       # Optional - for "Jarvis" wake word
WEATHER_API_KEY=...            # Optional - for weather feature
NEWS_API_KEY=...               # Optional - for news feature
```

| API | Cost | Get From |
|-----|------|----------|
| OpenAI | ~$0.001/request | [platform.openai.com](https://platform.openai.com) |
| Picovoice | Free | [console.picovoice.ai](https://console.picovoice.ai) |
| OpenWeatherMap | Free | [openweathermap.org](https://openweathermap.org/api) |
| NewsAPI | Free | [newsapi.org](https://newsapi.org) |

---

## 🎮 Usage

### Start IVERI
```bash
python main.py
```

### Choose Mode
- **Chat** - Type commands or press Enter to speak
- **Wake** - Say "Jarvis" to activate (needs Picovoice key)

### Example Commands
```
"What time is it?"              → Tells time
"Open YouTube"                  → Opens YouTube
"Search cats on YouTube"        → YouTube search
"Remember my name is John"      → Saves to memory
"What's my name?"               → Recalls from memory
"Take a screenshot"             → Captures screen
"Weather in London"             → Gets weather
"Volume up"                     → Increases volume
"Turn on LED"                   → Turns on LED (Pi only)
"Goodbye"                       → Exits
```

---

## 📁 Project Files

```
Iveri-AI-/
├── main.py              # Main program
├── speech.py            # Speech recognition
├── tts.py               # Text-to-speech
├── gpt.py               # OpenAI GPT-5-nano
├── wakeword.py          # "Jarvis" detection
├── commands.py          # 59 command handlers
├── memory.py            # Remember/recall
├── internet_tasks.py    # Weather, news
├── hardware.py          # LED control (Pi)
├── config.py            # Settings
├── requirements.txt     # Dependencies
├── setup_pi.sh          # Pi setup script
├── setup_bluetooth.sh   # Bluetooth setup
└── iveri.service        # Auto-start service
```

---

## ⚠️ Limitations (Honest)

- **Needs internet** for speech recognition and AI answers
- **Wake word** needs Picovoice API key
- **LED control** only works on Raspberry Pi
- **Weather/News** needs respective API keys
- **Speech recognition** can misunderstand in noisy environments

---

## 🧪 Testing

All 59 commands have been tested on Windows. Run tests:

```bash
python test_complete.py
```

---

## 📜 License

MIT License - Free to use and modify

---

## 👨‍💻 Author

**Nishant**

[![GitHub](https://img.shields.io/badge/GitHub-Nishant--aiml-181717?logo=github)](https://github.com/Nishant-aiml)

---

<div align="center">

⭐ Star if useful!

</div>
