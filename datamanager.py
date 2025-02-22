from tinydb import TinyDB, Query  # Add TinyDB and Query import
import config
class ResponseDB:
    """Handles database operations using TinyDB"""
    def __init__(self, db_path=config.DATABASE_FILE):
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