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
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    token = auth_header.split("Bearer ")[-1]
    user = supabase.auth.get_user(token)

    return user if user else None