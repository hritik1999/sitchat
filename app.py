import eventlet
eventlet.monkey_patch()
import os
from flask import Flask, request, jsonify, session
from application.auth.auth import supabase
from application.api.api import ShowsResource, ShowResource, EpisodesResource, EpisodeResource, UserResource, ChatResource , setup_socket_handlers, active_stages
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Initialize Socket.IO with more compatible settings
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",              # Allow all origins for simplicity
    async_mode="eventlet",                 # Use eventlet for better websocket support
    logger=DEBUG,                          # Enable logging in debug
    engineio_logger=DEBUG,                 # Enable engine.io logging in debug
    ping_timeout=60,                       # Increase ping timeout for better stability
    ping_interval=25,                      # Adjust ping interval
    max_http_buffer_size=10e6,             # Increase buffer size for large messages
    manage_session=True,                   # Let Socket.IO manage sessions
)

@app.route("/auth/verify", methods=["POST"])
def auth_verify():
    data = request.get_json()
    token = data.get("access_token")
    if not token:
        return jsonify({"error": "Missing access token"}), 400

    user_response = supabase.auth.get_user(token)
    if not user_response:
        return jsonify({"error": "Invalid token"}), 401

    # If the response has a nested 'user' attribute, use that
    try:
        user = user_response.user
    except AttributeError:
        user = user_response

    # Convert to a dict (if it's a Pydantic model)
    user_data = user.dict() if hasattr(user, "dict") else user
    print(user_data)

    return jsonify({"message": "Login successful", "user": user_data})


setup_socket_handlers(socketio)
web_api.add_resource(ShowsResource, '/api/shows')
web_api.add_resource(ShowResource, '/api/shows/<show_id>')
web_api.add_resource(EpisodesResource, '/api/show/<show_id>/episodes')
web_api.add_resource(EpisodeResource, '/api/show/<show_id>/episodes/<episode_id>')
web_api.add_resource(UserResource, '/api/user')
web_api.add_resource(ChatResource, '/api/chats', '/api/chats/<string:chat_id>', '/api/episodes/<string:episode_id>/chats')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001, host='0.0.0.0')