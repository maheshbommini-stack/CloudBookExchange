from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key for login sessions
app.secret_key = "cloud-book-exchange-secret-key"


# ---------------- DATABASE ----------------

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db_connection()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Books table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            subject TEXT NOT NULL,
            condition TEXT NOT NULL,
            owner_id INTEGER
        )
    """)

    # Add owner_id to old database
    columns = conn.execute(
        "PRAGMA table_info(books)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "owner_id" not in column_names:

        conn.execute(
            "ALTER TABLE books ADD COLUMN owner_id INTEGER"
        )

    # Exchange requests table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS exchanges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            requester_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route("/")
def home():

    return render_template("index.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]

        # Hash password
        password = generate_password_hash(
            request.form["password"]
        )

        conn = get_db_connection()

        try:

            conn.execute(
                """
                INSERT INTO users
                (username, email, password)
                VALUES (?, ?, ?)
                """,
                (username, email, password)
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return "Email already registered!"

        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        conn.close()

        # Check password
        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["email"] = user["email"]

            return redirect(
                url_for("dashboard")
            )

        return "Invalid email or password!"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "dashboard.html"
    )


# ---------------- BOOKS + SEARCH ----------------

@app.route("/books")
def books():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    search = request.args.get(
        "search",
        ""
    ).strip()

    conn = get_db_connection()

    if search:

        books = conn.execute(
            """
            SELECT *
            FROM books

            WHERE title LIKE ?
               OR author LIKE ?
               OR subject LIKE ?

            ORDER BY id DESC
            """,
            (
                "%" + search + "%",
                "%" + search + "%",
                "%" + search + "%"
            )
        ).fetchall()

    else:

        books = conn.execute(
            """
            SELECT *
            FROM books
            ORDER BY id DESC
            """
        ).fetchall()

    conn.close()

    return render_template(
        "books.html",
        books=books
    )


# ---------------- ADD BOOK ----------------

@app.route(
    "/add-book",
    methods=["GET", "POST"]
)
def add_book():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]
        subject = request.form["subject"]
        condition = request.form["condition"]

        conn = get_db_connection()

        conn.execute(
            """
            INSERT INTO books
            (title, author, subject, condition, owner_id)

            VALUES (?, ?, ?, ?, ?)
            """,
            (
                title,
                author,
                subject,
                condition,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        return redirect(
            url_for("books")
        )

    return render_template(
        "add_book.html"
    )


# ---------------- REQUEST EXCHANGE ----------------

@app.route(
    "/request-exchange/<int:book_id>",
    methods=["POST"]
)
def request_exchange(book_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    # Find book
    book = conn.execute(
        """
        SELECT *
        FROM books
        WHERE id = ?
        """,
        (book_id,)
    ).fetchone()

    if not book:

        conn.close()

        return "Book not found!"

    # Prevent requesting own book
    if book["owner_id"] == session["user_id"]:

        conn.close()

        return "You cannot request your own book!"

    # Check duplicate request
    existing_request = conn.execute(
        """
        SELECT *
        FROM exchanges

        WHERE book_id = ?
        AND requester_id = ?
        """,
        (
            book_id,
            session["user_id"]
        )
    ).fetchone()

    if existing_request:

        conn.close()

        return "You have already requested this book!"

    # Create request
    conn.execute(
        """
        INSERT INTO exchanges
        (book_id, requester_id, status)

        VALUES (?, ?, ?)
        """,
        (
            book_id,
            session["user_id"],
            "Pending"
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("books")
    )


# ---------------- RECEIVED EXCHANGE REQUESTS ----------------

@app.route("/exchange-requests")
def exchange_requests():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    requests_list = conn.execute(
        """
        SELECT
            exchanges.id,
            exchanges.status,
            books.title,
            users.username,
            users.email

        FROM exchanges

        JOIN books
            ON exchanges.book_id = books.id

        JOIN users
            ON exchanges.requester_id = users.id

        WHERE books.owner_id = ?

        ORDER BY exchanges.id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "exchange_requests.html",
        requests=requests_list
    )


# ---------------- ACCEPT REQUEST ----------------

@app.route(
    "/accept-request/<int:request_id>",
    methods=["POST"]
)
def accept_request(request_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    # Check request belongs to owner's book
    exchange = conn.execute(
        """
        SELECT exchanges.id

        FROM exchanges

        JOIN books
            ON exchanges.book_id = books.id

        WHERE exchanges.id = ?
        AND books.owner_id = ?
        """,
        (
            request_id,
            session["user_id"]
        )
    ).fetchone()

    if not exchange:

        conn.close()

        return "Request not found!"

    # Accept
    conn.execute(
        """
        UPDATE exchanges

        SET status = 'Accepted'

        WHERE id = ?
        """,
        (request_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("exchange_requests")
    )


# ---------------- REJECT REQUEST ----------------

@app.route(
    "/reject-request/<int:request_id>",
    methods=["POST"]
)
def reject_request(request_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    # Check request belongs to owner's book
    exchange = conn.execute(
        """
        SELECT exchanges.id

        FROM exchanges

        JOIN books
            ON exchanges.book_id = books.id

        WHERE exchanges.id = ?
        AND books.owner_id = ?
        """,
        (
            request_id,
            session["user_id"]
        )
    ).fetchone()

    if not exchange:

        conn.close()

        return "Request not found!"

    # Reject
    conn.execute(
        """
        UPDATE exchanges

        SET status = 'Rejected'

        WHERE id = ?
        """,
        (request_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("exchange_requests")
    )


# ---------------- MY EXCHANGE REQUESTS ----------------

@app.route("/my-requests")
def my_requests():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    my_requests_list = conn.execute(
        """
        SELECT
            exchanges.id,
            exchanges.status,
            books.title,
            books.author,
            books.subject,
            users.username AS owner_name

        FROM exchanges

        JOIN books
            ON exchanges.book_id = books.id

        JOIN users
            ON books.owner_id = users.id

        WHERE exchanges.requester_id = ?

        ORDER BY exchanges.id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "my_requests.html",
        requests=my_requests_list
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ---------------- RUN ----------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)