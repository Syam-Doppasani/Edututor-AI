import streamlit as st
import sqlite3
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime
import openai

# ========== CONFIG ========== #
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'openid', 'email', 'profile'
]

st.set_page_config(page_title="EduTutor AI", layout="centered")

# ========== SESSION STATE INIT ========== #
def init_session():
    defaults = {
        'page': 'login',
        'credentials': None,
        'user_email': '',
        'user_name': '',
        'user_id': '',
        'role': '',
        'quiz_subject': '',
        'quiz_questions': [],
        'current_question': 0,
        'quiz_score': 0
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
init_session()

# ========== DB SETUP ========== #
conn = sqlite3.connect("quiz.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        subject TEXT,
        question TEXT,
        selected_option TEXT,
        correct_option TEXT,
        is_correct INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# ========== LOGIN PAGE ========== #
def login_page():
    st.title("📖🔐 EduTutor AI Login")
    role = st.selectbox("Select Role", ["student", "teacher"])
    user_id = st.text_input("Enter User ID")

    if st.button("Continue without Google", key="continue_without_google"):
        st.session_state['role'] = role
        st.session_state['user_id'] = user_id or "guest"
        st.session_state.page = 'dashboard'

    st.markdown("### Or")

    def get_auth_url():
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=SCOPES,
            redirect_uri='http://localhost:8501/'
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.session_state['flow'] = flow
        return auth_url

    if st.button("Login with Google", key="login_google"):
        auth_url = get_auth_url()
        st.markdown(f"[Click here to login with Google]({auth_url})")

    code = st.query_params.get("code")
    if code and 'flow' in st.session_state:
        try:
            flow = st.session_state['flow']
            flow.fetch_token(code=code)
            credentials = flow.credentials
            st.session_state['credentials'] = credentials

            user_info_service = build('oauth2', 'v2', credentials=credentials)
            user_info = user_info_service.userinfo().get().execute()

            st.session_state['user_name'] = user_info.get('name', '')
            st.session_state['user_email'] = user_info.get('email', '')
            st.session_state['user_id'] = st.session_state['user_email']
            st.session_state['role'] = 'student'
            st.session_state.page = 'dashboard'
        except Exception as e:
            st.error(f"Google login failed: {e}")

# ========== QUIZ HISTORY ========== #
def show_quiz_history():
    st.markdown("### 📜 Quiz History")
    user_id = st.session_state.get('user_id', '')
    cursor.execute("SELECT subject, question, selected_option, correct_option, is_correct, timestamp FROM quiz_history WHERE user_id=? ORDER BY timestamp DESC LIMIT 10", (user_id,))
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            subject, q, selected, correct, is_correct, ts = row
            st.write(f"**[{subject}]** {q}")
            st.write(f"📝 Your answer: `{selected}` | ✅ Correct: `{correct}` | {'🟢 Correct' if is_correct else '🔴 Wrong'}")
            st.caption(f"🕒 {ts}")
            st.markdown("---")
    else:
        st.info("No quiz history yet.")

# ========== DASHBOARD ========== #
def dashboard():
    st.title("📚 EduTutor AI Dashboard")
    if st.session_state.get('user_name'):
        st.success(f"Welcome, {st.session_state['user_name']} ({st.session_state['user_email']})")
    else:
        st.success(f"Logged in as {st.session_state['role']} - ID: {st.session_state['user_id']}")

    st.markdown("---")

    if st.session_state.get('credentials'):
        st.subheader("Your Google Classroom Courses")
        creds = st.session_state['credentials']
        classroom_service = build('classroom', 'v1', credentials=creds)
        results = classroom_service.courses().list().execute()
        courses = results.get('courses', [])
        if courses:
            for course in courses:
                st.write(f"📘 {course['name']}")
        else:
            st.info("No courses found.")
    else:
        st.info("Sync with Google to see your classroom courses.")

    st.markdown("---")
    if st.button("Take a Quiz ✏️", key="go_to_quiz"):
        st.session_state.page = 'quiz'
        st.rerun()

    show_quiz_history()

# ========== QUIZ PAGE ========== #
def quiz_page():
    st.title("📝 AI Quiz")

    subject = st.selectbox("Choose Subject", ["Math", "Science", "English"])

    if st.button("Generate Questions with AI", key="generate_ai_questions"):
        st.session_state.quiz_subject = subject
        st.session_state.quiz_questions = [
            {"question": f"What is {i}+{i}?", "options": [str(i+1), str(i+2), str(i+i), str(i*2)], "answer": str(i+i)}
            for i in range(1, 4)
        ]
        st.session_state.current_question = 0
        st.session_state.quiz_score = 0
        st.rerun()

    if st.session_state.quiz_questions:
        i = st.session_state.current_question
        q = st.session_state.quiz_questions[i]
        st.subheader(f"Q{i+1}: {q['question']}")
        selected = st.radio("Select an answer:", q['options'], key=f"quiz_q{i}")
        if st.button("Submit Answer", key=f"submit_q{i}"):
            correct = q['answer']
            is_correct = int(selected == correct)

            cursor.execute('''
                INSERT INTO quiz_history (user_id, subject, question, selected_option, correct_option, is_correct)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                st.session_state.get('user_id', 'guest'),
                st.session_state.get('quiz_subject', 'General'),
                q['question'], selected, correct, is_correct
            ))
            conn.commit()

            if is_correct:
                st.session_state.quiz_score += 1

            if i + 1 < len(st.session_state.quiz_questions):
                st.session_state.current_question += 1
                st.rerun()
            else:
                st.success("🎉 Quiz Completed!")
                total = len(st.session_state.quiz_questions)
                score = st.session_state.quiz_score
                st.info(f"✅ Your Score: {score}/{total}")

                # Show quiz history
                show_quiz_history()

                # Clear for next round
                st.session_state.quiz_questions = []
                st.session_state.quiz_score = 0

                if st.button("Back to Dashboard", key="end_back_dashboard"):
                    st.session_state.page = 'dashboard'
                    st.rerun()
    else:
        if st.button("Back to Dashboard", key="noquiz_back_dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()

# ========== ROUTER ========== #
if st.session_state.page == 'login':
    login_page()
elif st.session_state.page == 'dashboard':
    dashboard()
elif st.session_state.page == 'quiz':
    quiz_page()
