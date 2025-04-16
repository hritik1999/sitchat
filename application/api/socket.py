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