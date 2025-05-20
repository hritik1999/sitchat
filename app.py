import eventlet
eventlet.monkey_patch()
import os
from flask import Flask, request, jsonify, session
from application.auth.auth import supabase
from application.database.db import db
from application.api.api import ShowsResource, ShowResource, EpisodesResource, EpisodeResource, UserResource, ChatResource , RatingResource, AchievementsResource, LeaderboardResource,GenerateScript, GenerateShow
from application.api.socket import  setup_socket_handlers, active_stages
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO,disconnect
import threading
import logging
import time
import sys
import psutil
sys.stdout.flush()

# Simple solution: just set higher log levels for the libraries you want to silence
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set higher log levels for API-related libraries
logging.getLogger('supabase').setLevel(logging.ERROR)  # Only show errors
logging.getLogger('openai').setLevel(logging.ERROR)    # Only show errors
logging.getLogger('httpx').setLevel(logging.ERROR)     # HTTP client used by these libraries
logging.getLogger('urllib3').setLevel(logging.ERROR)   # Another HTTP client
logging.getLogger('requests').setLevel(logging.ERROR)  # Another HTTP client

# instantiate the app
app = Flask(__name__)
web_api = Api(app)

CORS(app, 
     resources={r"/*": {"origins": ["*"]}},
     supports_credentials=True)

# Get configuration from environment
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY') or 'your-secret-key-for-socket-io'

# Set Flask configuration
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG

# Set CPU and memory thresholds
CPU_THRESHOLD = 90.0
MEM_THRESHOLD = 90.0

# thread‑safe container for latest metrics
_latest = {
    "cpu_ema": psutil.cpu_percent(interval=None),
    "mem_ema": psutil.virtual_memory().percent,
}
_lock   = threading.Lock()

def _metric_loop():
    """Single background thread: sleep, sample, repeat."""
    alpha = 0.2  # smoothing factor: lower → smoother, slower to react
    while True:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        with _lock:
            # update both the EMA and (optionally) the raw values
            _latest["cpu_ema"] = alpha * cpu + (1 - alpha) * _latest["cpu_ema"]
            _latest["mem_ema"] = alpha * mem + (1 - alpha) * _latest["mem_ema"]
        time.sleep(1.0)  # sample once per second

# start once, as a daemon so it won’t block shutdown
thread = threading.Thread(target=_metric_loop, daemon=True)
thread.start()

@app.before_request
def reject_if_overloaded():
    with _lock:
        cpu = _latest["cpu_ema"]
        mem = _latest["mem_ema"]

    app.logger.info(f"CPU (EMA): {cpu:.1f}%, Memory (EMA): {mem:.1f}%")
    if cpu > CPU_THRESHOLD or mem > MEM_THRESHOLD:
        return jsonify({
            "error": "Server is at full capacity, please try again later."
        }), 503


# Initialize Socket.IO with more compatible settings
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    path="/socket.io",                     # Allow all origins for simplicity
    async_mode="eventlet",                 # Use eventlet for better websocket support
    logger=DEBUG,                          # Enable logging in debug
    engineio_logger=DEBUG,                 # Enable engine.io logging in debug
    ping_timeout=60,                       # Increase ping timeout for better stability
    ping_interval=25,                      # Adjust ping interval
    max_http_buffer_size=10e6,             # Increase buffer size for large messages
    manage_session=True,                   # Let Socket.IO manage sessions
)

# health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

# Middleware to authenticate socket.io connections
@socketio.on('connect')
def authenticate_socket():
    auth_header = None
    token = None

    with _lock:
        if _latest["cpu_ema"] > CPU_THRESHOLD or _latest["mem_ema"] > MEM_THRESHOLD:
            return disconnect() 
    
    # Check for token in auth data
    if hasattr(request, 'args') and request.args.get('token'):
        token = request.args.get('token')
    
    # Check for token in headers
    elif hasattr(request, 'headers') and request.headers.get('Authorization'):
        auth_header = request.headers.get('Authorization')
        if auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1]
        else:
            token = auth_header
    
    # Check socket.io specific auth field
    elif hasattr(request, 'auth') and request.auth.get('token'):
        token = request.auth.get('token')
    
    if token:
        try:
            # Verify token with Supabase
            user_response = supabase.auth.get_user(token)
            if user_response and hasattr(user_response, 'user') and user_response.user:
                # With the updated Supabase SDK, explicit authentication happens when we call get_user()
                # We don't need to set anything else for authentication to work
                return True
        except Exception as e:
            print(f"Socket auth error: {str(e)}")
            return False
            
    # Allow connection for now, but individual handlers should check auth
    # You could return False here to reject unauthenticated connections
    return True

@app.route("/auth/verify", methods=["POST"])
def auth_verify():
    data = request.get_json()
    token = data.get("access_token")
    if not token:
        return jsonify({"error": "Missing access token"}), 400

    try:
        # Get user from token
        user_response = supabase.auth.get_user(token)
        if not user_response:
            return jsonify({"error": "Invalid token"}), 401

        # Extract user from response
        user = user_response.user if hasattr(user_response, 'user') else user_response
        session_data = {}
        try:
            session_response = supabase.auth.get_session()
            if hasattr(session_response, 'session'):
                session = session_response.session
                session_data = {
                    'expires_at': session.expires_at if hasattr(session, 'expires_at') else None,
                    'refresh_token': session.refresh_token if hasattr(session, 'refresh_token') else None,
                }
        except Exception as e:
            print(f"Error getting session info: {str(e)}")
            # Continue anyway, verification still worked

        # Convert to a dict (if it's a Pydantic model)
        user_data = user.dict() if hasattr(user, "dict") else user
        return jsonify({
            "message": "Login successful", 
            "user": user_data,
            "session": session_data
        })
        
    except Exception as e:
        print(f"Auth verification error: {str(e)}")
        return jsonify({"error": f"Authentication error: {str(e)}"}), 401


setup_socket_handlers(socketio)
web_api.add_resource(ShowsResource, '/api/shows')
web_api.add_resource(ShowResource, '/api/shows/<show_id>')
web_api.add_resource(EpisodesResource, '/api/show/<show_id>/episodes')
web_api.add_resource(EpisodeResource, '/api/show/<show_id>/episodes/<episode_id>')
web_api.add_resource(UserResource, '/api/user')
web_api.add_resource(ChatResource, '/api/chats', '/api/chats/<string:chat_id>', '/api/episodes/<string:episode_id>/chats')
web_api.add_resource(RatingResource, '/api/ratings', '/api/ratings/<string:episode_id>')
web_api.add_resource(AchievementsResource, '/api/achievements/<string:chat_id>')
web_api.add_resource(LeaderboardResource, '/api/leaderboard')
web_api.add_resource(GenerateScript, '/api/generate_script/<string:show_id>')
web_api.add_resource(GenerateShow, '/api/generate_show')


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001, host='0.0.0.0',)