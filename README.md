# 🤖 AI Code Review Assistant

An AI-powered web application that reviews source code using Google's Gemini API. Users can paste code snippets, select the programming language, and receive AI-generated feedback including bug detection, optimizations, best practices, and suggestions.

---

## 🚀 Features

- 🔍 AI-powered code review
- 🐞 Detects potential bugs
- ⚡ Suggests optimizations
- 🧹 Recommends best practices
- 💡 Provides improvement suggestions
- 🌐 Simple and responsive web interface
- 🤖 Powered by Google Gemini

---

## 🛠️ Tech Stack

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- FastAPI
- Python

### AI

- Google Gemini API

---

## 📁 Project Structure

```
AI-Code-Review-Assistant/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env (not included)
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── robot image/
│
└── .gitignore
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/aarzoooooo/AI-Code-Review-Assistant.git
```

Move into the project:

```bash
cd AI-Code-Review-Assistant
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Create a `.env` file inside the `backend` folder:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

Run the backend:

```bash
cd backend
uvicorn main:app --reload
```

Open the frontend (`frontend/index.html`) using Live Server or any local web server.

---

## 📸 Demo

_(Add screenshots or the deployed website link here after deployment.)_

---

## 👩‍💻 Author

**Aarzoo Nuha**

GitHub: https://github.com/aarzoooooo
