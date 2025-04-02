from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import sqlite3
import pandas as pd
import PyPDF2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "AI Resume Screener Backend is Running!"

@app.route("/upload", methods=["POST"])
def upload_files():
    job_file = request.files.get("job_file")
    resumes = request.files.getlist("resumes")

    if not job_file or not resumes:
        return jsonify({"error": "Job description and resumes are required!"}), 400

    job_file.save(job_file.filename)

    resume_filenames = []
    for resume in resumes:
        filepath = os.path.join("./cvs/", resume.filename)
        resume.save(filepath)
        resume_filenames.append(resume.filename)

    shortlisted = resume_screening_pipeline(job_file.filename, "./cvs/")

    os.remove(job_file.filename)
    for resume in resume_filenames:
        os.remove(os.path.join("./cvs/", resume))

    if not isinstance(shortlisted, list):
        return jsonify({"error": "Unexpected data format from resume_screening_pipeline"}), 500

    return jsonify({
        "shortlisted": [
            {"resume": entry[0], "job_title": entry[1], "match_score": float(entry[2]), "email": entry[3]}
            for entry in shortlisted if isinstance(entry, (list, tuple)) and len(entry) >= 4
        ]
    })

# AI logic
model = SentenceTransformer("all-MiniLM-L6-v2")

def initialize_database(db_name="resume_screening.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS candidates (
                      id INTEGER PRIMARY KEY,
                      resume TEXT,
                      job_title TEXT,
                      match_score REAL,
                      email TEXT)''')
    conn.commit()
    conn.close()

def load_job_descriptions(csv_path):
    df = pd.read_csv(csv_path, encoding='latin1')
    return df[['Job Title', 'Job Description']]

def extract_text_from_resume(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        with open(file_path, "rb") as pdf:
            reader = PyPDF2.PdfReader(pdf)
            for page in reader.pages:
                text += page.extract_text() + " "
    return text.strip()

def extract_email_from_resume(resume_text):
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
    return email_match.group(0) if email_match else ""

def match_resumes_to_jobs(job_descriptions, resume_texts):
    job_embeddings = model.encode(job_descriptions['Job Description'].tolist(), convert_to_tensor=True)
    resume_embeddings = model.encode(resume_texts, convert_to_tensor=True)
    return util.pytorch_cos_sim(resume_embeddings, job_embeddings).cpu().numpy()

def rank_candidates(similarity_scores, job_descriptions, resume_files):
    ranked_candidates = []
    for i, resume in enumerate(resume_files):
        best_match_index = similarity_scores[i].argmax()
        match_score = similarity_scores[i].max()
        if match_score >= 0.6:
            resume_text = extract_text_from_resume(resume)
            email = extract_email_from_resume(resume_text)
            ranked_candidates.append((resume, job_descriptions.iloc[best_match_index]['Job Title'], float(match_score), email))
    ranked_candidates.sort(key=lambda x: x[2], reverse=True)
    return ranked_candidates

def store_in_database(ranked_candidates, db_name="resume_screening.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for candidate in ranked_candidates:
        cursor.execute("INSERT INTO candidates (resume, job_title, match_score, email) VALUES (?, ?, ?, ?)",
                       (candidate[0], candidate[1], candidate[2], candidate[3]))
    conn.commit()
    conn.close()

def send_mock_email(to_email, job_title):
    sender_email = "yourcompany@example.com"
    sender_password = "yourpassword"
    subject = "Congratulations! You've Been Selected for the Role"

    body = f"""
    Dear Candidate,

    We are pleased to inform you that you have been selected for the role of {job_title} at our company.

    Please let us know your availability for the next steps.

    Best regards,
    Hiring Team
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def notify_selected_candidates(ranked_candidates):
    for candidate in ranked_candidates:
        if candidate[3]:
            send_mock_email(candidate[3], candidate[1])

def resume_screening_pipeline(job_csv, resume_folder):
    initialize_database()
    job_descriptions = load_job_descriptions(job_csv)
    resume_files = [os.path.join(resume_folder, f) for f in os.listdir(resume_folder) if f.endswith(".pdf")]
    resume_texts = [extract_text_from_resume(f) for f in resume_files]

    similarity_scores = match_resumes_to_jobs(job_descriptions, resume_texts)
    ranked_candidates = rank_candidates(similarity_scores, job_descriptions, resume_files)
    store_in_database(ranked_candidates)
    notify_selected_candidates(ranked_candidates)

    return ranked_candidates

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
