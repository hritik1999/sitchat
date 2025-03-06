import json
import time
import threading
import logging
from typing import Dict, Optional, Any
from flask import request
from flask_socketio import join_room, leave_room

from application.database.db import db
from application.play.stage import Stage, StageState, StageError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StageManager:
    """
    Thread-safe manager for active stage instances.
    """
    
    def __init__(self):
        """Initialize the stage manager"""
        self._stages_lock = threading.RLock()
        self._active_stages: Dict[str, Stage] = {}
        self._client_sessions: Dict[str, set] = {}  # Maps client_id to set of chat_ids
        self._stage_clients: Dict[str, set] = {}  # Maps chat_id to set of client_ids
        
        # Start background maintenance thread
        self._maintenance_thread = threading.Thread(target=self._run_maintenance, daemon=True)
        self._maintenance_thread.start()
    
    def get_stage(self, chat_id: str, socketio=None) -> Optional[Stage]:
        """
        Get an existing stage or create a new one
        
        Parameters:
        chat_id: Chat ID to get stage for
        socketio: Socket.IO instance for new stages
        
        Returns:
        Optional[Stage]: The stage or None if not found/cannot be created
        """
        with self._stages_lock:
            # Check if stage already exists
            if chat_id in self._active_stages:
                stage = self._active_stages[chat_id]
                
                # Update socketio reference if provided and stage doesn't have one
                if socketio and not stage.socketio:
                    stage.socketio = socketio
                    logger.info(f"Updated socketio reference for existing stage {chat_id}")
                
                # Ensure the chat_id is properly set
                if stage.chat_id != chat_id:
                    logger.warning(f"Stage chat_id mismatch: {stage.chat_id} vs {chat_id}, fixing")
                    stage.chat_id = chat_id
                
                return stage
                
            # Stage doesn't exist, try to create it
            if socketio:
                try:
                    logger.info(f"Creating new stage for chat {chat_id}")
                    stage = Stage(chat_id=chat_id, socketio=socketio)
                    
                    # Verify the chat_id was properly set
                    if stage.chat_id != chat_id:
                        logger.warning(f"New stage chat_id mismatch: {stage.chat_id} vs {chat_id}, fixing")
                        stage.chat_id = chat_id
                    
                    self._active_stages[chat_id] = stage
                    self._stage_clients[chat_id] = set()
                    return stage
                except Exception as e:
                    logger.error(f"Error creating stage for chat {chat_id}: {str(e)}", exc_info=True)
                    return None
            
            logger.warning(f"Cannot create stage for {chat_id}: No socketio provided")
            return None
    
    def register_client(self, client_id: str, chat_id: str) -> None:
        """
        Register a client with a chat room
        
        Parameters:
        client_id: Client ID (socket session ID)
        chat_id: Chat ID the client is joining
        """
        with self._stages_lock:
            # Add chat to client's list
            if client_id not in self._client_sessions:
                self._client_sessions[client_id] = set()
            self._client_sessions[client_id].add(chat_id)
            
            # Add client to chat's list
            if chat_id not in self._stage_clients:
                self._stage_clients[chat_id] = set()
            self._stage_clients[chat_id].add(client_id)
    
    def unregister_client(self, client_id: str) -> list:
        """
        Unregister a client from all chats
        
        Parameters:
        client_id: Client ID to unregister
        
        Returns:
        list: List of chat_ids the client was in
        """
        with self._stages_lock:
            # Get all chats this client was in
            chat_ids = list(self._client_sessions.get(client_id, set()))
            
            # Remove client from chats
            for chat_id in chat_ids:
                if chat_id in self._stage_clients:
                    self._stage_clients[chat_id].discard(client_id)
            
            # Remove client's session entirely
            if client_id in self._client_sessions:
                del self._client_sessions[client_id]
            
            return chat_ids
    
    def get_active_clients(self, chat_id: str) -> int:
        """
        Get count of active clients in a chat
        
        Parameters:
        chat_id: Chat ID to check
        
        Returns:
        int: Number of active clients
        """
        with self._stages_lock:
            return len(self._stage_clients.get(chat_id, set()))
    
    def cleanup_inactive_stages(self, max_idle_time: int = 3600) -> int:
        """
        Remove stages that are completed or inactive from memory
        
        Parameters:
        max_idle_time: Maximum idle time in seconds before removing a stage
        
        Returns:
        int: Number of stages cleaned up
        """
        to_remove = []
        
        with self._stages_lock:
            current_time = time.time()
            
            for chat_id, stage in self._active_stages.items():
                # Check if stage is completed
                if stage.story_completed:
                    to_remove.append(chat_id)
                    continue
                
                # Check if no clients are connected
                if chat_id not in self._stage_clients or not self._stage_clients[chat_id]:
                    # Check last operation time
                    last_operation = getattr(stage, '_operation_timestamp', 0)
                    if current_time - last_operation > max_idle_time:
                        to_remove.append(chat_id)
            
            # Remove the identified stages
            for chat_id in to_remove:
                if chat_id in self._active_stages:
                    stage = self._active_stages[chat_id]
                    # Call cleanup to free resources
                    try:
                        stage.cleanup()
                    except Exception as e:
                        logger.error(f"Error cleaning up stage {chat_id}: {str(e)}")
                    
                    # Remove from dictionaries
                    del self._active_stages[chat_id]
                    if chat_id in self._stage_clients:
                        del self._stage_clients[chat_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} inactive stages")
        
        return len(to_remove)
    
    def reset_stuck_stages(self) -> int:
        """
        Reset stages that appear to be stuck in processing
        
        Returns:
        int: Number of stages reset
        """
        reset_count = 0
        
        with self._stages_lock:
            for chat_id, stage in self._active_stages.items():
                try:
                    if stage.reset_stuck_state():
                        reset_count += 1
                except Exception as e:
                    logger.error(f"Error resetting stage {chat_id}: {str(e)}")
        
        if reset_count:
            logger.info(f"Reset {reset_count} stuck stages")
        
        return reset_count
    
    def _run_maintenance(self) -> None:
        """Background thread for periodic maintenance tasks"""
        while True:
            try:
                # Clean up inactive stages every hour
                self.cleanup_inactive_stages()
                
                # Check for stuck stages every 5 minutes
                self.reset_stuck_stages()
            except Exception as e:
                logger.error(f"Error in maintenance thread: {str(e)}", exc_info=True)
            
            # Sleep for 5 minutes
            time.sleep(300)

# Create a singleton instance
stage_manager = StageManager()

def setup_socket_handlers(socketio):
    """Set up Socket.IO event handlers for chat interaction"""
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        client_id = request.sid
        logger.info(f"Client disconnected: {client_id}")
        
        # Get all chat rooms this client was in
        chat_ids = stage_manager.unregister_client(client_id)
        
        # For each room the client was in
        for chat_id in chat_ids:
            # Check if any clients are still in the room
            if stage_manager.get_active_clients(chat_id) == 0:
                # If no clients left, emit a status message to the room
                socketio.emit('status', {'message': 'Chat paused due to all clients disconnecting'}, room=chat_id)
                logger.info(f"All clients disconnected from chat {chat_id}")

    @socketio.on('join_chat')
    def handle_join_chat(data):
        """Join a chat room and initialize if needed"""
        client_id = request.sid
        
        # Log connection details
        logger.info(f"Client {client_id} attempting to join chat room")
        
        # Validate input
        chat_id = data.get('chat_id')
        if not chat_id:
            logger.warning(f"Client {client_id} provided no chat_id")
            socketio.emit('error', {'message': 'No chat ID provided'}, room=client_id)
            return
        
        logger.info(f"Client {client_id} joining chat {chat_id}")
        
        # Get the chat from database
        try:
            chat = db.get_chat(chat_id)
            if not chat:
                logger.warning(f"Chat {chat_id} not found for client {client_id}")
                socketio.emit('error', {'message': 'Chat not found'}, room=client_id)
                return
        except Exception as e:
            error_msg = f"Error fetching chat {chat_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            socketio.emit('error', {'message': error_msg}, room=client_id)
            return
        
        # Join the Socket.IO room for this chat
        try:
            join_room(chat_id)
            logger.info(f"Client {client_id} joined room {chat_id}")
            
            # Send confirmation
            socketio.emit('status', {
                'message': f'Joined chat room {chat_id}',
                'chat_id': chat_id
            }, room=client_id)
        except Exception as e:
            error_msg = f"Error joining room {chat_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            socketio.emit('error', {'message': error_msg}, room=client_id)
            return
        
        # Register client with chat
        stage_manager.register_client(client_id, chat_id)
        
        # Get chat messages directly from database with error handling
        try:
            messages = db.get_messages(chat_id)
            logger.info(f"Sending {len(messages)} historical messages to client {client_id}")
            
            # Send the chat history to the client
            for message in messages:
                # Add a small delay between messages to ensure proper ordering
                socketio.sleep(0.05)
                socketio.emit('dialogue', {
                    'role': message.get('role'),
                    'content': message.get('content'),
                    'type': message.get('type')
                }, room=client_id)
            
            logger.info(f"Finished sending historical messages to client {client_id}")
        except Exception as e:
            error_msg = f"Error loading messages for chat {chat_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            socketio.emit('error', {'message': error_msg}, room=client_id)
        
        # Get or initialize stage
        stage = stage_manager.get_stage(chat_id, socketio)
        
        if stage:
            # Check if story is completed
            if stage.story_completed:
                logger.info(f"Story already completed for chat {chat_id}")
                socketio.emit('objective_status', {
                    'completed': True,
                    'story_completed': True,
                    'index': stage.current_objective_index,
                    'total': len(stage.plot_objectives),
                    'message': 'Story is already complete.'
                }, room=client_id)
            else:
                # Send the current objective info
                current_obj = stage.current_objective()
                with stage._state_lock:
                    process_state = stage._state.name
                    logger.info(f"Chat {chat_id} current state: {process_state}, " +
                            f"objective {stage.current_objective_index}/{len(stage.plot_objectives)}")
                    
                    socketio.emit('status', {
                        'message': f'Current state: {process_state}',
                        'state': process_state
                    }, room=client_id)
                    
                    socketio.emit('objective_status', {
                        'completed': False,
                        'story_completed': False,
                        'index': stage.current_objective_index,
                        'current': current_obj,
                        'total': len(stage.plot_objectives)
                    }, room=client_id)
        else:
            logger.warning(f"Failed to get stage for chat {chat_id}")
            
            # Get the completed status from the chat data
            is_completed = chat.get('completed', False) or chat.get('story_completed', False)
            
            if is_completed:
                # Send completed status directly from database
                # We don't need to initialize the stage if it's already completed
                total_objectives = 0
                
                # Handle plot objectives parsing with error handling
                plot_objectives = chat.get('plot_objectives', [])
                if isinstance(plot_objectives, str):
                    try:
                        plot_objectives = json.loads(plot_objectives)
                    except json.JSONDecodeError:
                        plot_objectives = []
                
                total_objectives = len(plot_objectives)
                
                socketio.emit('objective_status', {
                    'completed': True,
                    'story_completed': True,
                    'index': chat.get('current_objective_index', 0),
                    'total': total_objectives,
                    'message': 'Story is already complete.'
                }, room=client_id)
            else:
                # If chat exists but stage doesn't, we'll initialize it when starting
                socketio.emit('status', {
                    'message': 'Ready to start chat',
                    'ready': True,
                    'chat_id': chat_id
                }, room=client_id)
        
        logger.info(f"Client {client_id} successfully joined chat {chat_id}")
    
    @socketio.on('start_chat')
    def handle_start_chat(data):
        """Start or resume a chat session"""
        client_id = request.sid
        
        # Validate input
        chat_id = data.get('chat_id')
        if not chat_id:
            socketio.emit('error', {'message': 'No chat ID provided'}, room=client_id)
            return
        
        # Get or initialize the stage
        stage = stage_manager.get_stage(chat_id, socketio)
        
        if not stage:
            error_msg = f"Could not initialize stage for chat {chat_id}"
            logger.error(error_msg)
            socketio.emit('error', {'message': error_msg}, room=client_id)
            return
        
        # Check if already completed
        if stage.story_completed:
            socketio.emit('objective_status', {
                'completed': True,
                'story_completed': True,
                'index': stage.current_objective_index,
                'total': len(stage.plot_objectives),
                'message': 'Story is already complete.'
            }, room=chat_id)
            return
        
        # Check current state
        with stage._state_lock:
            if stage._state == StageState.PROCESSING:
                socketio.emit('status', {'message': 'Already processing. Please wait.'}, room=chat_id)
                return
            elif stage._state != StageState.IDLE:
                socketio.emit('status', {
                    'message': f'Chat is in {stage._state.name} state. Cannot start.',
                    'state': stage._state.name
                }, room=chat_id)
                return
        
        # Start the stage in a background thread
        socketio.emit('status', {
            'message': 'Chat started',
            'started': True
        }, room=chat_id)
        
        def start_sequence():
            try:
                stage.advance_turn()
            except Exception as e:
                error_msg = f"Error starting chat sequence: {str(e)}"
                logger.error(error_msg, exc_info=True)
                socketio.emit('error', {'message': error_msg}, room=chat_id)
        
        # Use the stage's thread pool to run this
        Stage._thread_pool.submit(start_sequence)
        
        logger.info(f"Started chat {chat_id} for client {client_id}")
    
    @socketio.on('player_input')
    def handle_player_input(data):
        """Handle player input/interruption"""
        client_id = request.sid
        
        # Validate input
        chat_id = data.get('chat_id')
        player_input = data.get('input')
        
        if not chat_id:
            socketio.emit('error', {'message': 'Missing chat ID'}, room=client_id)
            return
        
        if not player_input or not player_input.strip():
            socketio.emit('error', {'message': 'Empty player input'}, room=client_id)
            return
        
        # Get or initialize the stage
        stage = stage_manager.get_stage(chat_id, socketio)
        
        if not stage:
            error_msg = f"Could not initialize stage for chat {chat_id}"
            logger.error(error_msg)
            socketio.emit('error', {
                'message': error_msg,
                'code': 'chat_not_initialized'
            }, room=client_id)
            return
        
        # Check if already completed
        if stage.story_completed:
            socketio.emit('status', {'message': 'Story is already complete.'}, room=chat_id)
            return
        
        # Check current state
        with stage._state_lock:
            if stage._state == StageState.PROCESSING:
                socketio.emit('status', {'message': 'Already processing. Please wait.'}, room=chat_id)
                return
            elif stage._state != StageState.IDLE:
                socketio.emit('status', {
                    'message': f'Chat is in {stage._state.name} state. Cannot process input.',
                    'state': stage._state.name
                }, room=chat_id)
                return
        
        # Process player input in the stage's thread pool
        socketio.emit('status', {'message': 'Processing player input...'}, room=chat_id)
        
        def process_input():
            try:
                result = stage.player_interrupt(player_input)
                if result.get('status') != 'success':
                    logger.warning(f"Player input processing returned: {result.get('status')} - {result.get('message')}")
            except Exception as e:
                error_msg = f"Error processing player input: {str(e)}"
                logger.error(error_msg, exc_info=True)
                socketio.emit('error', {'message': error_msg}, room=chat_id)
        
        # Use the stage's thread pool to run this
        Stage._thread_pool.submit(process_input)
        
        logger.info(f"Processing player input for chat {chat_id}, client {client_id}")
    
    @socketio.on('heartbeat')
    def handle_heartbeat():
        """Handle heartbeat to keep connection alive"""
        # Just acknowledge the heartbeat
        pass
    
    # Add the stage manager to socketio for use in other parts of the application
    socketio.stage_manager = stage_manager