import eventlet
eventlet.monkey_patch()
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
from application.database.db import db
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Verify Supabase connection
try:
    # Test database connection
    user = db.supabase.auth.get_user()
    print("Supabase client initialized successfully")
except Exception as e:
    print(f"Warning: Could not connect to Supabase: {str(e)}")
    print("Application will run with in-memory storage only")

# instantiate the app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
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

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    socketio.emit('status', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('join_session')
def handle_join(data):
    session_id = data.get('session_id')
    if session_id in active_stages:
        socketio.emit('status', {'message': f'Joined session {session_id}'})
        
        # Send the current dialogue history to catch up the client
        stage = active_stages[session_id]
        for line in stage.dialogue_history:
            socketio.emit('dialogue', line)
            
        # Ensure story completion is properly detected
        is_completed = (stage.current_objective_index >= len(stage.plot_objectives) or stage.story_completed)
        
        # If index exceeds or equals objectives count, mark story as complete
        if stage.current_objective_index >= len(stage.plot_objectives):
            stage.story_completed = True
        
        # Send the current objective info with story_completed flag
        socketio.emit('objective_status', {
            'current': stage.current_objective(),
            'index': stage.current_objective_index,
            'total': len(stage.plot_objectives),
            'completed': is_completed,
            'story_completed': is_completed,
            'final': is_completed
        })
    else:
        # Check if this is a database chat session that should be loaded
        chat_id = session_id
        try:
            chat = db.get_chat(chat_id)
            if chat:
                # Get the episode details
                episode = db.get_episode(chat['episode_id'])
                if not episode:
                    socketio.emit('error', {'message': 'Episode not found for this chat'})
                    return
                
                # Get the show details
                show = db.get_show(episode['show_id'])
                if not show:
                    socketio.emit('error', {'message': 'Show not found for this episode'})
                    return
                
                # Parse JSON fields
                characters = json.loads(show['characters']) if isinstance(show['characters'], str) else show['characters']
                plot_objectives = json.loads(episode['plot_objectives']) if isinstance(episode['plot_objectives'], str) else episode['plot_objectives']
                
                # Create the director
                director = Director(
                    director_llm,
                    show['name'],
                    show['description'], 
                    episode['background'], 
                    characters, 
                    chat['player_description'], 
                    show['relations']
                )
                
                # Create actors
                actors = {}
                for name, desc in characters.items():
                    actors[name] = Actor(
                        name=name,
                        description=desc,
                        relations=show['relations'],
                        background=episode['background'],
                        llm=actor_llm
                    )
                
                # Create player
                player = Player(
                    name=chat['player_name'],
                    description=chat['player_description']
                )
                
                # Create and store the stage
                stage = Stage(
                    actors=actors, 
                    director=director, 
                    player=player, 
                    plot_objectives=plot_objectives,
                    socketio=socketio
                )
                
                # Set the chat ID and load history
                stage.chat_id = chat_id
                stage.current_objective_index = chat['current_objective_index']
                
                # Load chat history from database
                if stage.load_chat_history():
                    # Store in active stages
                    active_stages[chat_id] = stage
                    
                    # Send status message
                    socketio.emit('status', {'message': f'Restored chat session {chat_id}'})
                    
                    # Send the dialogue history
                    for line in stage.dialogue_history:
                        socketio.emit('dialogue', line)
                    
                    # Determine completion status
                    is_completed = (chat['completed'] or 
                                   stage.current_objective_index >= len(stage.plot_objectives))
                    
                    # Send objective status
                    socketio.emit('objective_status', {
                        'current': stage.current_objective(),
                        'index': stage.current_objective_index,
                        'total': len(stage.plot_objectives),
                        'completed': is_completed,
                        'story_completed': is_completed,
                        'final': is_completed
                    })
                    
                else:
                    socketio.emit('error', {'message': 'Failed to load chat history'})
            else:
                socketio.emit('error', {'message': 'Session not found'})
        except Exception as e:
            socketio.emit('error', {'message': f'Error restoring session: {str(e)}'})

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
    socketio.run(app, debug=True, port=5001, host='0.0.0.0')