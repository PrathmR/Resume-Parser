import os
import datetime
import random
import io

# Flask imports (removed session)
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

# Data processing imports
import pandas as pd
# REMOVED: pymysql import
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
import pafy
import plotly.express as px

# Custom course data import
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos

# --- Flask App Initialization ---
app = Flask(__name__)
# REMOVED: app.secret_key
UPLOAD_FOLDER = 'Uploaded_Resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# REMOVED: All database connection and setup code

# --- Helper Functions (from your original script) ---
def fetch_yt_video(link):
    try:
        video = pafy.new(link)
        return video.title
    except Exception as e:
        print(f"Could not fetch YouTube title: {e}")
        return "YouTube Video"

def pdf_reader(file_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text

def course_recommender(course_list, no_of_reco=4):
    rec_course = []
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        rec_course.append((c_name, c_link))
        if len(rec_course) == no_of_reco:
            break
    return rec_course

# REMOVED: The insert_data function

# --- Flask Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return redirect(request.url)
        file = request.files['resume']
        if file.filename == '':
            return redirect(request.url)
        
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            # --- Start Analysis ---
            resume_data = ResumeParser(save_path).get_extracted_data()
            if resume_data:
                resume_text = pdf_reader(save_path)
                
                name = resume_data.get('name', 'N/A')
                email = resume_data.get('email', 'N/A')
                mobile = resume_data.get('mobile_number', 'N/A')
                pages = resume_data.get('no_of_pages', 0)

                cand_level = ''
                if pages == 1: cand_level = "Fresher"
                elif pages == 2: cand_level = "Intermediate"
                elif pages >= 3: cand_level = "Experienced"

                skills = resume_data.get('skills', [])
                keywords = {
                    'Data Science': ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit'],
                    'Web Development': ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'flask'],
                    'Android Development': ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy'],
                    'IOS Development': ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode'],
                    'UI-UX Development': ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'user experience']
                }
                
                reco_field = ''
                recommended_skills = []
                rec_course = []

                for i in skills:
                    if i.lower() in keywords['Data Science']:
                        reco_field = 'Data Science'
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling', 'Data Mining', 'Clustering & Classification', 'Data Analytics', 'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras', 'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask", 'Streamlit']
                        rec_course = course_recommender(ds_course)
                        break
                    # ... (other elif blocks are the same)
                    elif i.lower() in keywords['Web Development']:
                        reco_field = 'Web Development'
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento', 'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                        rec_course = course_recommender(web_course)
                        break
                    elif i.lower() in keywords['Android Development']:
                        reco_field = 'Android Development'
                        recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java', 'Kivy', 'GIT', 'SDK', 'SQLite']
                        rec_course = course_recommender(android_course)
                        break
                    elif i.lower() in keywords['IOS Development']:
                        reco_field = 'IOS Development'
                        recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode', 'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation', 'Auto-Layout']
                        rec_course = course_recommender(ios_course)
                        break
                    elif i.lower() in keywords['UI-UX Development']:
                        reco_field = 'UI-UX Development'
                        recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq', 'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Editing', 'Illustrator', 'After Effects', 'Premier Pro', 'Indesign', 'Wireframe', 'Solid', 'Grasp', 'User Research']
                        rec_course = course_recommender(uiux_course)
                        break
                
                resume_score = 0
                tips = {}
                if 'Objective' in resume_text:
                    resume_score += 20
                    tips['Objective'] = (True, "Awesome! You have added Objective.")
                else:
                    tips['Objective'] = (False, "Please add a career objective to state your intentions.")
                
                if 'Declaration' in resume_text:
                    resume_score += 20
                    tips['Declaration'] = (True, "Awesome! You have added a Declaration.")
                else:
                    tips['Declaration'] = (False, "Please add a Declaration to assure the resume's authenticity.")
                
                if 'Hobbies' in resume_text or 'Interests' in resume_text:
                    resume_score += 20
                    tips['Hobbies'] = (True, "Awesome! You have added your Hobbies.")
                else:
                    tips['Hobbies'] = (False, "Add Hobbies/Interests to show your personality.")
                
                if 'Achievements' in resume_text:
                    resume_score += 20
                    tips['Achievements'] = (True, "Awesome! You have added Achievements.")
                else:
                    tips['Achievements'] = (False, "Add Achievements to showcase your capabilities.")

                if 'Projects' in resume_text:
                    resume_score += 20
                    tips['Projects'] = (True, "Awesome! You have added your Projects.")
                else:
                    tips['Projects'] = (False, "Add Projects to demonstrate your work experience.")

                resume_vid = random.choice(resume_videos)
                res_vid_title = fetch_yt_video(resume_vid)
                interview_vid = random.choice(interview_videos)
                int_vid_title = fetch_yt_video(interview_vid)
                
                # REMOVED: The call to insert_data()

                return render_template('results.html', 
                                       name=name, email=email, mobile=mobile, pages=pages,
                                       cand_level=cand_level, skills=skills, reco_field=reco_field,
                                       recommended_skills=recommended_skills, rec_course=rec_course,
                                       resume_score=resume_score, tips=tips,
                                       resume_vid=resume_vid, res_vid_title=res_vid_title,
                                       interview_vid=interview_vid, int_vid_title=int_vid_title)

    return render_template('index.html')

# REMOVED: All admin, dashboard, logout, and download routes

if __name__ == '__main__':
    app.run(debug=True)