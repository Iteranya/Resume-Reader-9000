CREDENTIALS_FILE= 'credentials.json'
SPREADSHEET_NAME = 'Test Form 2 (Responses)'
OUTPUT_DIR='responses'
RESUME_CV_DIR = 'resume_cv'
ANSWERS_DIR = 'ans_attachments'
DATABASE_FILE= 'responses_db.json'  # New config entry
SCOPES = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

FIELD_MAPPINGS =  {
    'Resume/CV': {
        'type': 'attachment',
        'format': 'pdf',
        'extract_text': True,
    }
    # Example additional fields:
    # 'profile_picture': {
    #     'type': 'attachment',
    #     'format': 'image',
    #     'extract_text': False,
    # },
    # 'email': {
    #     'type': 'text',
    # }
}

KEYMAP = {
    "timestamp": "timestamp",
    "email_address": "email_address",
    "phone_number": "phone_number",
    "resume/cv": "resume/cv",
    "nama_lengkap": "nama_lengkap",
    "tanggal_lahir": "tanggal_lahir",
    "jenis_kelamin": "jenis_kelamin",
    "posisi_yang_diinginkan": "posisi_yang_diinginkan",
    "domisili": "domisili",
    "questions": "questions",
    "answers": "answers",
    "eval": "eval",
    "score": "score",
    "Resume/CV": "Resume/CV"
}