from tinydb import TinyDB, Query
import config
import os

class ResponseDB:
    """Handles database operations using TinyDB"""
    def __init__(self, db_path=config.DATABASE_FILE):
        self.db = TinyDB(db_path)
        self.query = Query()
   
    def upsert_response(self, response_data):
        """Insert or update a response based on phone number"""
        phone_number = response_data.get('phone_number')
       
        if not phone_number:
            print("⚠️ Response missing 'phone_number', skipping...")
            return
            
        # Upsert operation (update if exists, insert otherwise)
        self.db.upsert(
            response_data,
            self.query['phone_number'] == phone_number
        )

    def check_duplicate(self, phone_number, timestamp):
        """
        Check if a response already exists in the database using phone number and timestamp.
       
        Args:
            phone_number (str): phone_number to check
            timestamp (str): timestamp to check
       
        Returns:
            bool: True if a duplicate exists, False otherwise
        """
        # Use TinyDB's query interface
        result = self.db.search(
            (self.query['phone_number'] == phone_number) & 
            (self.query['timestamp'] == timestamp)
        )
        
        # For debugging
        print(f"Checking for Phone: {phone_number}, timestamp: {timestamp}")
        print(f"Found matches: {len(result)}")
        if result:
            print(f"First match: {result[0]}")
            
        return len(result) > 0