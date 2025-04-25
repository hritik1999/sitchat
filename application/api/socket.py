import time, threading, logging, schedule
from flask import request
from flask_socketio import join_room, leave_room
from application.database.db import db
from application.play.stage import Stage

logger = logging.getLogger("SocketHandlers")
active_stages = {}
active_stages_lock = threading.RLock()

def setup_socket_handlers(socketio):
    """Set up Socket.IO event handlers for chat interaction"""
    # Patch Stage class to track processing time
    original_init = Stage.__init__
    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.processing_started_at = None
        self.is_processing_before = False
        def update_timestamp(name, value):
            if name == 'is_processing' and not self.is_processing_before and value:
                self.processing_started_at = time.time()
                self.is_processing_before = value
        self.__setattr__ = update_timestamp if not hasattr(self, '__setattr__') else update_timestamp
    Stage.__init__ = patched_init
    
    # Start monitoring for stuck processes
    def run_scheduler():
        schedule.every(5).minutes.do(lambda: monitor_active_stages(socketio))
        schedule.every(30).minutes.do(cleanup_inactive_stages)
        while True:
            schedule.run_pending()
            time.sleep(60)
    threading.Thread(target=run_scheduler, daemon=True).start()
    logger.info("Stage monitoring started")
    socketio.cleanup_inactive_stages = cleanup_inactive_stages
    socketio.monitor_active_stages = lambda: monitor_active_stages(socketio)

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info(f"Client disconnected: {request.sid}")
        try:
            client_rooms = getattr(request, 'rooms', set())
            if request.sid in client_rooms: client_rooms.remove(request.sid)
            stopped_chats = []
            for chat_id in client_rooms:
                with active_stages_lock:
                    if chat_id in active_stages:
                        try:
                            logger.info(f"Stopping stage for chat_id={chat_id}")
                            active_stages[chat_id]._cancel_all_operations()
                            active_stages.pop(chat_id)
                            stopped_chats.append(chat_id)
                        except Exception as e:
                            logger.error(f"Error stopping stage: {str(e)}", exc_info=True)
                            socketio.emit('error', {'message': f'Error stopping chat: {str(e)}'}, room=chat_id)
            for chat_id in stopped_chats:
                socketio.emit('status', {'message': 'Chat stopped as client disconnected'}, room=chat_id)
            leave_room(request.sid)
            logger.info(f"Client {request.sid} disconnected, cleaned up {len(stopped_chats)} chats")
        except Exception as e:
            logger.error(f"Disconnect error: {str(e)}", exc_info=True)
        try: cleanup_inactive_stages()
        except Exception as e: logger.error(f"Cleanup error: {str(e)}", exc_info=True)

    @socketio.on('leave_chat')
    def handle_leave_chat(data):
        """Handle explicit leave_chat event"""
        try:
            chat_id = data.get('chat_id')
            if not chat_id:
                socketio.emit('error', {'message': 'No chat ID provided'}, room=request.sid)
                return
            logger.info(f"Client {request.sid} leaving chat: {chat_id}")
            with active_stages_lock:
                if chat_id in active_stages:
                    logger.info(f"Stopping stage for chat_id={chat_id}")
                    active_stages[chat_id]._cancel_all_operations()
                    active_stages.pop(chat_id)
                    socketio.emit('status', {'message': 'Chat stopped as you left'}, room=chat_id)
            leave_room(chat_id)
        except Exception as e:
            logger.error(f"Leave error: {str(e)}", exc_info=True)
            socketio.emit('error', {'message': f'Error leaving chat: {str(e)}', 'code': 'leave_error'}, room=request.sid)

    @socketio.on('join_chat')
    def handle_join_chat(data):
        """Join a chat room and initialize if needed"""
        try:
            chat_id = data.get('chat_id')
            if not chat_id:
                socketio.emit('error', {'message': 'No chat ID provided'}, room=request.sid)
                return
            logger.info(f"Client {request.sid} joining chat: {chat_id}")
            chat = db.get_chat(chat_id)
            if not chat:
                socketio.emit('error', {'message': 'Chat not found'}, room=request.sid)
                return
            join_room(chat_id)
            
            stage = None
            create_new_stage = False
            with active_stages_lock:
                if chat_id in active_stages:
                    stage = active_stages[chat_id]
                else:
                    is_completed = chat.get('story_completed', False) or chat.get('completed', False)
                    if is_completed:
                        socketio.emit('objective_status', {
                            'completed': True, 'story_completed': True,
                            'index': chat.get('current_objective_index', 0),
                            'total': len(chat.get('plot_objectives', [])),
                            'message': 'Story is already complete.'
                        }, room=request.sid)
                        return
                    create_new_stage = True

            if create_new_stage:
                try:
                    logger.info(f"Creating new stage for chat_id: {chat_id}")
                    stage = Stage(chat_id=chat_id, socketio=socketio)
                    with active_stages_lock:
                        if chat_id not in active_stages:
                            active_stages[chat_id] = stage
                        else:
                            stage = active_stages[chat_id]
                    
                    if stage == active_stages[chat_id]:
                        logger.info(f"Starting sequence for chat_id: {chat_id}")
                        def run_stage():
                            try: stage.trigger_next_turn()
                            except Exception as e:
                                logger.error(f"Stage error: {str(e)}", exc_info=True)
                                socketio.emit('error', {'message': f'Error: {str(e)}', 'code': 'stage_error'}, room=chat_id)
                                stage.is_processing = False
                        threading.Thread(target=run_stage, daemon=True).start()
                except Exception as e:
                    logger.error(f"Stage creation error: {str(e)}", exc_info=True)
                    socketio.emit('error', {'message': f'Error: {str(e)}', 'code': 'stage_error'}, room=request.sid)
                    return
            
            if stage:
                try: current_obj = stage.plot_objectives[stage.current_objective_index]
                except IndexError: current_obj = None
                socketio.emit('objective_status', {
                    'story_completed': stage.story_completed,
                    'index': stage.current_objective_index,
                    'current': current_obj,
                    'total': len(stage.plot_objectives)
                }, room=request.sid)
        except Exception as e:
            logger.error(f"Join error: {str(e)}", exc_info=True)
            socketio.emit('error', {'message': f'Error: {str(e)}', 'code': 'join_error'}, room=request.sid)

    @socketio.on('player_input')
    def handle_player_input(data):
        """Handle player input/interruption"""
        try:
            chat_id, player_input = data.get('chat_id'), data.get('input')
            if not chat_id or not player_input:
                socketio.emit('error', {'message': 'Missing chat ID or input'}, room=request.sid)
                return
            logger.info(f"Player input for chat {chat_id}: {player_input[:50]}...")
            
            # Get or create stage
            stage = None
            with active_stages_lock:
                if chat_id in active_stages:
                    stage = active_stages[chat_id]
                else:
                    try:
                        stage = Stage(chat_id=chat_id, socketio=socketio)
                        active_stages[chat_id] = stage
                    except Exception as e:
                        logger.error(f"Init error: {str(e)}", exc_info=True)
                        socketio.emit('error', {'message': f'Error: {str(e)}', 'code': 'init_error'}, room=request.sid)
                        return
            
            if stage.story_completed:
                socketio.emit('status', {'message': 'Story already complete'}, room=chat_id)
                return
                
            stage.is_processing = True
            def process_input():
                try: stage.player_interrupt(player_input)
                except Exception as e:
                    logger.error(f"Input error: {str(e)}", exc_info=True)
                    socketio.emit('error', {'message': f'Error: {str(e)}', 'code': 'input_error'}, room=chat_id)
                finally: stage.is_processing = False
            
            threading.Thread(target=process_input, daemon=True).start()
            socketio.emit('status', {'message': 'Processing input...'}, room=chat_id)
        except Exception as e:
            logger.error(f"Input handler error: {str(e)}", exc_info=True)
            socketio.emit('error', {'message': f'Error: {str(e)}'}, room=request.sid)
    
    @socketio.on('heartbeat')
    def handle_heartbeat(): pass

def monitor_active_stages(socketio):
    """Check for stuck stages and reset them"""
    current_time = time.time()
    with active_stages_lock:
        for chat_id, stage in list(active_stages.items()):
            if not hasattr(stage, 'processing_started_at'): stage.processing_started_at = None
            if stage.is_processing and stage.processing_started_at and (current_time - stage.processing_started_at > 300):
                stage.is_processing = False
                stage.processing_started_at = None
                socketio.emit('status', {'message': 'Processing reset. You can continue now.'}, room=chat_id)

def cleanup_inactive_stages():
    """Remove completed stages from memory"""
    with active_stages_lock:
        for chat_id in list(active_stages.keys()):
            if active_stages[chat_id].story_completed:
                logger.info(f"Removing completed stage for chat_id: {chat_id}")
                del active_stages[chat_id]