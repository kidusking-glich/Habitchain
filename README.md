
# HabitChain API 🧠⛓️

**ADHD-friendly habit tracking backend with streaks, dependencies, and dynamic difficulty**

## 📌 Project Overview

HabitChain is a RESTful backend API built with **Django Rest Framework** that helps users build habits using:

* 🔥 **Daily streak tracking**
* 🔗 **Habit dependencies** (complete prerequisite habits first)
* 🎯 **Dynamic difficulty adjustment** based on user performance
* 🔐 **JWT authentication**
* 📊 **Swagger/OpenAPI documentation**

The system is designed to encourage consistency and prevent overload by adapting habit difficulty over time.

---

## 🚀 Features

### ✅ Authentication

* JWT-based authentication using **SimpleJWT**
* Secure access to all habit-related endpoints
* Login & token refresh endpoints

### ✅ Habit Management

* Create, update, delete, and list habits
* Filter, search, and order habits
* Habits are user-owned (multi-user safe)

### ✅ Habit Completion

* One completion per habit per day (idempotent)
* Completion enforces dependencies
* Automatically updates streaks and difficulty

### ✅ Habit Dependencies

* Define prerequisite habits (A → B)
* Prevents:

  * Self-dependency
  * Duplicate dependencies
  * Circular dependencies (A → B → A)

### ✅ Streak Tracking

* Tracks:

  * `current_streak`
  * `longest_streak`
  * `last_completed_date`
* Resets streak correctly when days are missed
* Per-user, per-habit streaks

### ✅ Dynamic Difficulty Algorithm

Difficulty adjusts automatically based on performance:

* ⬆️ **Increase difficulty**

  * 6–7 completions in the last 7 days
  * OR 7-day streak achieved
* ⬇️ **Decrease difficulty**

  * ≤2 completions in the last 7 days
  * OR missed more than 2 consecutive days
* Difficulty range: **1 (easy) → 5 (hard)**
* All changes are logged

### ✅ Difficulty Adjustment Logs

* Records:

  * Old difficulty
  * New difficulty
  * Reason
  * Timestamp
* Useful for transparency and analytics

---

## Installation

```bash
git clone [Habit Chain](https://github.com/kidusking-glich/Habitchain.git)
cd Habitchain
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver



## 🛠️ Tech Stack

* **Python 3**
* **Django 6**
* **Django Rest Framework**
* **MySQL**
* **JWT (SimpleJWT)**
* **drf-spectacular** (Swagger / OpenAPI)

---

## 📂 Project Structure

```
Habitchain/
├── core/
│   ├── models.py        # Habit, Streak, Dependency, Completion, Logs
│   ├── serializers.py   # DRF serializers with validation
│   ├── views.py         # ViewSets & API logic
│   ├── utils.py         # Streak & difficulty algorithms
│   ├── urls.py          # API routes
│   └── migrations/
├── Habitchain/
│   ├── settings.py
│   ├── urls.py
├── manage.py
└── README.md
```

---

## 🔐 Authentication Flow

1. **Login**

   ```
   POST /auth/login/
   ```

   Returns access & refresh tokens.

2. **Authorize in Swagger**

   ```
   Authorization: Bearer <access_token>
   ```

All `/api/` endpoints require authentication.

---

## 🔄 Core API Endpoints

### Habits

```
GET    /api/habits/
POST   /api/habits/
GET    /api/habits/{id}/
PUT    /api/habits/{id}/
DELETE /api/habits/{id}/
```

### Complete Habit

```
POST /api/habits/{id}/complete/
```

### Streak

```
GET /api/habits/{id}/streak/
```

### Habit Dependencies

```
POST /api/dependencies/
GET  /api/dependencies/
```

### Swagger Docs

```
GET /api/docs/
```

---

## 🧮 Dynamic Difficulty Logic (Summary)

```text
If completions ≥ 6 in last 7 days → difficulty +1
If completions ≤ 2 in last 7 days → difficulty -1
If 7-day streak achieved → difficulty +1
If missed >2 days → difficulty -1
```

All changes are capped between **1 and 5** and logged.

---

## 🧪 Database & Migrations

* All models are fully migrated
* Streak table includes:

  * `current_streak`
  * `longest_streak`
  * `last_completed_date`
* No pending migrations

Run if needed:

```bash
python manage.py migrate
```

---

## ▶️ Running the Project

```bash
python manage.py runserver
```

Access:

* API: `http://127.0.0.1:8000/api/`
* Swagger: `http://127.0.0.1:8000/api/docs/#`

---


## 👤 Author

**Abel**
ALX Software Engineering Program
Backend Specialization

