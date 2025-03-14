# Okay, here we go...

import llm
import regex

def prompt_for_commentary(res:str, des:str):
    system_prompt = f"You are Assistant, you will compare the given parsed resume with the desired job position and write down commentaries and summaries on it.\n\nThe summary/commentary must contain:\n1. The job seeker's background\n2. The job seeker's related experience with the position  they're applying (if any)\n3. The job seeker's additional and adjacent experience with similar stuff\n4. Any critique or praise for the resume\n5. Missing information if any\n\nImportant: DO NOT make any decision on job acceptance or not. Assistant only comments, Assistant does not make any accepting-related comment. Also DO NOT make any comment on resume formatting/structure/etc."
    user_prompt = f"User: <parsed_resume> {res} </parsed_resume>\n<parsed_job_position>{des}</parsed_job_position> Based on the given data, write down your commentary"
    assist_prompt = "Assistant: Understood, here's my detailed commentary on the resume."
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": assist_prompt},
    ]

def prompt_for_questions(com:str):
    system_prompt = f"You are Assistant, you will create 5 interview question from the given resume summary and commentary\n\nThe 5 interview  question must contain:\n1. Asking for missing details in the resume if any\n2. Asking in more detail about the job seeker's experience\n3. Asking in more detail about the job seeker's prior experience\n4. Asking in more detail about the job seeker's motivation\n5. All questions must refer to the job seeker's resume and desired job position\n\nEach question MUST be written between brackets like in the following format:\n[1. What is your full name?]\n[2. This is an example question, obviously]\n[3. Also example question?]"
    user_prompt = f"User: <parsed_commentary> {com} </parsed_commentary>\n Write down 5 interview questions based on the resume commentary"
    assist_prompt = "Assistant: Understood, here's 5 related interview questions:"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": assist_prompt},
    ]

def make_commentary(resume_cv_string, desired_position_string):
    res = resume_cv_string
    des = desired_position_string
    prompt = prompt_for_commentary(res,des)
    result = llm.send_prompt(prompt)
    return result

def make_question(commentary_string):

    com = commentary_string
    prompt = prompt_for_questions(com)
    result = llm.send_prompt(prompt)
    return result

def create_interview_question(resume,position):
    raw_questions = make_question(make_commentary(resume,position))
    cleaned_questions_array = regex.extract_bracketed_text(raw_questions)
    return cleaned_questions_array