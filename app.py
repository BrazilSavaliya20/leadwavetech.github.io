from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import os
import json
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASS', '87338@Brazil'),
        database=os.getenv('DB_NAME', 'lead_wave_db'),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/blog")
def blog():
    try:
        import os, json
        from flask import current_app as app

        # Dynamically force path to this notebook environment
        json_path = os.path.join(os.getcwd(), 'data', 'blogs.json') 
        app.logger.info(f"📁 Reading from: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            posts = json.load(f)
        app.logger.info(f"✅ Found {len(posts)} post(s).")
    except Exception as e:
        app.logger.error(f"❌ Blog load error: {e}")
        posts = []

    return render_template("blog.html", posts=posts)





@app.route("/admin/upload-blog", methods=["GET", "POST"])
def upload_blog():
    secret = request.args.get("key")
    if secret != os.getenv("ADMIN_KEY", "mysecret"):
        return "Unauthorized", 401

    if request.method == "POST":
        blog = {
            "title": request.form["title"],
            "date": request.form["date"],
            "summary": request.form["summary"],
            "slug": request.form["slug"],
            "content": request.form["content"]
        }

        try:
            path = os.path.join("data", "blogs.json")
            with open(path, "r+", encoding="utf-8") as file:
                blogs = json.load(file)
                blogs.insert(0, blog)
                file.seek(0)
                json.dump(blogs, file, indent=2)
                file.truncate()
            flash("✅ Blog uploaded successfully!", "success")
            return redirect(url_for("blog"))
        except Exception as e:
            app.logger.error(f"Blog upload failed: {e}")
            flash("❌ Error uploading blog.", "error")
            return redirect(url_for("upload_blog", key=secret))

    return render_template("blog_upload.html")

@app.route("/admin/delete-blog/<slug>")
def delete_blog(slug):
    secret = request.args.get("key")
    if secret != os.getenv("ADMIN_KEY", "mysecret"):
        return "Unauthorized", 401

    path = os.path.join("data", "blogs.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            blogs = json.load(f)

        blogs = [b for b in blogs if b["slug"] != slug]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(blogs, f, indent=2)

        flash("🗑️ Blog deleted successfully!", "success")
    except Exception as e:
        app.logger.error(f"Blog delete failed: {e}")
        flash("❌ Failed to delete blog.", "error")

    return redirect(url_for("blog", key=secret))


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    location = request.form.get("location")
    message = request.form.get("message")

    if not all([name, email, phone, location, message]):
        flash("❗ All fields are required.", "error")
        return redirect(url_for("home"))

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO contacts (name, phone, email, location, message)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, phone, email, location, message))
            conn.commit()
        flash("✅ Message submitted successfully!", "success")
    except Exception as e:
        flash("❌ There was an error saving your message.", "error")
        app.logger.error(f"Database Error: {e}")
    finally:
        conn.close()

    return redirect(url_for("home"))

@app.route("/sample", methods=["POST"])
def sample():
    firstname = request.form.get("firstname")
    email = request.form.get("email")

    if not firstname or not email:
        flash("❗ Please fill in all sample request fields.", "error")
        return redirect(url_for("home"))

    app.logger.info(f"🎁 Sample requested: {firstname}, {email}")
    flash("✅ Sample request submitted!", "success")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=False)