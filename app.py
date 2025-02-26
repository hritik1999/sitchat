from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO
from application.api.api import setup_api, active_stages
from application.ai.llm import actor_llm, director_llm
from application.play.actor import Actor
from application.play.director import Director
from application.play.player import Player
from application.play.stage import Stage 

# instantiate the app
app = Flask(__name__)
web_api = Api(app)

CORS(app, 
     resources={r"/*": {"origins": ["http://localhost:5173"]}},
     supports_credentials=True)

# Initialize Socket.IO with more compatible settings
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",  # Allow all origins for simplicity
    async_mode="eventlet",     # Use eventlet for better websocket support
    logger=True,               # Enable logging
    engineio_logger=True       # Enable engine.io logging
)
# Configure CORS to explicitly allow your frontend origin




# Socket.IO events
@socketio.on('connect')
def handle_connect():
    socketio.emit('status', {'message': 'Connected to server'})

@socketio.on('join_session')
def handle_join(data):
    session_id = data.get('session_id')
    if session_id in active_stages:
        socketio.emit('status', {'message': f'Joined session {session_id}'})
    else:
        socketio.emit('error', {'message': 'Session not found'})
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Configure API routes with socketio
setup_api(web_api, socketio)

if __name__ == '__main__':
    # Important: Use eventlet for running the server
    import eventlet
    eventlet.monkey_patch()
    socketio.run(app, debug=True, port=5001, host='0.0.0.0')