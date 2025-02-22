import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PyPDF2 import PdfReader
from io import BytesIO
import re
import json
import os
from datetime import datetime
from datamanager import ResponseDB
import config
# Configuration constants
# Field mappings for form responses
# Add/modify fields here when form questions change
FIELD_MAPPINGS = config.FIELD_MAPPINGS

def sanitize_field_name(field_name):
    """Convert field names to lowercase with underscores instead of spaces."""
    return field_name.lower().replace(" ", "_")

def setup_directories():
    """Create necessary directories for storing responses and attachments."""
    for directory in [config.OUTPUT_DIR, config.ATTACHMENT_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def initialize_google_services():
    """Initialize and return Google Sheets and Drive services."""
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        config.CREDENTIALS_FILE,
        config.SCOPES
    )
    
    sheets_client = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    return sheets_client, drive_service

def download_file_from_drive(service, file_id, mime_type='application/pdf'):
    """
    Download a file from Google Drive using the Drive API.
    
    Args:
        service: Google Drive service instance
        file_id: ID of the file to download
        mime_type: Expected MIME type of the file
    
    Returns:
        BytesIO object containing the file content
    """
    try:
        # Verify file type
        file_metadata = service.files().get(fileId=file_id, fields='mimeType').execute()
        if file_metadata['mimeType'] != mime_type:
            raise ValueError(f"File is not the expected type. Expected: {mime_type}, Got: {file_metadata['mimeType']}")

        # Download file
        request = service.files().get_media(fileId=file_id)
        file_content = BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        # Show download progress
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download Progress: {int(status.progress() * 100)}%")
                
        file_content.seek(0)
        return file_content.read()
        
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        raise

def extract_text_from_pdf(pdf_content):
    """Extract text content from a PDF file."""
    try:
        with BytesIO(pdf_content) as pdf_file:
            reader = PdfReader(pdf_file)
            return '\n'.join(
                page.extract_text() for page in reader.pages
                if page.extract_text()
            )
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

def extract_file_id(url):
    """Extract file ID from various Google Drive URL formats."""
    patterns = [
        r'/file/d/([^/]+)',
        r'id=([^&]+)',
        r'open\?id=([^&]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def process_attachment(drive_service, url, field_config, response_id):
    """
    Process an attachment field from the form response.
    
    Args:
        drive_service: Google Drive service instance
        url: URL of the attachment
        field_config: Configuration for this field
        response_id: Unique identifier for this response
        
    Returns:
        dict containing processed attachment information
    """
    result = {
        'original_url': url,
        'local_path': None,
        'extracted_text': None,
        'error': None
    }
    
    try:
        file_id = extract_file_id(url)
        if not file_id:
            raise ValueError("Could not extract file ID from URL")
            
        # Download file
        content = download_file_from_drive(
            drive_service, 
            file_id, 
            f"application/{field_config['format']}"
        )
        
        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{response_id}_{timestamp}.{field_config['format']}"
        filepath = os.path.join(config.ATTACHMENT_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        result['local_path'] = filepath
        
        # Extract text if configured
        if field_config.get('extract_text'):
            result['extracted_text'] = extract_text_from_pdf(content)
            
    except Exception as e:
        result['error'] = str(e)
        
    return result

def process_responses():
    """Main function to process form responses"""
    setup_directories()
    sheets_client, drive_service = initialize_google_services()
    db = ResponseDB()

    # Get form responses
    sheet = sheets_client.open(config.SPREADSHEET_NAME).sheet1
    responses = sheet.get_all_records()
    print(f"📥 Found {len(responses)} responses to process...")

    # Track processed and skipped responses
    processed_count = 0
    skipped_count = 0

    # Process each response
    for idx, response in enumerate(responses, 1):
        phone_number = str(response.get('Phone Number', ''))  # Convert to string for consistency
        timestamp = response.get('Timestamp', '')
        
        # Check if response already exists

        if db.check_duplicate(phone_number, timestamp):
            print(f"⏭️ Skipping duplicate response {idx}/{len(responses)} "
                  f"(Phone: {phone_number}, Timestamp: {timestamp})")
            skipped_count += 1
            continue

        response_id = response.get('id', datetime.now().strftime('%Y%m%d_%H%M%S'))
        processed_response = {sanitize_field_name(k): v for k, v in response.items()}
        
        # Add extra fields with default values
        processed_response["questions"] = ""
        processed_response["answers"] = ""
        processed_response["eval"] = ""
        processed_response["score"] = 0
        
        # Process special fields
        for field_name, field_config in FIELD_MAPPINGS.items():
            if field_name in response and response[field_name]:
                if field_config['type'] == 'attachment':
                    processed_response[field_name] = process_attachment(
                        drive_service,
                        response[field_name],
                        field_config,
                        response_id
                    )
        
        # Save to database
        db.upsert_response(processed_response)
        print(f"✅ Processed response {idx}/{len(responses)} (ID: {response_id})")
        processed_count += 1

    print(f"\n🎉 Processing complete:")
    print(f"   ✅ Successfully processed: {processed_count} responses")
    print(f"   ⏭️ Skipped duplicates: {skipped_count} responses")
    print(f"💾 Database saved to: {config.DATABASE_FILE}")

