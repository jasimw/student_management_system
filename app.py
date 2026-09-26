from flask import Flask, render_template, request, redirect,session
import mysql.connector
import os

app = Flask(__name__, template_folder="templates")
app.secret_key = "student_management_secret"

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "4000")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    ssl_ca="/etc/ssl/certs/ca-certificates.crt",
    ssl_verify_cert=True,
    ssl_verify_identity=True
)
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234": 
            session["logged_in"] = True
            return redirect("/")
        else:
            return "Invalid Username or Password"
    return render_template("login.html")
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/login")
@app.route("/start")
def start():
    return redirect("/login")
@app.route("/")
def home():
    if not session.get("logged_in"):
     return redirect("/login")
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.close()

    return render_template("index.html", total_students=total_students)

@app.route("/add_student", methods=["POST"])
def add_student():
    name = request.form["name"]
    register_no = request.form["register_no"]
    department = request.form["department"]
    year = request.form["year"]

    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO students (name, register_no, department, year) VALUES (%s, %s, %s, %s)",
        (name, register_no, department, year)
    )

    db.commit()
    cursor.close()

    return redirect("/")
@app.route("/students")
def students():
    if not session.get("logged_in"):
     return redirect("/login")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    cursor.close()
    return render_template("students.html", students=data)
@app.route("/test")
def test():
    return "Test Working"
@app.route("/delete/<id>")
def delete_student(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    db.commit()
    cursor.close()
    return redirect("/students")
@app.route("/update/<id>", methods=["GET", "POST"])
def update_student(id):
    if request.method == "POST":
       cursor = db.cursor()
       name = request.form["name"]
       register_no = request.form["register_no"]
       department = request.form["department"]
       year = request.form["year"]

       cursor.execute(
            "UPDATE students SET name=%s, register_no=%s, department=%s, year=%s WHERE id=%s",
            (name, register_no, department, year, id)
       )
       db.commit()
       cursor.close()
       return redirect("/students")

    cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
    student = cursor.fetchone()
    cursor.close()

    return render_template("update.html", student=student)
@app.route("/search")
def search_student():
    name = request.args.get("name", "")
    department = request.args.get("department", "")
    year = request.args.get("year", "")

    cursor = db.cursor()

    query = "SELECT * FROM students WHERE 1=1"
    values = []

    if name:
        query += " AND name LIKE %s"
        values.append("%" + name + "%")

    if department:
        query += " AND department = %s"
        values.append(department)

    if year:
        query += " AND year = %s"
        values.append(year)

    cursor.execute(query, tuple(values))

    data = cursor.fetchall()
    cursor.close()

    return render_template("students.html", students=data)
if __name__ == "__main__":
    app.run(debug=True)
