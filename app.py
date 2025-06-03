from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# ✅ Firebase Initialization
cred = credentials.Certificate("firebase_key.json")  # Ensure this file exists
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("FIREBASE_DB_URL", "https://lead-wave-8f858-default-rtdb.firebaseio.com/")
})


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/blog")
def blog():
    try:
        path = os.path.join(os.getcwd(), 'data', 'blogs.json')
        with open(path, "r", encoding="utf-8") as f:
            posts = json.load(f)
    except Exception as e:
        app.logger.error(f"❌ Blog load error: {e}")
        posts = []

    # Optional: Only show post count to admin
    is_admin = request.args.get("key") == os.getenv("ADMIN_KEY", "mysecret")
    return render_template("blog.html", posts=posts, is_admin=is_admin)


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
            return redirect(url_for("blog", key=secret))
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
        ref = db.reference("/contacts")
        ref.push({
            "name": name,
            "email": email,
            "phone": phone,
            "location": location,
            "message": message
        })
        flash("✅ Message submitted successfully!", "success")
    except Exception as e:
        flash("❌ There was an error saving your message.", "error")
        app.logger.error(f"Firebase Error: {e}")

    return redirect(url_for("home"))


@app.route("/sample", methods=["POST"])
def sample():
    firstname = request.form.get("firstname")
    email = request.form.get("email")

    if not firstname or not email:
        flash("❗ Please fill in all sample request fields.", "error")
        return redirect(url_for("home"))

    try:
        ref = db.reference("/sample_requests")
        ref.push({
            "name": firstname,
            "email": email
        })
        flash("✅ Sample request submitted!", "success")
    except Exception as e:
        app.logger.error(f"Sample request failed: {e}")
        flash("❌ Failed to submit sample request.", "error")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=False)
