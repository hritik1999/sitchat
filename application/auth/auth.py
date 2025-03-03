from flask import Flask, request, jsonify
from supabase import create_client
import dotenv
import os

dotenv.load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SECRET = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_SECRET)

def get_current_user():
    """Extract user ID from the authorization token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
        
    # Extract token (handle both "Bearer token" and just "token" formats)
    if auth_header.startswith("Bearer "):
        token = auth_header.split("Bearer ")[1]
    else:
        token = auth_header
        
    try:
        # Get user from Supabase
        user = supabase.auth.get_user(token)
        if user and user.user:
            return user.user.id
        return None
    except Exception as e:
        print(f"Error authenticating user: {str(e)}")
        return None