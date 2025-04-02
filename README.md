# This is the Al JOB SCREENING TOOL

### the backend is on the [Google Collab](https://colab.research.google.com/drive/1ExnRoDsoiP6UB4tKohfGJjvoNJQEzjMP?usp=sharing) but you can see the code in the Backend/main.py file 

## Technology
* Natural language Processing (NLP)
* Machine Learning (ML)
* Data Storage (Sqlite) 
* pyhton
* html
* css
* js

## Tools
* PyPDF2: Used to extract text from PDF resumes.
* python-docx: Extracts text from DOCX format resumes.
* Scikit-learn: A general-purpose machine learning library that could be used (though not directly in the current code) for more advanced ML tasks, like model training.
* NumPy: A fundamental library for numerical computing in Python, essential for data manipulation.
* SQLite3: A lightweight, file-based database engine used for storing candidate and job data.
* Regular Expressions (re): Used for extracting email addresses from resume text.
* SMTPlib: Enables sending email notifications to shortlisted candidates.
* Flask: Server for the backend hosting

## **Model**
* **Sentence Transformers** :-  This framework provides pre-trained language models for sentence embeddings, enabling efficient semantic similarity calculations. This is crucial for matching resumes to jobs based on meaning.
![image](https://github.com/user-attachments/assets/dfda0a65-69ed-4339-b791-03114150559e)

## **Code Structure**
* initialize_database:- initialize the SQLite database to store the shortlisted candidate. 
* load_job_descriptions:- read the csv file and load the all jobs and its description.
* extract_text_from_resume:- analyse the resume pdf and extract the text from it.
* extract_email_from_resume:- analyse the resume pdf and extract the Email from it.
* match_resumes_to_jobs:- it takes resume text and job description and compare them.
* rank_candidates:- this function rank the candidates on behalf of the score to find best fit.
* store_in_database:- This function store the candidate data in to the database.
* send_mock_email:- This function sends the mail to the shortlisted candidates.
* notify_selected_candidates:- This function takes the shortlisted candidates and give to the send_mock_email function. 
* resume_screening_pipeline:- this is the main function which execute all functions in the series to do job done.



