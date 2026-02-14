# 🏭 Industrial Gauge Digitizer Pro

> **A "Human-in-the-Loop" Computer Vision application that digitizes analog industrial gauges using Groq LPU and Meta Llama 4 Vision.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎥 Project Overview
Millions of industrial machines are "offline" because retrofitting them with digital sensors is expensive and invasive. This project bridges that gap using software.

**Key Features:**
- **Real-time Telemetry:** Extracts gauge readings in <500ms using Groq's LPU.
- **Multimodal Reasoning:** Detects "Red Zone" danger levels and gauge condition (e.g., cracked glass, rust).
- **Human-in-the-loop:** A staging area for operator verification before database commit.
- **Digital Historian:** Auto-generates CSV shift reports for compliance auditing.

## 🛠️ Tech Stack
- **Inference Engine:** [Groq API](https://groq.com)
- **Vision Models:** - Primary: **Meta Llama 4 Scout (17B)** for spatial reasoning.
  - Fallback: **Llama 3.2 Vision (90B)** for high-availability reliability.
- **Frontend:** Streamlit (Python)
- **Data Handling:** Pandas & Session State
- **Input:** Webcam or File Upload

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/Durgaprasadpenumuru/industrial-gauge-digitizer.git
cd industrial-gauge-digitizer
```
### 2.Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Create a .env file in the root directory and add your Groq API key
```bash
GROQ_API_KEY=gsk_your_actual_api_key_here
```
### 4. Run the pipeline
```bash
streamlit run app.py
```
👨‍💻 Author
Durga Prasad

