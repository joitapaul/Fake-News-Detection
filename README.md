# 🕵️‍♂️ Fake News Verifier

**AI-Powered Indian News Fact Checker**
_Fighting misinformation with intelligence, empathy, and style._

![Banner](https://img.shields.io/badge/AI%20Fake%20News%20Verifier-%F0%9F%94%8D-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?style=for-the-badge&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

---

## 🌐 Overview

> “Truth needs no army — just the courage to verify it.”

**Fake News Verifier** is an AI-driven web application built using **Streamlit** and **Google Gemini AI**, designed to detect and analyze  the fake or misleading news in the **Indian context**.  
It intelligently evaluates news articles, gives **verification confidence**, and recommends **trusted Indian sources** for cross-checking.

---

## ✨ Features

✅ **Real-Time Fake News Detection**  
✅ **AI-Powered Indian Context Analysis**  
✅ **Confidence Scoring & Reasoning**  
✅ **Auto-Extraction from News URLs**  
✅ **Elegant Human-Centric UI** (warm theme, soft gradients, and handcrafted details)  
✅ **Downloadable AI Reports in JSON Format**  
✅ **Cross-Verification with Trusted Indian News Sources**

---

## 🧠 Powered By

- [Google Gemini AI](https://ai.google.dev/) – Advanced content reasoning model  
- [Streamlit](https://streamlit.io/) – Rapid UI development framework  
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) – For scraping and parsing article content  
- [Python Dotenv](https://pypi.org/project/python-dotenv/) – Secure environment management  

---

## 🏗️ Project Structure

```text
📂 Fake-News-Verifier/
│
├── main_beautiful.py          # Main Streamlit app
├── run_bg.py                  # Launch script with background image
├── test_ai.py                 # AI connection tester
│
├── .env                       # API keys (ignored in Git)
├── .gitignore                 # Prevents sensitive data from being committed
├── requirements.txt           # Project dependencies
│
└── assets/
    └── transparent_bg_sample.svg

```


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/DebasmitaBose0/Fake-News-Detection.git
cd "Fake News final" || cd Fake-News-Detection || cd Fake-News-Verifier
```

### 2️⃣ Install Dependencies
pip install -r requirements.txt

### 3️⃣ Add Your API Key
Create a `.env` file in the project root (the repository already contains a `.gitignore` that excludes `.env`) and add your API key:
```text
GEMINI_API_KEY=your_api_key_here
```

### 4️⃣ Run the App
There are two easy ways to run the app locally.

Option A — use the included launcher (recommended):
```bash
python run_bg.py
```

Option B — run Streamlit directly:
```bash
python -m streamlit run main_beautiful.py
```

Then open your browser and navigate to:
👉 http://localhost:8501 (or the URL shown in the terminal)

---

## 🧪 Testing the AI Engine
Before launching the UI, test your Gemini API connection:

```bash
python test_ai.py
```

If everything is configured correctly you should see a short confirmation and a sample response from the Generative API.

---

## 📰 Trusted Sources
The AI cross-checks claims with reliable Indian news outlets:
🟢 Anandabazar Patrika
🟢 The Telegraph
🟢 The Statesman
🟢 Times of India
🟢 NDTV
🟢 The Hindu
🟢 Indian Express

---

## 🔍 Alt News (Fact Checker)

🔍 Boom Live

🔍 The Quint WebQoof

---

## 🎨 UI Theme Preview

Warm, handcrafted, and inviting.
Inspired by paper textures and human-like design to make AI feel trustworthy and organic.

Light ThemeSidebar PanelVerdict Section

⚡ Example
Input:

“PM Modi announced that petrol will now be free for all Indian citizens.”

Output:
VERIFICATION_STATUS: FALSE
CONFIDENCE_SCORE: 92
DETAILED_ANALYSIS: No credible sources reported this claim...

---

👩‍💻 Contributors

- Debasmita Bose — Lead Developer & Designer 🎨
- Manisha Debnath — Co-Developer & Research Analyst 📊
- Joita Paul — Data & Testing Specialist 🧪

---

## 🧩 Future Enhancements
🚀 Real-time social media verification
🧠 Multilingual news analysis (Hindi, Bengali, etc.)
📱 Mobile-optimized interface
📊 Integration with live Indian news APIs

---

## ⚖️ License
This project is licensed under the MIT License (see `LICENSE`).
Debasmita Bose © 2025

---

## 💬 Closing Note

“Fake news dies when truth becomes easier to verify.”
Stay smart, stay skeptical, and let AI help you find the truth.

---


