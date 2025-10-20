#analyze_resume.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
   raise RuntimeError("GOOGLE_API_KEY not set in environment")
genai.configure(api_key=api_key)

# Use a working model from your available list
model = genai.GenerativeModel("gemini-2.5-flash")

def analyze_resume(resume_text):
   prompt = f"""
You are an expert career coach and HR professional. Analyze the following resume and provide a detailed, structured report. Be specific, concise, and insightful.

Resume:
\"\"\"
{resume_text}
\"\"\"

Return your analysis in the following sections:

1. *Summary of Candidate*:
   - Briefly describe the candidate's background, field, and strengths.

2. *Strengths*:
   - List key technical, soft skills, and relevant experiences.

3. *Weaknesses & Gaps*:
   - Identify missing skills, experience gaps, or areas needing improvement.

4. *ATS (Applicant Tracking System) Score*:
   - Rate the resume's ATS compatibility out of 100.
   - Explain why the score was given.

5. *Suggested Improvements*:
   - Recommend ways to improve formatting, structure, or clarity.
   - Suggest missing keywords based on common job roles.

6. *Interview Questions (based on the resume)*:
   - Generate 5–7 technical and behavioral questions relevant to the candidate's profile.

7. *Course Recommendations*:
   - Suggest online courses to upskill or fill gaps (mention platforms like Coursera, Udemy, etc.).

Respond in clean, markdown-style formatting for readability.
"""
   response = model.generate_content(prompt)
   return response.text