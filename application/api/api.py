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
import schedule
import time

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
            show_id=episode.get('show_id'),
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


import time
import threading
import logging
from flask import request
from flask_socketio import join_room, leave_room
from application.database.db import db
from application.play.stage import Stage

# Configure logging
logger = logging.getLogger("SocketHandlers")

# In-memory cache of active stages with thread safety
active_stages = {}
active_stages_lock = threading.RLock()

def setup_socket_handlers(socketio):
    """Set up Socket.IO event handlers for chat interaction"""
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection and properly clean up all resources"""
        logger.info(f"Client disconnected: {request.sid}")
        
        try:
            # Find and stop any active stages associated with this client
            client_rooms = getattr(request, 'rooms', set())
            
            # Remove the client's own room
            if request.sid in client_rooms:
                client_rooms.remove(request.sid)
            
            # For each room (likely to be a chat_id) the client was in
            # Keep track of chats that were stopped
            stopped_chats = []
            
            for chat_id in client_rooms:
                with active_stages_lock:
                    if chat_id in active_stages:
                        try:
                            logger.info(f"Stopping stage for chat_id={chat_id} due to client disconnect")
                            # Call the stop method to properly terminate all operations
                            active_stages[chat_id].stop()
                            # Remove from active stages to free up resources
                            active_stages.pop(chat_id)
                            stopped_chats.append(chat_id)
                        except Exception as e:
                            logger.error(f"Error stopping stage for chat_id={chat_id}: {str(e)}", exc_info=True)
                            socketio.emit('error', {'message': f'Error stopping chat: {str(e)}'}, room=chat_id)
            
            # Notify all rooms about disconnection
            for chat_id in stopped_chats:
                socketio.emit('status', {
                    'message': 'Chat processing stopped as client disconnected'
                }, room=chat_id)
            
            # Remove the client from any rooms they may have been in
            leave_room(request.sid)
            
            logger.info(f"Client {request.sid} disconnected and cleaned up {len(stopped_chats)} chats")

        except Exception as e:
            logger.error(f"Error handling disconnect: {str(e)}", exc_info=True)
            
        # Force a cleanup of inactive stages to ensure memory is freed
        try:
            cleanup_inactive_stages()
        except Exception as e:
            logger.error(f"Error during forced cleanup: {str(e)}", exc_info=True)

    @socketio.on('leave_chat')
    def handle_leave_chat(data):
        """Handle explicit leave_chat event when user navigates away"""
        try:
            chat_id = data.get('chat_id')
            if not chat_id:
                socketio.emit('error', {'message': 'No chat ID provided'}, room=request.sid)
                return
            
            logger.info(f"Client {request.sid} explicitly leaving chat: {chat_id}")
            
            # Stop the stage immediately
            with active_stages_lock:
                if chat_id in active_stages:
                    logger.info(f"Stopping stage for chat_id={chat_id} due to explicit leave")
                    # Call the stop method to properly terminate all operations
                    active_stages[chat_id].stop()
                    # Remove from active stages
                    active_stages.pop(chat_id)
                    socketio.emit('status', {
                        'message': 'Chat processing stopped as you left the chat'
                    }, room=chat_id)
            
            # Leave the room
            leave_room(chat_id)
            logger.info(f"Client {request.sid} has left chat: {chat_id}")
            
        except Exception as e:
            logger.error(f"Error handling leave_chat: {str(e)}", exc_info=True)
            socketio.emit('error', {
                'message': f'Error leaving chat: {str(e)}',
                'code': 'leave_error'
            }, room=request.sid)

    @socketio.on('join_chat')
    def handle_join_chat(data):
        """Join a chat room and initialize if needed with thread safety"""
        try:
            chat_id = data.get('chat_id')
            if not chat_id:
                socketio.emit('error', {'message': 'No chat ID provided'}, room=request.sid)
                return
            
            logger.info(f"Client {request.sid} joining chat: {chat_id}")
                
            # Get the chat from database
            chat = db.get_chat(chat_id)
            if not chat:
                socketio.emit('error', {'message': 'Chat not found'}, room=request.sid)
                return
                
            # Join the Socket.IO room for this chat
            join_room(chat_id)
            
            # Use thread-safe access to active_stages
            stage = None
            create_new_stage = False
            
            with active_stages_lock:
                # Check if stage already exists in memory
                if chat_id in active_stages:
                    logger.debug(f"Using existing stage for chat_id: {chat_id}")
                    stage = active_stages[chat_id]
                else:
                    # Get the completed status from the chat data
                    is_completed = chat.get('story_completed', False) or chat.get('completed', False)
                    
                    if is_completed:
                        socketio.emit('objective_status', {
                            'completed': True,
                            'story_completed': True,
                            'index': chat.get('current_objective_index', 0),
                            'total': len(chat.get('plot_objectives', [])),
                            'message': 'Story is already complete.'
                        }, room=request.sid)
                        return
                    
                    # Mark that we need to create a new stage (outside the lock)
                    create_new_stage = True

            # If we need to create a new stage, do it outside the lock to prevent
            # long operations with the lock held
            if create_new_stage:
                try:
                    logger.info(f"Creating new stage for chat_id: {chat_id}")
                    stage = Stage(chat_id=chat_id, socketio=socketio)
                    
                    # Now store it in the dictionary with the lock
                    with active_stages_lock:
                        # Double-check that another thread didn't create it while we were working
                        if chat_id not in active_stages:
                            active_stages[chat_id] = stage
                        else:
                            # Another thread created it first, use that one and discard ours
                            logger.warning(f"Another thread created stage for {chat_id}, using that one")
                            stage = active_stages[chat_id]
                    
                    # Only one thread should trigger the stage sequence
                    if stage == active_stages[chat_id]:
                        logger.info(f"Starting sequence for chat_id: {chat_id}")
                        
                        # Run the stage in thread
                        def run_stage():
                            try:
                                stage.run_sequence()
                            except Exception as e:
                                logger.error(f"Error running stage: {str(e)}", exc_info=True)
                                socketio.emit('error', {
                                    'message': f'Error running stage: {str(e)}',
                                    'code': 'stage_run_error'
                                }, room=chat_id)
                                with stage.processing_lock:
                                    stage.is_processing = False
                        
                        thread = threading.Thread(target=run_stage)
                        thread.daemon = True
                        thread.start()
                    
                except Exception as e:
                    logger.error(f"Error creating stage: {str(e)}", exc_info=True)
                    socketio.emit('error', {
                        'message': f'Error creating stage: {str(e)}',
                        'code': 'stage_creation_error'
                    }, room=request.sid)
                    return
            
            # Send the current objective info
            if stage:
                current_obj = stage.current_objective()
                socketio.emit('objective_status', {
                    'story_completed': stage.story_completed,
                    'index': stage.current_objective_index,
                    'current': current_obj,
                    'total': len(stage.plot_objectives)
                }, room=request.sid)
            
        except Exception as e:
            logger.error(f"Error joining chat: {str(e)}", exc_info=True)
            socketio.emit('error', {
                'message': f'Error joining chat: {str(e)}',
                'code': 'join_error'
            }, room=request.sid)

    
    @socketio.on('player_input')
    def handle_player_input(data):
        """Handle player input/interruption with thread safety"""
        try:
            chat_id = data.get('chat_id')
            player_input = data.get('input')
            
            if not chat_id or not player_input:
                socketio.emit('error', {'message': 'Missing chat ID or player input'}, room=request.sid)
                return
            
            logger.info(f"Player input for chat_id {chat_id}: {player_input[:50]}...")
            
            # Get or initialize the stage with proper locking
            stage = None
            create_new_stage = False
            
            with active_stages_lock:
                # Check if the stage exists in memory first
                if chat_id in active_stages:
                    stage = active_stages[chat_id]
                else:
                    create_new_stage = True
            
            # If we need to create a new stage, do it outside the lock
            if create_new_stage:
                try:
                    # Create the stage with the chat_id
                    logger.info(f"Creating new stage for player input in chat_id: {chat_id}")
                    stage = Stage(chat_id=chat_id, socketio=socketio)
                    
                    # Store it with proper locking
                    with active_stages_lock:
                        if chat_id not in active_stages:
                            active_stages[chat_id] = stage
                        else:
                            # Another thread created it, use that one
                            stage = active_stages[chat_id]
                except Exception as e:
                    logger.error(f"Error initializing chat: {str(e)}", exc_info=True)
                    socketio.emit('error', {
                        'message': f'Error initializing chat: {str(e)}',
                        'code': 'chat_not_initialized'
                    }, room=request.sid)
                    return
            
            # Now we have a valid stage, check state
            with stage.processing_lock:
                # Check if story is completed
                if stage.story_completed:
                    socketio.emit('status', {'message': 'Story is already complete.'}, room=chat_id)
                    return
                
                # REMOVED: Don't check if already processing - always allow player interrupts
                # REMOVED: if stage.is_processing:
                # REMOVED:     socketio.emit('status', {'message': 'Already processing. Please wait.'}, room=chat_id)
                # REMOVED:     return
                    
                # Mark as processing to prevent others from interfering
                # This will be properly reset in player_interrupt if it was already processing
                stage.is_processing = True
            
            # Process player input in a background thread
            def process_input():
                try:
                    stage.player_interrupt(player_input)
                except Exception as e:
                    logger.error(f"Error processing player input: {str(e)}", exc_info=True)
                    socketio.emit('error', {
                        'message': f'Error processing player input: {str(e)}',
                        'code': 'input_error'
                    }, room=chat_id)
                finally:
                    with stage.processing_lock:
                        stage.is_processing = False
            
            thread = threading.Thread(target=process_input)
            thread.daemon = True
            thread.start()
            
            socketio.emit('status', {'message': 'Processing player input...'}, room=chat_id)
        except Exception as e:
            logger.error(f"Error handling player input: {str(e)}", exc_info=True)
            socketio.emit('error', {
                'message': f'Error handling player input: {str(e)}',
                'code': 'input_handler_error'
            }, room=request.sid)
    
    @socketio.on('heartbeat')
    def handle_heartbeat():
        """Handle heartbeat to keep connection alive"""
        pass  # Just acknowledging the heartbeat is enough
        
    def monitor_active_stages():
        """Check for stuck stages and attempt to reset them"""
        current_time = time.time()
        with active_stages_lock:
            for chat_id, stage in list(active_stages.items()):
                # Add a timestamp attribute to track when processing started
                if not hasattr(stage, 'processing_started_at'):
                    stage.processing_started_at = None
                    
                # If stage is processing for more than 5 minutes, it might be stuck
                if stage.is_processing and stage.processing_started_at and (current_time - stage.processing_started_at > 300):
                    logger.warning(f"Stage for chat_id {chat_id} appears stuck, resetting processing flag")
                    with stage.processing_lock:
                        stage.is_processing = False
                        stage.processing_started_at = None
                    socketio.emit('status', {'message': 'Processing was stuck and has been reset. You can continue now.'}, room=chat_id)
    
    def cleanup_inactive_stages():
        """Remove stages that are completed or inactive from memory"""
        with active_stages_lock:
            for chat_id in list(active_stages.keys()):
                stage = active_stages[chat_id]
                if stage.story_completed:
                    logger.info(f"Removing completed stage for chat_id: {chat_id}")
                    del active_stages[chat_id]
    
    # Patch the Stage class to track processing time
    original_stage_init = Stage.__init__
    
    def patched_stage_init(self, *args, **kwargs):
        original_stage_init(self, *args, **kwargs)
        self.processing_started_at = None
        self.original_set_processing = self.processing_lock.__enter__
        
        def set_processing_with_timestamp(*args, **kwargs):
            result = self.original_set_processing(*args, **kwargs)
            # After acquiring the lock, if we're setting is_processing to True, record the time
            if not hasattr(self, 'is_processing_before'):
                self.is_processing_before = self.is_processing
            if not self.is_processing_before and self.is_processing:
                self.processing_started_at = time.time()
            self.is_processing_before = self.is_processing
            return result
        
        self.processing_lock.__enter__ = set_processing_with_timestamp
    
    # Apply the monkey patch
    Stage.__init__ = patched_stage_init
    
    # Setup monitoring schedule
    import schedule
    
    def start_monitoring():
        """Start the monitoring function on a periodic schedule"""
        schedule.every(5).minutes.do(monitor_active_stages)
        schedule.every(30).minutes.do(cleanup_inactive_stages)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        logger.info("Stage monitoring scheduler started")
    
    # Start the monitoring
    start_monitoring()
    
    # Make cleanup function available to the application
    socketio.cleanup_inactive_stages = cleanup_inactive_stages
    socketio.monitor_active_stages = monitor_active_stages