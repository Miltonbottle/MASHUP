import os
import zipfile
from flask import Flask, render_template, request
from dotenv import load_dotenv
import yagmail
import importlib.util
import sys

# Load environment variables
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Add FFmpeg path
ffmpeg_path = r"C:\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

# Dynamically load 102303460.py
file_path = os.path.join(os.path.dirname(__file__), "102303460.py")
spec = importlib.util.spec_from_file_location("mashup_module", file_path)
mashup_module = importlib.util.module_from_spec(spec)
sys.modules["mashup_module"] = mashup_module
spec.loader.exec_module(mashup_module)

generate_mashup = mashup_module.generate_mashup

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            singer = request.form["singer"]
            count = int(request.form["count"])
            duration = int(request.form["duration"])
            email = request.form["email"]

            output_file = "mashup.mp3"

            # 🔥 Generate mashup
            generate_mashup(singer, count, duration, output_file)

            # 🔥 Create ZIP
            zip_filename = "mashup.zip"
            with zipfile.ZipFile(zip_filename, "w") as zipf:
                zipf.write(output_file)

            # 🔥 Send Email
            yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)
            yag.send(
                to=email,
                subject="Your Mashup File 🎵",
                contents="Your mashup is ready! Please find the attached ZIP file.",
                attachments=zip_filename
            )

            # Return success message to interface
            return render_template(
                "index.html",
                success="Mashup generated and sent successfully to your email!"
            )

        except Exception as e:
            return render_template(
                "index.html",
                error=str(e)
            )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
