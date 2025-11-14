#  Student Lend Note

**Student Lend Note** is a lightweight web application that connects student borrowers and lenders. It supports **in-person lending** (no shipping needed), **clear due-date tracking**, and a simple **reputation rating** system that helps students build trust within their community.

This platform reduces wasted time, lowers costs for students needing textbooks or resources, and helps create a student-led sharing community.

Developed for the **203 Assessment at Yoobee Colleges** by **Joan Allysen** and **Jason William**, facilitated by **Sagar Dake**.

---

## ✨ Features

- 📘 Borrow and lend books/resources  
- 🗓️ Due-date and loan status tracking  
- ⭐ Reputation rating to build student trust  
- 📝 Notes creation and management  
- 🤖 Related notes algorithm powered by Sentence Transformers  
- 📱 Clean and student-friendly UI  

---

## 🚀 Getting Started

### **1. Clone the Repository**
```bash
git clone https://github.com/joanallysen/Lend-Student-Note.git
cd Lend-Student-Note
```

### **2. Create a Virtual Environment (Recommended)**
Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### **3. Run the Application**
```bash
python app.py
```

The app will run at: http://127.0.0.1:5000

## ⚠️ Important Note
The first run may take longer because Sentence Transformers needs to load its model.

## 🛠️ Troubleshooting
Update pip if installation fails:

```bash
pip install --upgrade pip
```
Ensure Python 3.10+ is installed and the correct interpreter is selected (especially in VS Code).
