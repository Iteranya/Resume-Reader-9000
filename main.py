import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PyPDF2 import PdfReader
from io import BytesIO
import time
import re

def download_file_from_drive(service, file_id):
    """
    Download a file from Google Drive using the Drive API.
    """
    try:
        # Get file metadata to verify it's a PDF
        file_metadata = service.files().get(fileId=file_id, fields='mimeType').execute()
        if file_metadata['mimeType'] != 'application/pdf':
            raise ValueError(f"File is not a PDF. Mime type: {file_metadata['mimeType']}")

        # Create request to download file
        request = service.files().get_media(fileId=file_id)
        
        # Download the file
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download Progress: {int(status.progress() * 100)}%")
                
        fh.seek(0)
        return fh.read()
        
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        raise

def extract_text_from_pdf(pdf_content):
    """
    Extract text from PDF content with error handling.
    """
    try:
        with BytesIO(pdf_content) as pdf_file:
            reader = PdfReader(pdf_file)
            pdf_text = []
            for page in reader.pages:
                try:
                    text = page.extract_text()
                    if text:
                        pdf_text.append(text)
                except Exception as e:
                    pdf_text.append(f"Error extracting page: {str(e)}")
            return '\n'.join(pdf_text)
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

def extract_file_id(url):
    """
    Extract file ID from various Google Drive URL formats.
    """
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

def main():
    # Configure API credentials
    print("Initializing Google APIs...")
    SCOPES = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json',
        SCOPES
    )
    
    # Initialize both Sheets and Drive services
    sheets_client = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    print("Successfully authorized with Google APIs")

    try:
        sheet = sheets_client.open('Test Form').sheet1
        data = sheet.get_all_records()
        print(f"Successfully opened sheet with {len(data)} rows")
    except Exception as e:
        print(f"Error accessing Google Sheet: {str(e)}")
        return

    for row in data:
        print(f"\n{'='*50}")
        print(f"Processing row: {row.get('id', 'N/A')}")
        
        if not row.get('resume'):
            print("No resume URL found in row")
            row['pdf_content'] = ''
            continue

        url = row['resume']
        print(f"Processing URL: {url}")
        
        try:
            file_id = extract_file_id(url)
            if not file_id:
                raise ValueError("Could not extract file ID from URL")
                
            print(f"Extracted file ID: {file_id}")
            
            # Download PDF using Drive API
            pdf_content = download_file_from_drive(drive_service, file_id)
            print(f"Successfully downloaded PDF, size: {len(pdf_content)} bytes")
            
            # Extract text
            result = extract_text_from_pdf(pdf_content)
            print(result)
            print(f"Successfully extracted text from PDF")
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            row['pdf_content'] = f"Error: {str(e)}"

        print(f"Finished processing row: {row.get('id', 'N/A')}")

if __name__ == "__main__":
    main()