# EduInsight AI - AI-Powered Student Result & Analytics Portal

EduInsight AI is a modern, responsive web application built with Django that empowers educators, administrators, and students with student result tracking and analytics. Using a machine learning pipeline (scikit-learn Random Forest model), it predicts final grades and student pass/fail risk status in real-time based on study hours, attendance, assignments, and mid-term marks.

### 🌐 Live Deployment
The application is deployed on Vercel and can be accessed live at:
👉 **[https://edu-insight-ai-six.vercel.app/](https://edu-insight-ai-six.vercel.app/)**

---

## 🚀 Features

- **Role-Based Portals**:
  - **Admin Portal**: Check system activity, DB registration metrics, and manage user roles.
  - **Teacher Portal**: Batch upload student results via CSV/Excel, add/edit records manually, and analyze class performance distribution.
  - **Student Portal**: View transcripts, monitor a personal performance curve, check custom AI grade/failure risk recommendations, and download report cards.
- **Interactive Dashboards**: Dynamic charts powered by **Chart.js** displaying pass/fail ratios and average subject performance.
- **Batch CSV/Excel Uploads**: Automated parsing of student marks using **Pandas** with a smart name parser for generating student profiles automatically.
- **AI-Powered Grade Prediction**: An integrated Random Forest classifier model predicting student grades and status with 75% accuracy.
- **PDF Report Generation**: Downloadable academic report cards styled dynamically using **ReportLab**.
- **REST APIs**: Full JSON endpoints powered by Django REST Framework (DRF) for integration.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Pip package manager

### 1. Clone & Navigate to Project Root
```bash
git clone https://github.com/SakshiBodke01/EduInsight-AI.git
cd EduInsight-AI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Migration & Seeding
Create tables, train the machine learning model, and seed default test users (along with mock Marathi students):
```bash
python seed_data.py
```

### 4. Run the Development Server
```bash
python manage.py runserver
```
Visit the portal locally at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 🔑 Default Accounts (Seeded)

| Role | Username | Password | Purpose & View Access |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | System stats, database metrics overview, direct admin panel link. |
| **Teacher** | `teacher` | `teacher123` | Upload student grade CSVs, add/edit single results, view class-wide performance graphs. |
| **Student (Default)** | `student` | `student123` | View transcript grades (assigned to **Rohan Deshmukh**), check personal performance curve, review AI recommendations, and download PDF. |

### Seeded Mock Student Logins 
- **Snehal Patil**: `snehal_patil` / `snehal_patil123`
- **Aditya Joshi**: `aditya_joshi` / `aditya_joshi123`
- **Aniket Kulkarni**: `aniket_kulkarni` / `aniket_kulkarni123`

---

## 📁 Project Structure

```
EduInsight-AI/
│
├── api/                  # REST API views, URLs, and serializers (DRF)
├── ml_model/             # Random Forest training script and serialized model (.joblib)
├── portal/               # Core Django app (models, forms, signals, and views)
│   ├── utils/            # ML engine wrapper and ReportLab PDF generator
│   └── decorators.py     # Role-based decorators (@admin_required, etc.)
├── static/               # CSS styles, JS assets, and sample CSV templates
├── templates/            # HTML templates organized by dashboard roles
├── manage.py             # Django management entrypoint
├── requirements.txt      # List of dependencies
└── seed_data.py          # Script to run migrations, train model, and seed data
```

---

## 📡 API Endpoints

- **Results Endpoint**: [http://127.0.0.1:8000/api/results/](http://127.0.0.1:8000/api/results/) (CRUD actions on individual subjects)
- **Analytics Endpoint**: [http://127.0.0.1:8000/api/analytics/](http://127.0.0.1:8000/api/analytics/) (Summary distributions, passing rates, and class averages)
