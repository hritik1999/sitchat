from flask_restful import Resource, Api, marshal_with, fields, reqparse, marshal
from flask import request, jsonify, g, Response
import threading
import json
import uuid
from application.ai.llm import actor_llm, director_llm
from application.play.actor import Actor
from application.play.director import Director
from application.play.player import Player
from application.play.stage import Stage
from application.database.db import db
from application.auth.auth import authenticate_request, get_current_user_id

# Store active stage sessions in memory (these aren't persisted yet)
active_stages = {}

# --- Authentication Resources ---

class AuthResource(Resource):
    def post(self, action):
        """Handle auth actions: register, login, logout"""
        if action == 'register':
            data = request.get_json()
            return db.sign_up(
                data.get('email'),
                data.get('password'),
                data.get('username')
            )
        
        elif action == 'login':
            data = request.get_json()
            return db.sign_in(
                data.get('email'),
                data.get('password')
            )
        
        elif action == 'logout':
            return db.sign_out()
        
        else:
            return {"error": "Invalid action"}, 400


# --- Show Resources ---

class ShowsResource(Resource):
    def get(self):
        """Get a list of all shows"""
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        shows = db.get_shows(limit, offset)
        return jsonify({"shows": shows})
    
    @authenticate_request
    def post(self):
        """Create a new show"""
        user_id = get_current_user_id()
        data = request.get_json()
        
        show = db.create_show(
            creator_id=user_id,
            name=data.get('name'),
            description=data.get('description'),
            characters=data.get('characters', {}),
            relations=data.get('relations', ''),
            image_url=data.get('image_url')
        )
        
        if not show:
            return {"error": "Failed to create show"}, 500
        
        return jsonify({"show": show})


class ShowResource(Resource):
    def get(self, show_id):
        """Get a specific show by ID"""
        show = db.get_show(show_id)
        
        if not show:
            return {"error": "Show not found"}, 404
        
        return jsonify({"show": show})
    
    @authenticate_request
    def put(self, show_id):
        """Update a show"""
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Verify ownership
        show = db.get_show(show_id)
        if not show or show.get('creator_id') != user_id:
            return {"error": "Not authorized to edit this show"}, 403
        
        updated_show = db.update_show(show_id, data)
        
        if not updated_show:
            return {"error": "Failed to update show"}, 500
        
        return jsonify({"show": updated_show})
    
    @authenticate_request
    def delete(self, show_id):
        """Delete a show"""
        user_id = get_current_user_id()
        
        # Verify ownership
        show = db.get_show(show_id)
        if not show or show.get('creator_id') != user_id:
            return {"error": "Not authorized to delete this show"}, 403
        
        success = db.delete_show(show_id)
        
        if not success:
            return {"error": "Failed to delete show"}, 500
        
        return {"success": True}


# --- Episode Resources ---

class EpisodesResource(Resource):
    def get(self, show_id):
        """Get all episodes for a show"""
        episodes = db.get_episodes(show_id)
        return jsonify({"episodes": episodes})
    
    @authenticate_request
    def post(self, show_id):
        """Create a new episode for a show"""
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Verify ownership of the show
        show = db.get_show(show_id)
        if not show or show.get('creator_id') != user_id:
            return {"error": "Not authorized to add episodes to this show"}, 403
        
        episode = db.create_episode(
            show_id=show_id,
            creator_id=user_id,
            name=data.get('name'),
            description=data.get('description', ''),
            background=data.get('background', ''),
            plot_objectives=data.get('plot_objectives', [])
        )
        
        if not episode:
            return {"error": "Failed to create episode"}, 500
        
        return jsonify({"episode": episode})


class EpisodeResource(Resource):
    def get(self, episode_id):
        """Get a specific episode by ID"""
        episode = db.get_episode(episode_id)
        
        if not episode:
            return {"error": "Episode not found"}, 404
        
        return jsonify({"episode": episode})
    
    @authenticate_request
    def put(self, episode_id):
        """Update an episode"""
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Verify ownership
        episode = db.get_episode(episode_id)
        if not episode or episode.get('creator_id') != user_id:
            return {"error": "Not authorized to edit this episode"}, 403
        
        updated_episode = db.update_episode(episode_id, data)
        
        if not updated_episode:
            return {"error": "Failed to update episode"}, 500
        
        return jsonify({"episode": updated_episode})
    
    @authenticate_request
    def delete(self, episode_id):
        """Delete an episode"""
        user_id = get_current_user_id()
        
        # Verify ownership
        episode = db.get_episode(episode_id)
        if not episode or episode.get('creator_id') != user_id:
            return {"error": "Not authorized to delete this episode"}, 403
        
        success = db.delete_episode(episode_id)
        
        if not success:
            return {"error": "Failed to delete episode"}, 500
        
        return {"success": True}


# --- Chat/Session Resources ---

class ChatsResource(Resource):
    def get(self):
        """Get chats for the current user or by episode"""
        user_id = request.args.get('user_id')
        episode_id = request.args.get('episode_id')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        chats = db.get_chats(user_id, episode_id, limit, offset)
        return jsonify({"chats": chats})
    
    @authenticate_request
    def post(self):
        """Create a new chat session"""
        user_id = get_current_user_id()
        data = request.get_json()
        
        chat = db.create_chat(
            episode_id=data.get('episode_id'),
            user_id=user_id,
            player_name=data.get('player_name', 'Player'),
            player_description=data.get('player_description', '')
        )
        
        if not chat:
            return {"error": "Failed to create chat"}, 500
        
        # Start the chat session in memory
        chat_id = chat['id']
        
        # Get the episode details
        episode = db.get_episode(data.get('episode_id'))
        if not episode:
            return {"error": "Episode not found"}, 404
        
        # Get the show details
        show = db.get_show(episode['show_id'])
        if not show:
            return {"error": "Show not found"}, 404
        
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
            data.get('player_description', ''), 
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
            name=data.get('player_name', 'Player'),
            description=data.get('player_description', '')
        )
        
        # Create and store the stage in memory
        stage = Stage(
            actors=actors, 
            director=director, 
            player=player, 
            plot_objectives=plot_objectives,
            socketio=self.socketio if hasattr(self, 'socketio') else None
        )
        
        # Store the chat_id to link with database
        stage.chat_id = chat_id
        
        # Store in active stages
        active_stages[chat_id] = stage
        
        # Start the stage sequence in a background thread to not block the response
        def start_sequence():
            try:
                # Give the frontend a moment to connect to the socket before starting
                import time
                time.sleep(1)
                
                # Start the sequence
                result = stage.advance_turn()
                
                # Save the initial dialogue to the database
                if result.get('dialogue'):
                    db.add_messages_batch(chat_id, result['dialogue'])
                
            except Exception as e:
                if hasattr(self, 'socketio'):
                    self.socketio.emit('error', {'message': f'Error starting sequence: {str(e)}'})
            
        thread = threading.Thread(target=start_sequence)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'chat_id': chat_id,
            'message': 'Chat created and started automatically',
            'state': stage.get_state()
        })


class ChatResource(Resource):
    def get(self, chat_id):
        """Get a specific chat by ID with its messages"""
        chat = db.get_chat(chat_id)
        
        if not chat:
            return {"error": "Chat not found"}, 404
        
        # Get the messages for this chat
        messages = db.get_messages(chat_id)
        
        return jsonify({
            "chat": chat,
            "messages": messages
        })
    
    @authenticate_request
    def delete(self, chat_id):
        """Delete a chat"""
        user_id = get_current_user_id()
        
        # Verify ownership
        chat = db.get_chat(chat_id)
        if not chat or chat.get('user_id') != user_id:
            return {"error": "Not authorized to delete this chat"}, 403
        
        # Remove from active stages if present
        if chat_id in active_stages:
            del active_stages[chat_id]
        
        success = db.delete_chat(chat_id)
        
        if not success:
            return {"error": "Failed to delete chat"}, 500
        
        return {"success": True}


# --- Stage Resources (for interactive chat) ---

class StageResource(Resource):
    def __init__(self, socketio):
        self.socketio = socketio
        
    def post(self):
        """Create a new stage session with database integration"""
        data = request.get_json()
        
        # Check if user is authenticated
        user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                token = auth_header.split('Bearer ')[1]
                user = db.supabase.auth.get_user(token)
                user_id = user.user.id
            except:
                # Continue as anonymous
                pass
        
        show = data.get('show')
        description = data.get('description')
        background = data.get('background')
        actors_data = data.get('actors_data')
        relations = data.get('relations')
        player_name = data.get('player_name', 'Player')
        player_description = data.get('player_description')
        plot_objectives = data.get('plot_objectives')
        
        # Create director
        director = Director(
            director_llm,
            show,
            description, 
            background, 
            actors_data, 
            player_description, 
            relations
        )
        
        # Create actors
        actors = {}
        for name, desc in actors_data.items():
            actors[name] = Actor(
                name=name,
                description=desc,
                relations=relations,
                background=background,
                llm=actor_llm
            )
        
        # Create player
        player = Player(
            name=player_name,
            description=player_description
        )
        
        # Create a unique ID for this session
        session_id = str(uuid.uuid4())
        
        # Create and store the stage
        stage = Stage(
            actors=actors, 
            director=director, 
            player=player, 
            plot_objectives=plot_objectives,
            socketio=self.socketio
        )
        
        active_stages[session_id] = stage
        
        # If a user is logged in, save this session to the database
        if user_id:
            try:
                # First check if this show exists in the DB, or create it
                shows = db.get_shows_by_creator(user_id)
                show_id = None
                
                for existing_show in shows:
                    if existing_show['name'] == show:
                        show_id = existing_show['id']
                        break
                
                if not show_id:
                    # Create a new show
                    new_show = db.create_show(
                        creator_id=user_id,
                        name=show,
                        description=description,
                        characters=actors_data,
                        relations=relations
                    )
                    show_id = new_show['id']
                
                # Now create or find the episode
                episodes = db.get_episodes(show_id)
                episode_id = None
                episode_name = f"Episode {len(episodes) + 1}"
                
                new_episode = db.create_episode(
                    show_id=show_id,
                    creator_id=user_id,
                    name=episode_name,
                    description=f"Generated episode for {show}",
                    background=background,
                    plot_objectives=plot_objectives
                )
                episode_id = new_episode['id']
                
                # Finally, create a chat record
                chat = db.create_chat(
                    episode_id=episode_id,
                    user_id=user_id,
                    player_name=player_name,
                    player_description=player_description
                )
                
                # Link the chat ID to the stage for message persistence
                stage.chat_id = chat['id']
                
            except Exception as e:
                # Soft fail - continue with in-memory only
                print(f"Failed to save session to database: {str(e)}")
        
        # Start the stage sequence in a background thread to not block the response
        def start_sequence():
            try:
                # Give the frontend a moment to connect to the socket before starting
                import time
                time.sleep(1)
                stage.run_sequence()
            except Exception as e:
                self.socketio.emit('error', {'message': f'Error starting sequence: {str(e)}'})
            
        thread = threading.Thread(target=start_sequence)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'message': 'Stage created and started automatically',
            'state': stage.get_state()
        })
    
    def get(self, session_id):
        """Get the state of a stage session"""
        if session_id not in active_stages:
            return {'error': 'Session not found'}, 404
            
        stage = active_stages[session_id]
        return jsonify({
            'session_id': session_id,
            'state': stage.get_state()
        })


class AdvanceTurnResource(Resource):
    def __init__(self, socketio):
        self.socketio = socketio
        
    def post(self, session_id):
        """
        Manual trigger to advance the turn for a stage session
        Note: With the automatic progression, this should rarely be needed
        """
        if session_id not in active_stages:
            return {'error': 'Session not found'}, 404
            
        stage = active_stages[session_id]
        
        # Start advance_turn in a background thread to not block the response
        def advance_in_background():
            try:
                result = stage.advance_turn()
                
                # Save dialogue to database if chat_id is linked
                if hasattr(stage, 'chat_id') and result.get('dialogue'):
                    db.add_messages_batch(stage.chat_id, result['dialogue'])
                    
                    # Update chat progress
                    db.update_chat(stage.chat_id, {
                        'current_objective_index': stage.current_objective_index,
                        'completed': stage.current_objective_index >= len(stage.plot_objectives)
                    })
                    
            except Exception as e:
                self.socketio.emit('error', {'message': f'Error advancing turn: {str(e)}'})
            
        thread = threading.Thread(target=advance_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'message': 'Turn advancement started',
            'state': stage.get_state()
        })
    

class PlayerInterruptResource(Resource):
    def __init__(self, socketio):
        self.socketio = socketio
        
    def post(self, session_id):
        """Handle a player interruption"""
        if session_id not in active_stages:
            return {'error': 'Session not found'}, 404
            
        data = request.get_json()
        player_input = data.get('player_input', '')
        
        if not player_input.strip():
            return {'error': 'Empty player input'}, 400
            
        stage = active_stages[session_id]
        
        # Handle interrupt in a background thread to not block the response
        def interrupt_in_background():
            try:
                result = stage.player_interrupt(player_input)
                
                # Save player input and resulting dialogue to database if chat_id is linked
                if hasattr(stage, 'chat_id'):
                    # First add the player input message
                    player_message = {
                        'role': stage.player.name,
                        'content': player_input,
                        'type': 'player_input',
                        'sequence': len(db.get_messages(stage.chat_id))
                    }
                    db.add_message(
                        chat_id=stage.chat_id,
                        role=player_message['role'],
                        content=player_message['content'],
                        type=player_message['type'],
                        sequence=player_message['sequence']
                    )
                    
                    # Then add any resulting dialogue
                    if result.get('dialogue'):
                        # Get the latest sequence number
                        current_messages = db.get_messages(stage.chat_id)
                        start_sequence = len(current_messages)
                        
                        # Prepare messages with proper sequence numbers
                        dialogue_messages = []
                        for idx, msg in enumerate(result['dialogue']):
                            dialogue_messages.append({
                                'role': msg['role'],
                                'content': msg['content'],
                                'type': msg['type'],
                                'sequence': start_sequence + idx
                            })
                        
                        db.add_messages_batch(stage.chat_id, dialogue_messages)
                    
                    # Update chat progress
                    db.update_chat(stage.chat_id, {
                        'current_objective_index': stage.current_objective_index,
                        'completed': stage.current_objective_index >= len(stage.plot_objectives)
                    })
                    
            except Exception as e:
                self.socketio.emit('error', {'message': f'Error processing interruption: {str(e)}'})
            
        thread = threading.Thread(target=interrupt_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'message': 'Player interruption processed',
            'state': stage.get_state()
        })


def setup_api(api, socketio):
    # Authentication endpoints
    api.add_resource(AuthResource, '/api/auth/<string:action>')
    
    # Show endpoints
    api.add_resource(ShowsResource, '/api/shows')
    api.add_resource(ShowResource, '/api/shows/<string:show_id>')
    
    # Episode endpoints
    api.add_resource(EpisodesResource, '/api/shows/<string:show_id>/episodes')
    api.add_resource(EpisodeResource, '/api/episodes/<string:episode_id>')
    
    # Chat endpoints
    api.add_resource(ChatsResource, '/api/chats')
    api.add_resource(ChatResource, '/api/chats/<string:chat_id>')
    
    # Interactive stage endpoints (maintained for compatibility)
    api.add_resource(StageResource, '/api/stage', '/api/stage/<string:session_id>', 
                    resource_class_kwargs={'socketio': socketio})
    api.add_resource(AdvanceTurnResource, '/api/stage/<string:session_id>/advance',
                    resource_class_kwargs={'socketio': socketio})
    api.add_resource(PlayerInterruptResource, '/api/stage/<string:session_id>/interrupt',
                    resource_class_kwargs={'socketio': socketio})