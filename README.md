# Cybersecurity Learning Lab

> A local web application for learning offensive and defensive cybersecurity through guided labs, CTF-style challenges, and team-oriented content.

## What this project does

Cybersecurity Learning Lab is a Flask-based training portal. Learners log in, access Red Team, Blue Team, and Purple Team material, participate in CTF challenges, publish blog posts, manage profiles, and exchange public or approved private chat messages.

The project includes deliberately vulnerable exercises for hands-on learning:

- **SQL Injection lab** for understanding unsafe query construction.
- **XSS lab** for studying unsafe HTML rendering.
- **IDOR-style CTF challenge** in the simulated Alif Finance area.

## Architecture

```text
Browser
  │
  ▼
Flask application (app.py)
  ├── Authentication and role checks
  ├── Learning labs and CTF routes
  ├── Blog, profile, and chat APIs
  └── Jinja HTML templates + static CSS/JavaScript
  │
  ▼
SQLite database (created by init_db.py)
  ├── users
  ├── blogs
  ├── chat_messages
  └── chat_requests
```

## Key capabilities

| Area | Function |
| --- | --- |
| Authentication | Session-based login and participant/admin role checks |
| Learning | Red, Blue, and Purple Team learning pages |
| Hands-on labs | Controlled SQLi, XSS, and IDOR-style exercises |
| CTF | Challenge interface with points-oriented participant data |
| Collaboration | Blog publishing plus public and approved private chats |
| Profiles | Learner profile editing and profile-image uploads |

## Technology

- Python and Flask
- SQLite
- Jinja templates, HTML, CSS, and JavaScript
- Werkzeug password hashing and secure filename handling

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install flask werkzeug
python init_db.py
python app.py
```

Open `http://127.0.0.1:5000`.

## Important safety note

This is an **educational lab**, not a production application. The SQLi, XSS, and IDOR behaviors are intentionally insecure for controlled learning. Run it only in a local or isolated environment. Do not expose it to the public internet or reuse its demo credentials, secret key, database design, or insecure routes in a real system.

## Repository layout

```text
.
├── app.py          # Flask routes and API endpoints
├── init_db.py      # Database schema and demo data initializer
├── templates/      # Jinja pages
└── static/         # CSS, JavaScript, and local uploads
```
