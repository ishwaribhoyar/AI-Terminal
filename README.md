<div align="center">

# 🤖 IVERI AI Assistant

### Your Personal Voice-Controlled AI Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5--nano-412991.svg)](https://openai.com)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4-C51A4A.svg)](https://raspberrypi.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**IVERI** is a sophisticated voice-controlled AI assistant that runs on both Windows and Raspberry Pi. Powered by OpenAI's GPT-5-nano, it offers 59+ features including voice commands, smart home control, web automation, and natural conversation.

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [API Reference](#-api-reference)

</div>

---

## ✨ Highlights

- 🎤 **Voice-Activated** — Say "Jarvis" to wake, hands-free operation
- 🧠 **AI-Powered** — Natural conversations with GPT-5-nano
- 🌐 **59+ Commands** — Web, apps, system control, smart home
- 🔊 **Text-to-Speech** — Natural voice responses
- 💾 **Persistent Memory** — Remembers your preferences
- 🏠 **IoT Ready** — GPIO control for Raspberry Pi
- 🔒 **Privacy-First** — All processing on your device
- ⚡ **Cross-Platform** — Windows + Raspberry Pi Linux

---

## 🎯 Features

<table>
<tr>
<td width="50%">

### 🌐 Web & Search
- Open 12+ websites (YouTube, Google, Netflix...)
- Google & YouTube search
- Wikipedia lookup

### 💻 Applications
- Calculator, Notepad, Terminal
- File Manager, Settings
- Custom app launching

### 📂 File Management
- Open Downloads, Documents, Desktop
- Take screenshots
- Lock screen

</td>
<td width="50%">

### 🎛️ System Control
- Volume up/down/mute
- Battery status
- IP address & CPU temp

### 🧠 AI & Memory
- Natural conversation (GPT-5-nano)
- Remember/recall information
- Persistent notes

### 🌤️ Internet Services
- Real-time weather
- News headlines (Tech, Sports, Business)
- Web automation

</td>
</tr>
</table>

### 🏠 Raspberry Pi Exclusive
- **GPIO LED Control** — On/Off/Blink
- **Wake Word Detection** — "Jarvis" activation
- **Auto-start on Boot** — Systemd service
- **Bluetooth Audio** — Wireless headset support

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Microphone & Speaker
- API Keys (OpenAI required, others optional)

### Windows (Quick Start)

```bash
# Clone repository
git clone https://github.com/yourusername/iveri-ai.git
cd iveri-ai

# Install dependencies
pip install -r requirements.txt

# Configure API keys
copy .env.example .env
# Edit .env with your keys

# Run IVERI
python main.py
```

### Raspberry Pi (One-Command Setup)

```bash
# Clone repository
git clone https://github.com/yourusername/iveri-ai.git
cd iveri-ai

# Run automated setup (installs everything!)
chmod +x setup_pi.sh
./setup_pi.sh

# Configure API keys
nano .env

# Run IVERI
python3 main.py
```

### Bluetooth Headset (Optional)

```bash
# Pair your Bluetooth headset
./setup_bluetooth.sh
```

---

## 🎮 Usage

### Interaction Modes

| Mode | Activation | Description |
|------|------------|-------------|
| **Chat** | Type or press Enter | Text-based with optional voice input |
| **Wake** | Say "Jarvis" | Full voice control |

### Voice Commands

```
🗣️ "Jarvis"                    → Activates IVERI
🗣️ "What time is it?"          → Returns current time
🗣️ "Open YouTube"              → Opens YouTube in browser
🗣️ "Search cats on YouTube"    → Searches YouTube
🗣️ "Take a screenshot"         → Captures screen
🗣️ "Remember my name is John"  → Saves to memory
🗣️ "What's my name?"           → Recalls from memory
🗣️ "Weather in London"         → Gets weather info
🗣️ "Tech news"                 → Latest tech headlines
🗣️ "Volume up"                 → Increases volume
🗣️ "Goodbye"                   → Exits IVERI
```

### Example Conversation

```
You: Jarvis
IVERI: Yes?

You: What's the weather in New York?
IVERI: The weather in New York is partly cloudy with a temperature 
       of 12°C, feels like 10°C. Humidity is at 65%.

You: Remember my favorite city is New York
IVERI: I'll remember that your favorite city is New York.

You: Open YouTube and search for coding tutorials
IVERI: Searching YouTube for coding tutorials.
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      IVERI AI Assistant                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │  Speech  │───▶│   Main   │───▶│   TTS    │               │
│  │ (Input)  │    │ (Router) │    │ (Output) │               │
│  └──────────┘    └────┬─────┘    └──────────┘               │
│                       │                                      │
│         ┌─────────────┼─────────────┐                       │
│         ▼             ▼             ▼                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ Commands │  │  Memory  │  │   GPT    │                   │
│  │ (Local)  │  │(Storage) │  │ (AI)     │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
│         │             │             │                       │
│         ▼             ▼             ▼                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ Internet │  │ Hardware │  │  Config  │                   │
│  │ (APIs)   │  │  (GPIO)  │  │(Settings)│                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Module Overview

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `main.py` | Entry point, mode routing | `chat_mode()`, `wake_mode()` |
| `speech.py` | Speech recognition | `listen()` |
| `tts.py` | Text-to-speech | `speak()`, `stop()` |
| `gpt.py` | OpenAI integration | `get_response()` |
| `commands.py` | Local command handling | `handle_command()` |
| `memory.py` | Persistent storage | `remember()`, `recall()` |
| `internet_tasks.py` | Weather, News APIs | `get_weather()`, `get_news()` |
| `hardware.py` | GPIO control (Pi) | `led_on()`, `led_off()` |
| `wakeword.py` | Wake word detection | `wait_for_wake_word()` |
| `config.py` | Configuration | API keys, settings |

---

## 🔑 API Reference

### Required API Keys

| Service | Required | Free Tier | Get Key |
|---------|----------|-----------|---------|
| OpenAI | ✅ Yes | Pay-as-you-go | [platform.openai.com](https://platform.openai.com) |
| Picovoice | Optional | ✅ Free | [console.picovoice.ai](https://console.picovoice.ai) |
| OpenWeatherMap | Optional | ✅ Free | [openweathermap.org](https://openweathermap.org/api) |
| NewsAPI | Optional | ✅ Free | [newsapi.org](https://newsapi.org) |

### Environment Configuration

```env
# .env file
OPENAI_API_KEY=sk-your-openai-key
PICOVOICE_ACCESS_KEY=your-picovoice-key
WEATHER_API_KEY=your-openweathermap-key
NEWS_API_KEY=your-newsapi-key
```

---

## 🔧 Hardware Setup (Raspberry Pi)

### Minimum Requirements
- Raspberry Pi 4 (2GB+ RAM)
- USB Microphone or Bluetooth Headset
- Speaker (3.5mm, USB, or Bluetooth)
- MicroSD Card (16GB+)

### Wiring Diagram (LED Control)

```
GPIO 17 (Pin 11) ──┬── 330Ω Resistor ──── LED (+)
                   │
GND (Pin 6) ───────┴───────────────────── LED (-)
```

### Audio Options

| Option | Pros | Cons |
|--------|------|------|
| USB Mic + 3.5mm Speaker | Easy setup | Wired |
| USB Sound Card | Better quality | Extra hardware |
| Bluetooth Headset | Wireless, portable | Battery needed |
| ReSpeaker HAT | Best quality, array mic | $10-15 |

---

## 📁 Project Structure

```
iveri-ai/
├── main.py              # Entry point
├── speech.py            # Speech recognition
├── tts.py               # Text-to-speech
├── gpt.py               # OpenAI GPT-5-nano
├── commands.py          # 30+ local commands
├── memory.py            # Persistent storage
├── internet_tasks.py    # Weather, News APIs
├── hardware.py          # GPIO control
├── wakeword.py          # Jarvis detection
├── config.py            # Settings
├── requirements.txt     # Python dependencies
├── setup_pi.sh          # Pi auto-setup script
├── setup_bluetooth.sh   # Bluetooth pairing
├── iveri.service        # Systemd service
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── data/                # Persistent data
│   └── memory.json      # User memories
└── models/              # Custom wake words
```

---

## 🚀 Deployment

### Auto-Start on Boot (Raspberry Pi)

```bash
# Enable service
sudo systemctl enable iveri
sudo systemctl start iveri

# Check status
sudo systemctl status iveri

# View logs
journalctl -u iveri -f
```

### Docker (Coming Soon)

```dockerfile
# Future: Docker support planned
docker run -d --name iveri \
  -e OPENAI_API_KEY=your-key \
  --device /dev/snd \
  iveri-ai:latest
```

---

## 🧪 Testing

```bash
# Run all feature tests
python test_complete.py

# Quick feature check
python test_quick.py

# System diagnostics
python test_system.py
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [OpenAI](https://openai.com) for GPT-5-nano
- [Picovoice](https://picovoice.ai) for wake word detection
- [Google](https://cloud.google.com/speech-to-text) for speech recognition
- Raspberry Pi Foundation

---

<div align="center">

**Made with ❤️ for the AI community**

⭐ Star this repo if you found it helpful!

</div>
