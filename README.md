# RanjbarCoin – Telegram WebApp Bot

RanjbarCoin is a Telegram bot integrated with a WebApp interface that allows users to interact through a web-based UI inside Telegram.
The project includes a leaderboard system, upgrade mechanics, donation pages, and database-backed user management.

---

## 🚀 Features

* Telegram Bot integration
* Telegram WebApp interface
* User leaderboard system
* Upgrade & progression system
* Donation page
* SQLite database storage
* Interactive frontend UI
* Flask-based backend

---

## 📂 Project Structure

```
app/
├── app.py              # Main web application
├── bot.py              # Telegram bot logic
├── config.py           # Configuration variables
├── database.py         # Database connection
├── models.py           # Database models
├── init_db.py          # Database initialization
├── passenger_wsgi.py   # Deployment entry point
│
├── templates/          # HTML pages
└── static/             # CSS, JS, and assets
```

---

## ⚙️ Technologies Used

* Python
* Flask
* Telegram Bot API
* HTML / CSS / JavaScript
* SQLite

---

## 🛠 Installation

Clone the repository:

```bash
git clone https://github.com/Mrpower-coder/telegram-webapp-Ranjbarcoin.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Initialize database:

```bash
python init_db.py
```

Run the project:

```bash
python app.py
```

---

## 🌐 Deployment

The project includes a WSGI configuration (`passenger_wsgi.py`) for hosting environments that support Python web applications.

---

## 🤖 Telegram Integration

The bot communicates with the WebApp to provide interactive functionality directly inside Telegram.

---

## 📄 License

This project is intended for educational and development purposes.
