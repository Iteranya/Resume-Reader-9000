


CREDENTIALS_FILE= 'credentials.json'
SPREADSHEET_NAME = 'Test Form 2 (Responses)'
OUTPUT_DIR='responses'
ATTACHMENT_DIR = 'attachments'
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