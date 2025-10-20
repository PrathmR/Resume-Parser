from flask import Flask, request, render_template
import os
from utils.extract_text import extract_text_from_resume
from ai.analyze_resume import analyze_resume

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            print(f"File saved at: {filepath}")  # Debugging line to confirm file save

            # Extract text from the uploaded resume
            resume_text = extract_text_from_resume(filepath)
            print(f"Extracted Text: {resume_text[:200]}...")  # Debugging line to check extracted text

            # Analyze the extracted text using the AI model
            result = analyze_resume(resume_text)
            print(f"AI Analysis Result: {result}")  # Debugging line to confirm AI result

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
