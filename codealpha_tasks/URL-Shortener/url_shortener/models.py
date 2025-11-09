from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

db = SQLAlchemy()

class URLMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clicks = db.Column(db.Integer, default=0)
    
    def __init__(self, long_url):
        self.long_url = long_url
        self.short_code = self.generate_short_code()
    
    def generate_short_code(self):
        """Generate a random 6-character short code"""
        characters = string.ascii_letters + string.digits
        while True:
            short_code = ''.join(random.choices(characters, k=6))
            # Check if code already exists
            if not URLMapping.query.filter_by(short_code=short_code).first():
                return short_code
    
    def to_dict(self):
        return {
            'id': self.id,
            'long_url': self.long_url,
            'short_code': self.short_code,
            'short_url': f"http://localhost:5000/{self.short_code}",
            'created_at': self.created_at,
            'clicks': self.clicks
        }