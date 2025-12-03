# SlideSummarizer AI 🚀

A full-stack application that automatically analyzes PowerPoint presentations and generates high‑quality slide‑by‑slide summaries using **Google Gemini AI**.

This project was built as a production‑ready system including:
- A **React frontend**
- A **Flask backend API**
- An **async AI micro‑service** (explainer)
- A **SQLAlchemy database layer**
- Full deployment to **Render.com** (frontend, backend & worker)

---

## 🌐 Live Demo

You can try the deployed version here:  
👉 **https://slidesummarizer-frontend.onrender.com/**

---

## 🧠 What the App Does

Upload a `.pptx` file → choose summary style → get slide explanations generated automatically.

Supported summary modes:
- **Beginner** – simple and educational  
- **Comprehensive** – detailed and deep  
- **Executive Brief** – short, sharp, 2–3 sentence summaries  

Supported languages:
- English 🇬🇧  
- Hebrew 🇮🇱  
- Russian 🇷🇺  
- Spanish 🇪🇸  

---

## 🏗️ System Architecture

```
Frontend (React)
      |
      v
Backend API (Flask)
      |
      v
Database (SQLAlchemy + SQLite/Postgres)
      |
      v
AI Explainer Service (Async Worker)
      |
      v
Google Gemini API (Slide Summaries)
```

---

## 📂 Project Structure

```
SlideSummarizer-AI/
│── backend/
│   ├── api/
│   │   └── app.py
│   ├── explainer/
│   │   └── explainer_service.py
│   ├── database.py
│   └── shared/
│       ├── uploads/
│       ├── outputs/
│       └── logs/
│
│── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
│── README.md
```

---

## ⚙️ Technologies Used

### **Frontend**
- React
- Fetch API for backend communication
- Responsive UI/UX flow

### **Backend**
- Python + Flask  
- SQLAlchemy ORM  
- Email validation  
- CORS support  
- File management (uploads & outputs)

### **AI Service**
- Asynchronous Gemini model calls  
- Batch processing  
- PPTX parsing using `python-pptx`

### **Deployment**
- Render.com (Web Service + Background Worker)  
- Environment variables  
- Auto-builds from GitHub  

---

## 🚀 How to Run Locally

### 1. Clone the project
```bash
git clone https://github.com/Yuval2306/SlideSummarizer-AI.git
cd SlideSummarizer-AI
```

### 2. Backend setup
```bash
cd backend
pip install -r requirements.txt
python api/app.py
```

### 3. Frontend setup
```bash
cd frontend
npm install
npm start
```

Open:  
👉 http://localhost:3000

---

## 🔑 Environment Variables

### Backend
```
GEMINI_API_KEY=your_key_here
UPLOADS_DIR=shared/uploads
OUTPUTS_DIR=shared/outputs
LOGS_DIR=shared/logs
```

### Frontend
```
REACT_APP_API_URL=https://your-backend.onrender.com
```
---

## 🙌 Author

**Yuval Boker**
Full‑Stack & Software Developer
---
