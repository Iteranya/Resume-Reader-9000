from tinydb import TinyDB, Query  # Add TinyDB and Query import

class ResponseDB:
    """Handles database operations using TinyDB"""
    def __init__(self, db_path='responses_db.json'):
        self.db = TinyDB(db_path)
        self.query = Query()
    
    def upsert_response(self, response_data):
        """Insert or update a response based on phone number"""
        phone_number = response_data.get('Phone Number')
        
        if not phone_number:
            print("⚠️ Response missing 'Phone Number', skipping...")
            return

        # Upsert operation (update if exists, insert otherwise)
        self.db.upsert(
            response_data,
            self.query['Phone Number'] == phone_number
        )