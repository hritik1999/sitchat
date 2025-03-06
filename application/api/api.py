from flask_restful import Resource, Api, marshal_with, fields, reqparse, marshal
from flask import request, jsonify, g, Response, session
import threading
from application.database.db import db
from application.auth.auth import get_current_user
import os
import uuid
import json
from application.play.stage import Stage
from application.play.actor import Actor
from application.play.director import Director
from application.play.player import Player
from application.ai.llm import actor_llm, director_llm
from flask_socketio import join_room, leave_room

class UserResource(Resource):

    def get(self):
        # Get current user from the token
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401

        # Get user data from the database
        user = db.get_user(user_id)
        if not user:
            return {"error": "User not found"}, 404
        user_shows = db.get_shows_by_creator(user_id)
        user_episodes = db.get_episodes_by_creator(user_id)
        # Return the user data as a JSON response
        return jsonify({"user": user, "user_shows": user_shows, "user_episodes": user_episodes})
    
    def put(self):
        """Update user profile including avatar"""
        try:
            # Get current user from the token
            user_id = get_current_user()
            if not user_id:
                return {"error": "Unauthorized.Please login again"}, 401

            # Get current user data
            current_user = db.get_user(user_id)
            if not current_user:
                return {"error": "User not found"}, 404

            # Get form data
            form_data = request.form.get('data')
            if not form_data:
                return {"error": "No form data provided"}, 400

            # Parse JSON data
            try:
                data = json.loads(form_data)
            except json.JSONDecodeError:
                return {"error": "Invalid form data format"}, 400

            # Initialize avatar_url with existing URL
            avatar_url = current_user.get('avatar_url')

            # Handle avatar upload if provided
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file.filename != '':
                    # Validate file type
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    if '.' not in file.filename or \
                    file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                        return {"error": "Invalid file type"}, 400

                    try:
                        # Create unique filename
                        file_ext = file.filename.rsplit('.', 1)[1].lower()
                        filename = f"{str(uuid.uuid4())}.{file_ext}"
                        
                        # Save file temporarily
                        temp_path = os.path.join('/tmp', filename)
                        file.save(temp_path)

                        # Upload to storage
                        with open(temp_path, 'rb') as f:
                            file_content = f.read()
                        
                        result = db.supabase.storage.from_('show-images').upload(
                            path=filename,
                            file=file_content
                        )

                        # Clean up temp file
                        os.remove(temp_path)

                        if result and hasattr(result, 'error') and result.error:
                            return {"error": f"Upload failed: {result.error}"}, 500

                        # Get public URL for the new avatar
                        avatar_url = db.supabase.storage.from_('show-images').get_public_url(filename)

                        # Delete old avatar if exists
                        if current_user.get('avatar_url'):
                            try:
                                old_filename = current_user['avatar_url'].split('/')[-1]
                                db.supabase.storage.from_('show-images').remove(old_filename)
                            except Exception as e:
                                print(f"Warning: Failed to delete old avatar: {str(e)}")

                    except Exception as e:
                        print(f"Upload error: {str(e)}")
                        return {"error": f"Upload failed: {str(e)}"}, 500

            # Prepare update data
            update_data = {
                'username': data.get('username'),
                'email': data.get('email')
            }
            
            # Only include avatar_url if it has changed
            if avatar_url != current_user.get('avatar_url'):
                update_data['avatar_url'] = avatar_url

            # Update user profile
            updated_user = db.update_user_profile(user_id, update_data)
            
            if updated_user:
                return jsonify({"user": updated_user})
            else:
                # Try to get the user again to confirm the update
                check_user = db.get_user(user_id)
                if check_user:
                    return jsonify({"user": check_user})
                return {"error": "Failed to update user"}, 500

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {"error": f"An error occurred: {str(e)}"}, 500

class ShowsResource(Resource):
    def get(self):
        """Get a list of all shows"""
        shows = db.get_shows()
        return jsonify({"shows": shows})
        
    def post(self):
        """Create a new show"""
        # Get current user from the token
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401
            
        # Check if image file is provided
        if 'image' not in request.files:
            return {"error": "No image file provided"}, 400
            
        # Get the image file
        file = request.files['image']
        if file.filename == '':
            return {"error": "No selected file"}, 400
            
        # Get form data from the 'data' field
        form_data = request.form.get('data')
        if not form_data:
            return {"error": "No form data provided"}, 400
            
        # Parse the JSON data
        try:
            data = json.loads(form_data)
        except json.JSONDecodeError:
            return {"error": "Invalid form data format"}, 400
            
        # Validate file type (accept only images)
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in file.filename or \
           file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return {"error": "Invalid file type"}, 400
            
        try:
            # Create a unique filename
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{str(uuid.uuid4())}.{file_ext}"
            
            # Save file temporarily
            temp_path = os.path.join('/tmp', filename)
            file.save(temp_path)
            
            # Upload to Supabase storage
            with open(temp_path, 'rb') as f:
                file_content = f.read()
                
            # Upload to 'show-images' bucket
            result = db.supabase.storage.from_('show-images').upload(
                path=filename,
                file=file_content
            )
            
            # Clean up temp file
            os.remove(temp_path)
            
            # Check for Supabase storage errors
            if result and hasattr(result, 'error') and result.error:
                return {"error": f"Upload failed: {result.error}"}, 500
                
            # Get public URL
            public_url = db.supabase.storage.from_('show-images').get_public_url(filename)
            
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return {"error": f"Upload failed: {str(e)}"}, 500
        
        try:
            # Create the show in the database
            show = db.create_show(
                creator_id=user_id,
                name=data.get('name'),
                description=data.get('description'),
                characters=data.get('characters', []),
                relations=data.get('relations', ''),
                image_url=public_url
            )
        except Exception as e:
            print(f"database error:{str(e)}")
            return {"error":f'database problem: {str(e)}'}, 500

        
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
    
    def put(self, show_id):
        """Update a show"""
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401

        # Verify ownership
        show = db.get_show(show_id)
        if not show or show.get('creator_id') != user_id:
            return {"error": "Not authorized to edit this show"}, 403

        # Get form data from the 'data' field
        form_data = request.form.get('data')
        if not form_data:
            return {"error": "No form data provided"}, 400

        # Parse the JSON data
        try:
            data = json.loads(form_data)
        except json.JSONDecodeError:
            return {"error": "Invalid form data format"}, 400

        # Initialize public_url with existing image URL
        public_url = show.get('image_url')

        # Handle image upload if provided
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Validate file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' not in file.filename or \
                file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                    return {"error": "Invalid file type"}, 400

                try:
                    # Create a unique filename
                    file_ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"{str(uuid.uuid4())}.{file_ext}"
                    
                    # Save file temporarily
                    temp_path = os.path.join('/tmp', filename)
                    file.save(temp_path)

                    # Upload to Supabase storage
                    with open(temp_path, 'rb') as f:
                        file_content = f.read()
                    
                    # Upload to 'show-images' bucket
                    result = db.supabase.storage.from_('show-images').upload(
                        path=filename,
                        file=file_content
                    )

                    # Clean up temp file
                    os.remove(temp_path)

                    # Check for Supabase storage errors
                    if result and hasattr(result, 'error') and result.error:
                        return {"error": f"Upload failed: {result.error}"}, 500

                    # Get new public URL
                    public_url = db.supabase.storage.from_('show-images').get_public_url(filename)

                    # Delete old image if it exists
                    if show.get('image_url'):
                        try:
                            old_filename = show['image_url'].split('/')[-1]
                            db.supabase.storage.from_('show-images').remove(old_filename)
                        except Exception as e:
                            print(f"Warning: Failed to delete old image: {str(e)}")

                except Exception as e:
                    print(f"Upload error: {str(e)}")
                    return {"error": f"Upload failed: {str(e)}"}, 500

        # Update the show data
        update_data = {
            'name': data.get('name'),
            'description': data.get('description'),
            'characters': data.get('characters', []),
            'relations': data.get('relations', ''),
        }
        
        # Only update image_url if a new image was uploaded
        if public_url != show.get('image_url'):
            update_data['image_url'] = public_url

        try:
            updated_show = db.update_show(show_id, update_data)
            if not updated_show:
                return {"error": "Failed to update show"}, 500
            return jsonify({"show": updated_show})
        except Exception as e:
            print(f"Database error: {str(e)}")
            return {"error": f"Database problem: {str(e)}"}, 500
    
    def delete(self, show_id):
        """Delete a show"""
        user_id = get_current_user()
        
        # Verify ownership
        show = db.get_show(show_id)
        if not show or show.get('creator_id') != user_id:
            return {"error": "Not authorized to delete this show"}, 403
        
        success = db.delete_show(show_id)
        
        if not success:
            return {"error": "Failed to delete show"}, 500
        
        return {"success": True}
    
class EpisodesResource(Resource):
    def get(self, show_id):
        """Get all episodes for a show"""
        episodes = db.get_episodes(show_id)
        return jsonify({"episodes": episodes})

    def post(self, show_id):
        """Create a new episode for a show"""
        user_id = get_current_user()
        data = request.get_json()
        # Verify authentication
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401
        
        # Verify ownership of the show
        show = db.get_show(show_id)
        if not show:
            return {"error": "Show not found"}, 404
        
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
    def get(self,show_id, episode_id):
        """Get a specific episode by ID"""
        episode = db.get_episode(episode_id)
        if not episode:
            return {"error": "Episode not found"}, 404
        
        return jsonify({"episode": episode})
    
    def put(self, show_id, episode_id):
        """Update an episode"""
        user_id = get_current_user()
        data = request.get_json()
        
        # Verify ownership
        episode = db.get_episode(episode_id)
        if not episode or episode.get('creator_id') != user_id:
            return {"error": "Not authorized to edit this episode"}, 403
        
        updated_episode = db.update_episode(episode_id, data)
        
        if not updated_episode:
            return {"error": "Failed to update episode"}, 500
        
        return jsonify({"episode": updated_episode})
    
    def delete(self,show_id, episode_id):
        """Delete an episode"""
        user_id = get_current_user()
        
        # Verify ownership
        episode = db.get_episode(episode_id)
        if not episode or episode.get('creator_id') != user_id:
            return {"error": "Not authorized to delete this episode"}, 403
        
        success = db.delete_episode(episode_id)
        
        if not success:
            return {"error": "Failed to delete episode"}, 500
        
        return {"success": True}
    
    
class ChatResource(Resource):
    def post(self, episode_id):
        """Create a new chat session for an episode"""
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401
            
        data = request.get_json()
        player_name = data.get('player_name', 'Player')
        player_description = data.get('player_description', '')

        # Fetch episode details
        episode = db.get_episode(episode_id)
        if not episode:
            return {"error": "Episode not found"}, 404
            
        # Create a new chat in the database
        chat = db.create_chat(
            episode_id=episode_id,
            user_id=user_id,
            player_name=player_name,
            player_description=player_description
        )
        
        if not chat:
            return {"error": "Failed to create chat session"}, 500

        return jsonify({
            "chat": chat,
        })
    
    def get(self, chat_id=None):
        """Get chat sessions"""
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401
        
        # If chat_id is provided, get that specific chat
        if chat_id:
            chat = db.get_chat(chat_id)
            if not chat:
                return {"error": "Chat not found"}, 404
                
            # Verify ownership
            if chat.get('user_id') != user_id:
                return {"error": "Not authorized to access this chat"}, 403
                
            # Get messages for this chat
            messages = db.get_messages(chat_id)
            
            return jsonify({
                "chat": chat,
                "messages": messages
            })
        
        # Otherwise, get all chats for the user
        chats = db.get_chats(user_id)
        return jsonify({"chats": chats})


# In-memory cache of active stages (for performance)
active_stages = {}

def setup_socket_handlers(socketio):
    """Set up Socket.IO event handlers for chat interaction"""
    
    # Connection is already handled by the global socket.io middleware
    # This function is no longer needed
    # @socketio.on('connect')
    # def handle_connect():
    #    """Handle client connection"""
    #    socketio.emit('status', {'message': 'Connected to server'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f"Client disconnected: {request.sid}")
        # We don't remove stages from memory on disconnect to support reconnection

    @socketio.on('join_chat')
    def handle_join_chat(data):
        """Join a chat room and initialize if needed"""
        chat_id = data.get('chat_id')
        if not chat_id:
            socketio.emit('error', {'message': 'No chat ID provided'}, room=request.sid)
            return
            
        # Get the chat from database
        chat = db.get_chat(chat_id)
        if not chat:
            socketio.emit('error', {'message': 'Chat not found'}, room=request.sid)
            return
            
        # Join the Socket.IO room for this chat
        join_room(chat_id)
        
        # Get chat messages directly from database
        messages = db.get_messages(chat_id)
        
        # Send the chat history to the client
        for message in messages:
            socketio.emit('dialogue', {
                'role': message.get('role'),
                'content': message.get('content'),
                'type': message.get('type')
            }, room=request.sid)
        
        # Check if stage already exists in memory
        if chat_id in active_stages:
            # Get existing stage
            stage = active_stages[chat_id]
            
            # Check if story is completed
            if stage.story_completed:
                socketio.emit('objective_status', {
                    'completed': True,
                    'story_completed': True,
                    'index': stage.current_objective_index,
                    'total': len(stage.plot_objectives),
                    'message': 'Story is already complete.'
                }, room=request.sid)
            else:
                # Send the current objective info
                current_obj = stage.current_objective()
                socketio.emit('objective_status', {
                    'completed': False,
                    'story_completed': False,
                    'index': stage.current_objective_index,
                    'current': current_obj,
                    'total': len(stage.plot_objectives)
                }, room=request.sid)
        else:
            # Get the completed status from the chat data
            is_completed = chat.get('completed', False) or chat.get('story_completed', False)
            
            if is_completed:
                # Send completed status directly from database
                # We don't need to initialize the stage if it's already completed
                total_objectives = len(json.loads(chat.get('plot_objectives', '[]'))) if isinstance(chat.get('plot_objectives'), str) else len(chat.get('plot_objectives', []))
                socketio.emit('objective_status', {
                    'completed': True,
                    'story_completed': True,
                    'index': chat.get('current_objective_index', 0),
                    'total': total_objectives,
                    'message': 'Story is already complete.'
                }, room=request.sid)
            else:
                # If chat exists but stage doesn't, we'll initialize it when starting
                socketio.emit('status', {
                    'message': 'Ready to start chat',
                    'ready': True,
                    'chat_id': chat_id
                }, room=request.sid)
    
    @socketio.on('start_chat')
    def handle_start_chat(data):
        """Start or resume a chat session"""
        chat_id = data.get('chat_id')
        if not chat_id:
            socketio.emit('error', {'message': 'No chat ID provided'}, room=request.sid)
            return

        # Check if the stage already exists in memory
        if chat_id in active_stages:
            stage = active_stages[chat_id]
            
            # If story is already completed, just notify
            if stage.story_completed:
                socketio.emit('objective_status', {
                    'completed': True,
                    'story_completed': True,
                    'index': stage.current_objective_index,
                    'total': len(stage.plot_objectives),
                    'message': 'Story is already complete.'
                }, room=chat_id)
                return
                
            # If already processing, don't start again
            if stage.is_processing:
                socketio.emit('status', {'message': 'Already processing'}, room=chat_id)
                return
                
            # Resume existing session
            def resume_chat():
                stage.advance_turn()
                
            thread = threading.Thread(target=resume_chat)
            thread.daemon = True
            thread.start()
            
            return
            
        # If stage doesn't exist in memory, initialize it from database
        try:
            # Create new stage instance using chat_id
            stage = Stage(chat_id=chat_id, socketio=socketio)
            
            # Check if already completed (based on database)
            if stage.story_completed:
                socketio.emit('objective_status', {
                    'completed': True,
                    'story_completed': True,
                    'index': stage.current_objective_index,
                    'total': len(stage.plot_objectives),
                    'message': 'Story is already complete.'
                }, room=chat_id)
                return
            
            # Cache the stage in memory for performance
            active_stages[chat_id] = stage
            
            # Start the stage sequence in a background thread
            def start_sequence():
                # Start the first turn
                stage.advance_turn()
                
            thread = threading.Thread(target=start_sequence)
            thread.daemon = True
            thread.start()
            
            socketio.emit('status', {
                'message': 'Chat started',
                'started': True
            }, room=chat_id)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            socketio.emit('error', {'message': f'Error starting chat: {str(e)}'}, room=chat_id)
    
    @socketio.on('player_input')
    def handle_player_input(data):
        """Handle player input/interruption"""
        chat_id = data.get('chat_id')
        player_input = data.get('input')
        
        if not chat_id or not player_input:
            socketio.emit('error', {'message': 'Missing chat ID or player input'}, room=request.sid)
            return
            
        # Get or initialize the stage
        stage = None
        
        # Check if the stage exists in memory first
        if chat_id in active_stages:
            stage = active_stages[chat_id]
        else:
            # Try to initialize the stage from database
            try:
                # Create the stage with the chat_id
                stage = Stage(chat_id=chat_id, socketio=socketio)
                active_stages[chat_id] = stage
            except Exception as e:
                socketio.emit('error', {
                    'message': f'Error initializing chat: {str(e)}',
                    'code': 'chat_not_initialized'
                }, room=request.sid)
                return
            
        # Check if already processing
        if stage.is_processing:
            socketio.emit('status', {'message': 'Already processing. Please wait.'}, room=chat_id)
            return
            
        # Check if story is completed
        if stage.story_completed:
            socketio.emit('status', {'message': 'Story is already complete.'}, room=chat_id)
            return
            
        # Process player input in a background thread
        def process_input():
            stage.player_interrupt(player_input)
            
        thread = threading.Thread(target=process_input)
        thread.daemon = True
        thread.start()
        
        socketio.emit('status', {'message': 'Processing player input...'}, room=chat_id)
    
    @socketio.on('heartbeat')
    def handle_heartbeat():
        """Handle heartbeat to keep connection alive"""
        pass  # Just acknowledging the heartbeat is enough
        
    # Add a function to clean up memory - you can call this periodically 
    # if you're concerned about memory usage
    def cleanup_inactive_stages():
        """Remove stages that are completed or inactive from memory"""
        for chat_id in list(active_stages.keys()):
            stage = active_stages[chat_id]
            if stage.story_completed:
                del active_stages[chat_id]
                
    # You can expose this if needed
    socketio.cleanup_inactive_stages = cleanup_inactive_stages
 