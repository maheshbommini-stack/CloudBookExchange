# 📚 Cloud Book Exchange

A web-based book exchange platform where users can register, log in, add books, search available books, and request books from other users for exchange.

The project is developed using **Python Flask, SQLite, HTML, CSS, and JavaScript**.

---

## 🚀 Project Overview

Cloud Book Exchange provides a simple platform for students and book readers to exchange books with each other.

Users can:

- Create an account
- Log in securely
- Add books they want to exchange
- View available books
- Search for books
- Request a book from another user
- View exchange requests
- Accept exchange requests
- Reject exchange requests
- Log out securely

---

## ✨ Features

### 👤 User Authentication

- User registration
- User login
- Session-based authentication
- Secure password hashing
- Logout functionality
- Prevents unauthorized users from accessing protected pages

### 📚 Book Management

Users can:

- Add a new book
- Enter book title
- Enter author name
- Enter subject
- Select book condition
- View available books
- Store the book owner information

### 🔍 Book Search

Users can search books using:

- Book title
- Author
- Subject

The search uses partial matching, making it easier to find books.

### 🔄 Exchange Requests

Users can request books from other users.

The system prevents:

- Requesting your own book
- Duplicate exchange requests
- Requests from users who are not logged in

### ✅ Accept / Reject Requests

Book owners can view requests for their books.

They can:

- Accept a request
- Reject a request
- View the current request status

Request statuses include:

- `Pending`
- `Accepted`
- `Rejected`

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| HTML5 | Web page structure |
| CSS3 | Website styling |
| JavaScript | Frontend interactions |
| Jinja2 | Dynamic HTML templates |
| Werkzeug | Password hashing |

---

## 📂 Project Structure

```text
cloudbookexchange/
│
├── app.py
├── database.db
├── requirements.txt
├── README.md
│
├── templates/
│   ├── add_book.html
│   ├── books.html
│   ├── dashboard.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── exchange_requests.html
│
└── static/
    ├── style.css
    └── script.js
