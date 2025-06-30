# 📘 EduTutor AI (Streamlit Demo)

EduTutor AI is an interactive, AI-assisted learning platform designed to provide personalized quizzes and performance tracking for students and teachers. This is a demo version built using **Streamlit**, **Google Classroom API**, and **SQLite** for local quiz history storage.

---

## 🌟 Features

- 🔐 **Google Login** with optional anonymous access
- 🎓 **Role Selection**: Choose between Student or Teacher
- 🏫 **Google Classroom Integration**: View your enrolled courses
- 🧠 **AI Quiz Engine** (Static logic in demo)
- 📜 **Quiz History**: Stores attempts locally with timestamps
- 🧪 **Self-contained**: No external database required

---

## 📦 Tech Stack

| Layer     | Technology            |
|-----------|------------------------|
| UI        | [Streamlit](https://streamlit.io) |
| Auth      | Google OAuth 2.0      |
| DB        | SQLite (local file `quiz.db`) |
| API       | Google Classroom API  |
| AI Logic  | Static logic (replaceable with OpenAI/Watsonx) |

---

## 🔧 Setup Instructions

### 1. 🔑 Google API Setup
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project
- Enable **Google Classroom API**
- Configure OAuth 2.0 client:
  - App type: **Desktop**
  - Download `client_secret.json` to your project folder

### 2. ⚙️ Install Requirements

```bash
pip install streamlit google-auth google-auth-oauthlib google-api-python-client openai

```
### 3. ▶️ Run the App
```bash

streamlit run app.py
```

## 🗃️ Folder Structure
```
.
├── app.py                # Main Streamlit app
├── client_secret.json    # Google OAuth credentials
├── quiz.db               # SQLite database for history
├── README.md             # Project documentation
```


## 👨‍💻 Author
Made with ❤️ for educational purposes by **Syam Doppasani**
