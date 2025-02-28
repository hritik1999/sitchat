from flask import request, jsonify, g
from functools import wraps
from typing import Optional, Callable
import jwt
import os
from application.database.db import db

def authenticate_request(f: Callable) -> Callable:
    """
    Decorator to authenticate API requests using Supabase JWT token
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get the authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "No valid authentication token provided"}), 401
        
        # Extract the token
        token = auth_header.split('Bearer ')[1]
        
        try:
            # Verify the token with Supabase
            user = db.supabase.auth.get_user(token)
            
            # Set the user in Flask's g object for the request
            g.user = user
            g.user_id = user.user.id
            
            # Continue with the request
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({"error": "Invalid authentication token", "details": str(e)}), 401
        
    return decorated

def get_current_user() -> Optional[dict]:
    """Helper to get the current user if authenticated"""
    if hasattr(g, 'user'):
        return g.user
    return None

def get_current_user_id() -> Optional[str]:
    """Helper to get the current user ID if authenticated"""
    if hasattr(g, 'user_id'):
        return g.user_id
    return None

class Auth:
    """
    Authentication service for sitchat application
    """
    @staticmethod
    def sign_up(email: str, password: str, username: str) -> dict:
        """Register a new user"""
        try:
            # First, create the auth user
            auth_response = db.sign_up(email, password)
            
            if not auth_response.user:
                return {"error": "Failed to create user", "details": auth_response}, 400
            
            # Then create the user profile using the service role client
            user_id = auth_response.user.id
            
            # Get the supabase client with service role - bypasses RLS
            supabase_admin = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_SERVICE_KEY')  # Make sure this is the service key
            )
            
            profile_response = supabase_admin.table('users').insert({
                "id": user_id,
                "username": username
            }).execute()
            
            profile = profile_response.data[0] if profile_response.data else None
            
            if not profile:
                return {"error": "User created but profile creation failed"}, 500
            
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "email": email,
                    "username": username
                },
                "session": auth_response.session
            }
            
        except Exception as e:
            return {"error": "Registration failed", "details": str(e)}, 500
    
    @staticmethod
    def sign_in(email: str, password: str) -> dict:
        """Sign in a user"""
        try:
            auth_response = db.sign_in(email, password)
            
            if not auth_response.user:
                return {"error": "Invalid credentials"}, 401
            
            user_id = auth_response.user.id
            
            # Get the user profile
            profile = db.get_user(user_id)
            
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "email": email,
                    "username": profile.get('username') if profile else None
                },
                "session": auth_response.session
            }
            
        except Exception as e:
            return {"error": "Login failed", "details": str(e)}, 401
    
    @staticmethod
    def sign_out() -> dict:
        """Sign out the current user"""
        try:
            db.sign_out()
            return {"success": True}
        except Exception as e:
            return {"error": "Logout failed", "details": str(e)}, 500