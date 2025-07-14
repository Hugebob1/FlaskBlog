# FlaskBlog

A simple, modular Flask application featuring a PostgreSQL-backed blog, user authentication, rich text editing, comments, contact form, and responsive design. Hosted on Render with a free-tier PostgreSQL database.

Live demo: https://flaskblog-7b2d.onrender.com (cold start up to 50 s)

---

## Features

- **User accounts & authentication**  
  - Registration & login via Flask-Login  
  - Passwords securely hashed  
  - “Admin” role (first registered user) can edit or delete any post  
- **Blog posts**  
  - CRUD operations on posts (title, subtitle, date, body, image URL)  
  - Rich-text editor powered by CKEditor  
- **Comments**  
  - Authenticated users can comment on posts  
  - Nested relationships between users, posts, and comments  
- **About & Contact**  
  - “About” page with personal bio  
  - Contact form (Flask-WTF) that sends confirmation to the visitor and forwards details by email  
- **Responsive design**  
  - Bootstrap-powered layouts that adapt to mobiles, tablets, and desktop  
- **Modular structure**  
  - `mail_utils.py` – email sending  
  - `forms.py`      – Flask-WTF form definitions  
  - `app.py`        – application setup & route handlers  
- **Hosting & database**  
  - Deployed on [Render](https://render.com)  
  - Global PostgreSQL database (Render free tier)  
  - Environment variables for configuration and secrets

---

## 🔧 Getting Started

### 1. Clone & install

```bash
git clone https://github.com/yourusername/flaskblog.git
cd flaskblog
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

 ## .env FILE STRUCTURE
FLASK_KEY=your-secret-flask-key
DATABASE_URL=postgresql://username:password@host:port/dbname
MY_EMAIL=your-email@example.com
EMAIL_PASS=your-email-password //from google application not your real email pass.
