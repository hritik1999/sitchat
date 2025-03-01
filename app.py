import eventlet
eventlet.monkey_patch()
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO
import threading
from application.api.api import setup_api, active_stages
from application.database.db import db
from application.ai.llm import actor_llm, director_llm
from application.play.actor import Actor
from application.play.director import Director
from application.play.player import Player
from application.play.stage import Stage
from dotenv import load_dotenv
import os
import json 
import time

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
    cors_allowed_origins="*",
    async_mode="eventlet",
    logger=True,
    engineio_logger=True
)

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print("⚡ Client connected")
    socketio.emit('status', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print("💤 Client disconnected")

@socketio.on('ping')
def handle_ping(data):
    """Handle ping from client to keep connection alive"""
    socketio.emit('pong', {'timestamp': time.time()})

@socketio.on('join_session')
def handle_join(data):
    session_id = data.get('session_id')
    print(f"🔵 Socket join request for session: {session_id}")
    print(f"🔵 Available active stages: {list(active_stages.keys())}")
    
    if session_id in active_stages:
        print(f"✅ Found active stage for session: {session_id}")
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
        
        # Check if dialogue history is empty and we need to start the chat
        if len(stage.dialogue_history) == 0 and not stage.story_completed and not stage.is_processing:
            socketio.emit('status', {'message': 'Starting conversation...'})
            # Set the processing state immediately for better UI feedback
            socketio.emit('director_status', {"status": "directing", "message": "Director is directing..."})
            try:
                # Use a small delay to make sure the client is ready
                time.sleep(1)
                stage.advance_turn()
            except Exception as e:
                socketio.emit('error', {'message': f'Error starting sequence: {str(e)}'})
    else:
        # Check if this is a database chat session that should be loaded
        chat_id = session_id
        try:
            print(f"🔍 Looking up chat in database: {chat_id}")
            chat = db.get_chat(chat_id)
            if chat:
                print(f"✅ Found chat in database: {chat}")
                # Get the episode details
                episode = db.get_episode(chat['episode_id'])
                if not episode:
                    print(f"❌ Episode not found for chat: {chat_id}")
                    socketio.emit('error', {'message': 'Episode not found for this chat'})
                    return
                
                # Get the show details
                show = db.get_show(episode['show_id'])
                if not show:
                    print(f"❌ Show not found for episode: {episode['id']}")
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
                print(f"🔄 Loading chat history for: {chat_id}")
                loaded = stage.load_chat_history()
                if loaded:
                    print(f"✅ Successfully loaded chat history")
                    # Store in active stages
                    active_stages[chat_id] = stage
                    print(f"✅ Added to active_stages: {chat_id}")
                    
                    # Send status message
                    socketio.emit('status', {'message': f'Restored chat session {chat_id}'})
                    
                    # Send the dialogue history
                    for line in stage.dialogue_history:
                        socketio.emit('dialogue', line)
                    
                    # Determine completion status
                    is_completed = (chat['completed'] or 
                                   stage.current_objective_index >= len(stage.plot_objectives))
                    stage.story_completed = is_completed
                    
                    # Send objective status
                    socketio.emit('objective_status', {
                        'current': stage.current_objective(),
                        'index': stage.current_objective_index,
                        'total': len(stage.plot_objectives),
                        'completed': is_completed,
                        'story_completed': is_completed,
                        'final': is_completed
                    })
                    
                    # If there's no dialogue yet, start the conversation
                    if len(stage.dialogue_history) == 0 and not is_completed and not stage.is_processing:
                        socketio.emit('status', {'message': 'Starting conversation...'})
                        socketio.emit('director_status', {"status": "directing", "message": "Director is directing..."})
                        try:
                            # Use a small delay to make sure the client is ready
                            time.sleep(1)
                            stage.advance_turn()
                        except Exception as e:
                            socketio.emit('error', {'message': f'Error starting sequence: {str(e)}'})
                else:
                    print(f"❌ Failed to load chat history for: {chat_id}")
                    # Even if history fails to load, we should still create the stage
                    active_stages[chat_id] = stage
                    
                    # Send status message
                    socketio.emit('status', {'message': f'Created new chat session {chat_id}'})
                    
                    # Send objective status for the first objective
                    socketio.emit('objective_status', {
                        'current': stage.current_objective(),
                        'index': stage.current_objective_index,
                        'total': len(stage.plot_objectives),
                        'completed': False,
                        'story_completed': False,
                        'final': False
                    })
                    
                    # Start the conversation
                    socketio.emit('status', {'message': 'Starting new conversation...'})
                    socketio.emit('director_status', {"status": "directing", "message": "Director is directing..."})
                    try:
                        time.sleep(1)
                        stage.advance_turn()
                    except Exception as e:
                        socketio.emit('error', {'message': f'Error starting sequence: {str(e)}'})
            else:
                print(f"❌ Chat not found in database: {chat_id}")
                socketio.emit('error', {'message': 'Session not found'})
        except Exception as e:
            print(f"❌ Error restoring session: {str(e)}")
            socketio.emit('error', {'message': f'Error restoring session: {str(e)}'})

@socketio.on('get_dialogue_history')
def handle_get_dialogue_history(data):
    """Handle request for dialogue history"""
    session_id = data.get('session_id')
    print(f"🔍 Client requested dialogue history for session: {session_id}")
    
    if session_id in active_stages:
        stage = active_stages[session_id]
        print(f"✅ Found stage for session {session_id}, sending {len(stage.dialogue_history)} messages")
        
        # Send each message individually to ensure they're processed in order
        for line in stage.dialogue_history:
            socketio.emit('dialogue', line)
        
        # Also send current objective status
        is_completed = (stage.current_objective_index >= len(stage.plot_objectives) or 
                       stage.story_completed)
                       
        socketio.emit('objective_status', {
            'current': stage.current_objective(),
            'index': stage.current_objective_index,
            'total': len(stage.plot_objectives),
            'completed': is_completed,
            'story_completed': is_completed
        })
        
        # Also send current directing status if processing
        if stage.is_processing:
            socketio.emit('director_status', {"status": "directing", "message": "Director is directing..."})
        else:
            socketio.emit('director_status', {"status": "idle", "message": ""})
        
        return {'success': True, 'message_count': len(stage.dialogue_history)}
    
    # Try to find the chat in the database
    try:
        chat = db.get_chat(session_id)
        if chat:
            messages = db.get_messages(session_id)
            print(f"✅ Found {len(messages)} messages in database for chat: {session_id}")
            
            # Send messages
            for msg in messages:
                socketio.emit('dialogue', {
                    'role': msg['role'],
                    'content': msg['content'],
                    'type': msg['type']
                })
            
            # Send objective status
            episode = db.get_episode(chat['episode_id'])
            if episode:
                plot_objectives = json.loads(episode['plot_objectives']) if isinstance(episode['plot_objectives'], str) else episode['plot_objectives']
                
                socketio.emit('objective_status', {
                    'current': plot_objectives[chat['current_objective_index']] if chat['current_objective_index'] < len(plot_objectives) else None,
                    'index': chat['current_objective_index'],
                    'total': len(plot_objectives),
                    'completed': chat['completed'],
                    'story_completed': chat['completed']
                })
            
            return {'success': True, 'message_count': len(messages)}
    except Exception as e:
        print(f"❌ Error fetching dialogue history from database: {str(e)}")
    
    return {'success': False, 'error': 'Session not found'}

@socketio.on('restart_stage')
def handle_restart_stage(data):
    """Handle request to restart a potentially stuck stage"""
    session_id = data.get('session_id')
    print(f"🔄 Client requested restart for session: {session_id}")
    
    if session_id in active_stages:
        stage = active_stages[session_id]
        
        # Reset processing state to allow new actions
        stage.reset_processing_state(force=True)
        
        # If the stage has dialogue, send it again
        if stage.dialogue_history:
            print(f"✅ Resending {len(stage.dialogue_history)} messages")
            for line in stage.dialogue_history:
                socketio.emit('dialogue', line)
        
        # If there's no dialogue and not completed, try to advance
        elif not stage.story_completed:
            print("✅ Starting conversation")
            socketio.emit('status', {'message': 'Restarting conversation...'})
            socketio.emit('director_status', {"status": "directing", "message": "Director is directing..."})
            
            # Start in a background thread
            def start_in_background():
                try:
                    stage.advance_turn()
                except Exception as e:
                    socketio.emit('error', {"message": f"Error starting sequence: {str(e)}"})
            
            thread = threading.Thread(target=start_in_background)
            thread.daemon = True
            thread.start()
        
        return {'success': True, 'action': 'restarted'}
    
    return {'success': False, 'error': 'Session not found'}

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