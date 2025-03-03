import eventlet
eventlet.monkey_patch()
from flask import Flask, request, jsonify
from application.auth.auth import supabase
from application.api.api import ShowsResource, ShowResource, EpisodesResource, EpisodeResource, UserResource
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO

# instantiate the app
app = Flask(__name__)
web_api = Api(app)

CORS(app, 
     resources={r"/*": {"origins": ["*"]}},
     supports_credentials=True)

# Initialize Socket.IO with more compatible settings
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",  # Allow all origins for simplicity
    async_mode="eventlet",     # Use eventlet for better websocket support
    logger=True,               # Enable logging
    engineio_logger=True       # Enable engine.io logging
)

# Socket.IO events
# @socketio.on('connect')
# def handle_connect():
#     socketio.emit('status', {'message': 'Connected to server'})

# @socketio.on('disconnect')
# def handle_disconnect():
#     print("Client disconnected")

# socketio.on('join_session')
# def handle_join(data):
#     session_id = data.get('session_id')
#     if session_id in active_stages:
#         socketio.emit('status', {'message': f'Joined session {session_id}'})
        
#         # Send the current dialogue history to catch up the client
#         stage = active_stages[session_id]
#         for line in stage.dialogue_history:
#             socketio.emit('dialogue', line)
            
#         # Ensure story completion is properly detected
#         is_completed = (stage.current_objective_index >= len(stage.plot_objectives) or stage.story_completed)
        
#         # If index exceeds or equals objectives count, mark story as complete
#         if stage.current_objective_index >= len(stage.plot_objectives):
#             stage.story_completed = True
        
#         # Send the current objective info with story_completed flag
#         socketio.emit('objective_status', {
#             'current': stage.current_objective(),
#             'index': stage.current_objective_index,
#             'total': len(stage.plot_objectives),
#             'completed': is_completed,
#             'story_completed': is_completed,
#             'final': is_completed
#         })
#     else:
#         socketio.emit('error', {'message': 'Session not found'})


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


# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     response.headers.add('Access-Control-Allow-Credentials', 'true')
#     return response

# Configure API routes with socketio
# setup_api(web_api, socketio)

web_api.add_resource(ShowsResource, '/api/shows')
web_api.add_resource(ShowResource, '/api/shows/<show_id>')
web_api.add_resource(EpisodesResource, '/api/show/<show_id>/episodes')
web_api.add_resource(EpisodeResource, '/api/show/<show_id>/episodes/<episode_id>')
web_api.add_resource(UserResource, '/api/user')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001, host='0.0.0.0')