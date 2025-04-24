import json
import re
import time
import threading
from application.database.db import db
from application.play.player import Player
from application.play.actor import Actor
from application.play.director import Director
from application.ai.llm import actor_llm, director_llm
import math

class Stage:
    def __init__(self, actors=None, director=None, socketio=None, chat_id=None):
        """Initialize a Stage with actors/director or load from database with chat_id"""
        
        self.socketio = socketio
        self.dialogue_history = []
        self.is_processing = False
        
        # Multiple locks for different resources to prevent deadlocks
        self.processing_lock = threading.RLock()  # Use RLock to allow reentrant locking
        self.dialogue_lock = threading.RLock()    # Lock for dialogue history
        self.state_lock = threading.RLock()       # Lock for state changes
        self.db_lock = threading.RLock()          # Lock for database operations
        self.thread_lock = threading.RLock()      # Lock for thread management
        
        # Thread management and cancellation
        self.active_threads = {}                  # Track active threads by ID
        self.cancellation_event = threading.Event() # Event for signaling cancellation
        
        self.story_completed = False
        self.player_interrupted = False
        self.background = ''
        self.chat_id = None
        
        if chat_id:
            try:
                self._load_from_database(chat_id)
            except Exception as e:
                print('error loading from database:', e)
                self.emit_event('error', {"message": f"Error loading chat: {str(e)}"})
                raise
        else:
            with self.state_lock:
                self.actors = actors
                self.director = director
                self.player = None
                self.player_interrupted = False
                self.plot_objectives = []
                self.current_objective_index = 0
                self.context = ""
                self.plot_failure_reason = ''
                self.chat_summary = ''
                self.last_script_data = None
                self.last_outline = None

    def _parse_json_field(self, field):
        """Parse a potential JSON string field with error handling"""
        try:
            if isinstance(field, str):
                return json.loads(field)
            return field or []
        except json.JSONDecodeError as e:
            return []
    def _load_from_database(self, chat_id):
            """Load stage data from database with error handling"""
        
            with self.db_lock:
                self.chat_id = chat_id
                chat_data = db.get_chat(chat_id)
                
                if not chat_data:
                    error_msg = f"Chat with ID {chat_id} not found in database"
                    raise ValueError(error_msg)
                
                # Load basic chat data
                with self.state_lock:
                    self.current_objective_index = chat_data.get('current_objective_index', 0)
                    self.plot_failure_reason = chat_data.get('plot_failure_reason', '')
                    self.context = chat_data.get('context', '')
                    self.chat_summary = chat_data.get('chat_summary', '')
                    self.last_script_data = chat_data.get('last_script_data', None)
                    self.last_outline = chat_data.get('last_outline', None)
                    self.story_completed = chat_data.get('story_completed', False) or chat_data.get('completed', False)
                
                # Create player
                player_name = chat_data.get('player_name', 'Player')
                player_description = chat_data.get('player_description', '')
                self.player = Player(name=player_name, description=player_description)
                
                # Load episode data
                episode_id = chat_data.get('episode_id')
                episode_data = db.get_episode(episode_id)
                
                if not episode_data:
                    error_msg = f"Episode with ID {episode_id} not found in database"
                    raise ValueError(error_msg)
                
                # Parse plot objectives
                self.plot_objectives = self._parse_json_field(episode_data.get('plot_objectives', '[]'))
                background = episode_data.get('background', '')
                self.background = background
                # Load show data
                show_id = episode_data.get('show_id')
                show_data = db.get_show(show_id)
                
                if not show_data:
                    error_msg = f"Show with ID {show_id} not found in database"
                    raise ValueError(error_msg)
                
                self.show = show_data.get('name', '')
                self.description = show_data.get('description', '')
                
                # Parse characters
                characters = self._parse_json_field(show_data.get('characters', '[]'))
                relations = show_data.get('relations', '')
                
                # Create actors
                self.actors = {}
                for character in characters:
                    char_name = character.get('name') if isinstance(character, dict) else character.name
                    char_desc = character.get('description') if isinstance(character, dict) else character.description
                    
                    self.actors[char_name] = Actor(
                        char_name, char_desc, relations, background, actor_llm
                    )
                
                # Create director
                self.director = Director(
                    director_llm, self.show, self.description, 
                    background, self.actors, self.player, relations
                )
                
                # Load messages
                messages = db.get_messages(self.chat_id)
            
                if not messages:
                    return True
                
                with self.dialogue_lock:
                    self.dialogue_history = []
                    self.context = ""
                    
                    for msg in messages:
                        # Add to dialogue history
                        self.dialogue_history.append({
                            "role": msg['role'],
                            "content": msg['content'],
                            "type": msg['type']
                        })
                        
                        # Reconstruct context
                        if msg['type'] != 'system':
                            if msg['type'] == 'player_input':
                                line = f"{msg['role']}: {msg['content']}"
                            elif msg['type'] == 'narration':
                                line = f"Narration: {msg['content']}"
                            else:
                                line = f"{msg['role']}: {msg['content']}"
                                
                            self.context = f"{self.context}\n{line}" if self.context else line
    
    def _clean_json(self, json_str):
        """Clean JSON string by removing markdown and fixing common issues"""
        # Keep the original implementation as requested
        cleaned = json_str.strip()
        
        # Remove markdown fences
        if cleaned.startswith("```") and cleaned.endswith("```"):
            cleaned = cleaned.strip("```").strip()
            
        # Check for JSON prefix
        lines = cleaned.split("\n")
        if lines and lines[0].lower().startswith('json'):
            cleaned = "\n".join(lines[1:])
            
        # Remove trailing commas
        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)
        return cleaned
        
    def save_state_to_db(self):
        """Save current state to database with error handling"""
        if not self.chat_id:
            self.emit_event('error', {"message": "Cannot save state: no chat_id provided"})
            return False
        
        with self.state_lock:
            # Prepare data for save
            chat_data = {
                'current_objective_index': self.current_objective_index,
                'plot_failure_reason': self.plot_failure_reason,
                'context': self.context,
                'chat_summary': self.chat_summary,
                'last_script_data': self.last_script_data,
                'last_outline': self.last_outline,
                'story_completed': self.story_completed,
            }
        
        try:
            with self.db_lock:
                db.update_chat(self.chat_id, chat_data)
            return True
        except Exception as e:
            error_msg = f"Error saving state: {str(e)}"
            self.emit_event('error', {"message": error_msg})
            return False
        
    def emit_event(self, event_type, data):
        """Emit an event through Socket.IO if available"""
        if self.socketio:
            try:
                self.socketio.emit(event_type, data, room=self.chat_id)
            except Exception as e:
                error_msg = f"Error emitting event: {str(e)}"
                self.emit_event('error', {"message": error_msg})
        
    def process_director_script(self, script_json):
        """Process the script from director with typing indicators and thread safety"""
        dialogue_lines = []
        
        # Parse the script first
        try:
            script_str = self._clean_json(script_json)
            script_data = json.loads(script_str)
        except json.JSONDecodeError as e:
            error_msg = f"Error parsing script JSON: {str(e)}"
            self.emit_event('error', {"message": error_msg})
            script_data = {"scripts": []}
        
        # Process each line in the script with proper locks
        with self.dialogue_lock:
            sequence_count = len(self.dialogue_history)
            
            for line in script_data.get("scripts", []):
                # Check for cancellation before processing each line
                if self.cancellation_event.is_set():
                    return dialogue_lines
                
                role = line.get("role", "")
                instructions = line.get("instruction", "") or line.get("content", "")
                
                # Handle different role types
                if role == "Player" or (self.player and role == self.player.name):
                    # Handle player action prompt
                    player_action_data = {
                        "role": role,
                        "content": instructions,
                        "type": "player_prompt",
                        "wait_for_response": True
                    }
                    self.emit_event('player_action', player_action_data)
                    
                    # Wait for 10 seconds or until cancellation
                    wait_time = 10  # seconds
                    start_time = time.time()
                    
                    while time.time() - start_time < wait_time:
                        # Check for cancellation frequently
                        if self.cancellation_event.is_set():
                            return dialogue_lines
                        
                        # Sleep a short time to avoid CPU spin
                        time.sleep(0.1)
                
                elif role.lower() in [actor.name.lower() for actor in self.actors.values()]:
                    # Handle actor dialogue
                    self.emit_event('typing_indicator', {"role": role, "status": "typing"})
                    
                    try:
                        actor = self.actors[role]
                        # Release dialogue lock while waiting for actor reply
                        context_snapshot = self.context  # Create snapshot
                    except Exception as e:
                        actor = self.actors[role.lower()]
                        context_snapshot = self.context  # Create snapshot
                    
                    # Release the lock during the potentially long actor.reply
                    try:
                        # Check again for cancellation
                        if self.cancellation_event.is_set():
                            return dialogue_lines
                        
                        reply_output = actor.reply(context_snapshot, instructions)
                        
                        db.add_message(
                            chat_id=self.chat_id,
                            role=role,
                            content=reply_output,
                            type="actor_dialogue",
                            sequence=sequence_count
                        )
                        if self.context:
                            time.sleep(math.floor(len(reply_output.split(' '))/2))
                        else:
                            pass
                        
                        # Re-acquire lock to update dialogue
                        with self.dialogue_lock:
                            dialogue_line = f"{role}: {reply_output}"
                            self.dialogue_history.append(dialogue_line)
                            self.context = f"{self.context}\n{dialogue_line}" if self.context else dialogue_line
                            
                            dialogue_entry = {
                                "role": role, 
                                "content": reply_output, 
                                "type": "actor_dialogue"
                            }
                            dialogue_lines.append(dialogue_entry)
                            
                            sequence_count += 1
                    except Exception as e:
                        self.emit_event('error', {"message": f"Error with actor reply {role}: {str(e)}"})
                        continue
                    
                    self.emit_event('typing_indicator', {"role": role, "status": "idle"})
                    self.emit_event('dialogue', dialogue_entry)
                    
                elif role.lower() == "narration":
                    # Handle narration
                    self.emit_event('typing_indicator', {"role": "Narration", "status": "typing"})
                    
                    # Check for cancellation
                    if self.cancellation_event.is_set():
                        return dialogue_lines
                    
                    content = line.get('content', instructions)
                    dialogue_line = f"Narration: {content}"
                    self.dialogue_history.append(dialogue_line)
                    self.context = f"{self.context}\n{dialogue_line}" if self.context else dialogue_line
                    
                    self.emit_event('typing_indicator', {"role": "Narration", "status": "idle"})
                    
                    dialogue_entry = {
                        "role": "Narration", 
                        "content": content, 
                        "type": "narration"
                    }
                    dialogue_lines.append(dialogue_entry)
                    
                    db.add_message(
                        chat_id=self.chat_id,
                        role="Narration",
                        content=content,
                        type="narration",
                        sequence=sequence_count
                    )
                    
                    sequence_count += 1
                    self.emit_event('dialogue', dialogue_entry)
                    
                else:
                    # Handle other roles
                    self.emit_event('typing_indicator', {"role": role, "status": "typing"})
                    
                    # Check for cancellation
                    if self.cancellation_event.is_set():
                        return dialogue_lines
                    
                    actor = Actor(role, '', '', self.background, llm=actor_llm)
                    reply_output = actor.reply(self.context, instructions)
                    
                    if self.context:
                        time.sleep(math.floor(len(reply_output.split(' '))/2))
                    else:
                        pass
                    
                    dialogue_line = f"{role}: {reply_output}"
                    self.dialogue_history.append(dialogue_line)
                    self.context = f"{self.context}\n{dialogue_line}" if self.context else dialogue_line
                    
                    self.emit_event('typing_indicator', {"role": role, "status": "idle"})
                    
                    dialogue_entry = {
                        "role": role, 
                        "content": reply_output, 
                        "type": "other"
                    }
                    dialogue_lines.append(dialogue_entry)
                    
                    db.add_message(
                        chat_id=self.chat_id,
                        role=role,
                        content=reply_output,
                        type="other",
                        sequence=sequence_count
                    )
                    
                    sequence_count += 1
                    
                    self.emit_event('dialogue', dialogue_entry)
        
        if self.chat_id:
            self.save_state_to_db()
            
        return dialogue_lines
    
    # Improved _cancel_all_operations method with more aggressive cancellation
    def _cancel_all_operations(self):
        """Cancel all running operations with enhanced cleanup"""
        # Set cancellation event to signal all threads to stop
        self.cancellation_event.set()
        
        # Emit an immediate cancellation status
        self.emit_event('status', {"message": "Processing interrupted and stopped"})

        for role in list(self.actors.keys()):
            self.emit_event('typing_indicator', {"role": role, "status": "idle"})
        
        # Clear director status
        self.emit_event('director_status', {"status": "idle", "message": ""})
        
        # Signal status update
        self.emit_event('status', {"message": "Scene reset for player input"})


    def trigger_next_turn(self):
        """Trigger the next turn in a non-blocking way with proper thread safety"""
        if self.current_objective_index >= len(self.plot_objectives) or self.story_completed:
            self.emit_event('status', {"message": "Story completed"})
            return

        with self.processing_lock:
            if self.is_processing:
                return
            self.is_processing = True
            self.cancellation_event.clear()

        def execute_turn():
            current_thread_id = threading.current_thread().ident
            try:
                with self.thread_lock:
                    self.active_threads[current_thread_id] = {
                        'type': 'turn_thread',
                        'start_time': time.time()
                    }
                self.advance_turn()
            except Exception as error:
                self.emit_event('error', {"message": f"Error in turn: {str(error)}"})
            finally:
                with self.processing_lock:
                    self.is_processing = False
                with self.thread_lock:
                    self.active_threads.pop(current_thread_id, None)

        turn_thread = threading.Thread(target=execute_turn)
        turn_thread.daemon = True
        turn_thread.start()
            
    def advance_turn(self):
        """Advance the game turn based on current objective with comprehensive error handling"""
        current_thread_id = threading.current_thread().ident
        with self.thread_lock:
            if current_thread_id not in self.active_threads:
                self.active_threads[current_thread_id] = {
                    'type': 'advance_turn',
                    'start_time': time.time()
                }
        
        try:
            if self.cancellation_event.is_set():
                return {"status": "cancelled", "message": "Turn cancelled by player", "dialogue": []}
            
            self.emit_event('director_status', {"status": "directing", "message": "Director is directing..."})
            
            try:
                with self.state_lock:
                    if self.current_objective_index >= len(self.plot_objectives):
                        self.story_completed = True
                        if self.chat_id:
                            self.save_state_to_db()
                        self.emit_event('status', {"message": "No current objective. Story complete."})
                        self.emit_event('objective_status', {
                            "message": "All objectives have been completed! Story is finished.",
                            "index": self.current_objective_index,
                            "total": len(self.plot_objectives),
                            "final": True,
                            "story_completed": True
                        })
                        return {"status": "complete", "message": "Story complete", "dialogue": []}
                
                context_snapshot = self.context
                current_objective = self.plot_objectives[self.current_objective_index]
                
                # Check cancellation before outline generation
                if self.cancellation_event.is_set():
                    return {"status": "cancelled", "message": "Turn cancelled", "dialogue": []}
                
                # generate new outline only if the last objective was completed successfully else use the previous outline
                if not self.plot_failure_reason and not self.player_interrupted:
                    outline_str = self.director.generate_outline(context_snapshot, current_objective)
                    outline = json.loads(self._clean_json(outline_str))
                else:
                    outline = self.last_outline
                    self.player_interrupted = False
                
                # Check cancellation after outline generation
                if self.cancellation_event.is_set():
                    return {"status": "cancelled", "message": "Turn cancelled", "dialogue": []}
                
                self.emit_event('director_status', {"status": "directing", "message": "Director is writing next scene..."})
                
                with self.state_lock:
                    self.last_outline = outline
                    self.chat_summary = outline.get('previous_outline', '')
                    
                    # Reset context and update backgrounds if the previous objective was successful else keep using the previous one
                    with self.dialogue_lock:
                        if not self.plot_failure_reason:
                            self.context = ''
                            self.director.background = self.chat_summary
                            for actor_name in self.actors:
                                self.actors[actor_name].background = self.chat_summary
                        else:
                            self.context = self.context
                    
                # Check cancellation
                if self.cancellation_event.is_set():
                    return {"status": "cancelled", "message": "Turn cancelled", "dialogue": []}
                
                new_outline = outline.get('new_outline', outline)
                
                # Generate turn instructions without holding locks
                latest_context = self.context  # Get fresh context
                self.emit_event('director_status', {"status": "directing", "message": "Director is cueing the actors..."})
                script_json = self.director.generate_turn_instructions(latest_context, new_outline)
                
                # Check cancellation after script generation
                if self.cancellation_event.is_set():
                    return {"status": "cancelled", "message": "Turn cancelled", "dialogue": []}
                
                with self.state_lock:
                    self.last_script_data = script_json
                
                # Process the director's script
                self.emit_event('director_status', {"status": "idle", "message": ""})
                dialogue_lines = self.process_director_script(script_json)
                
                # Check cancellation after processing script
                if self.cancellation_event.is_set():
                    return {"status": "cancelled", "message": "Turn cancelled", "dialogue": []}
                
            except json.JSONDecodeError as e:
                error_msg = f"Error parsing outline JSON: {str(e)}"
                self.emit_event('error', {"message": error_msg})
                return {"status": "error", "message": error_msg, "dialogue": []}
                
            except Exception as e:
                error_msg = f"Error generating outline or script: {str(e)}"
                self.emit_event('error', {"message": error_msg})
                return {"status": "error", "message": error_msg, "dialogue": []}
            
            # Check objective completion
            context_snapshot = self.context
            try:
                self.emit_event('director_status', {"status": "directing", "message": "Checking objective completion..."})
                check_result_str = self.director.check_objective(context_snapshot, current_objective)
                self.emit_event('director_status', {"status": "idle", "message": ""})
                check_result = json.loads(self._clean_json(check_result_str))
                completed = check_result.get('completed', False)
                if completed:
                    self.plot_failure_reason = ''
                    self.current_objective_index += 1
                    self.story_completed = self.current_objective_index == len(self.plot_objectives)
                else:
                    self.plot_failure_reason = check_result.get('reason', '')
                objective_status = {
                    "completed": completed,
                    "reason": check_result.get('reason', ''),
                    "error": False,
                    "index": self.current_objective_index,
                    "total": len(self.plot_objectives),
                    "final": self.current_objective_index == len(self.plot_objectives),
                    "story_completed": self.story_completed
                }
                self.emit_event('objective_status', objective_status)
                self.save_state_to_db()
            except Exception as e:
                error_msg = f"Error checking objective: {str(e)}"
                self.emit_event('error', {"message": error_msg})
                objective_status = {
                    "completed": False,
                    "message": error_msg,
                    "error": True
                }
            
            result = {
                "status": "success",
                "dialogue": dialogue_lines,
                "objective": {
                    "current": current_objective,
                    "index": self.current_objective_index,
                    "total": len(self.plot_objectives),
                    "status": objective_status
                }
            }
            
            # Instead of triggering next turn directly, use a timer to schedule it after lock release
            if self.current_objective_index < len(self.plot_objectives):
                # Schedule next turn after a short delay (100ms)
                timer = threading.Timer(0.1, self.trigger_next_turn)
                timer.daemon = True
                timer.start()
            
            return result
        
        except Exception as e:
            error_msg = f"Unexpected error in advance_turn: {str(e)}"
            self.emit_event('error', {"message": error_msg})
            return {"status": "error", "message": error_msg, "dialogue": []}
        
        finally:
            with self.processing_lock:
                self.is_processing = False
            
            # Unregister thread if still registered
            with self.thread_lock:
                if current_thread_id in self.active_threads:
                    self.active_threads.pop(current_thread_id)

    def player_interrupt(self, player_input):
        """Handle player interruption with new input and proper thread safety"""

        self.emit_event('director_status', {'status':'directing',"message": "Director is resetting scene for player input..."})
        self._cancel_all_operations()

        with self.processing_lock:
            self.is_processing = False

        with self.dialogue_lock:
            current_context = self.context

        time.sleep(0.1)
        self.cancellation_event.clear()
        self.player_interrupted = True

        with self.processing_lock:
            self.is_processing = True

        try:
            self.emit_event('status', {"message": "Player interrupts"})

            with self.dialogue_lock:
                player_name = self.player.name
                player_dialogue = {
                    "role": player_name,
                    "content": player_input,
                    "type": "player_input"
                }
                interrupt_line = f"{player_name}: {player_input}"
                self.context = f"{current_context}\n{interrupt_line}" if current_context else interrupt_line
                self.dialogue_history.append(player_dialogue)

            if self.chat_id:
                with self.db_lock:
                    try:
                        db.add_message(self.chat_id, player_name, player_input, "player_input", len(self.dialogue_history) - 1)
                    except Exception as e:
                        self.emit_event('error', {"message": f"Error saving player message: {str(e)}"})
                self.save_state_to_db()

        except Exception as e:
            error_msg = f"Unexpected error in player_interrupt: {str(e)}"
            self.emit_event('error', {"message": error_msg})

        finally:
            with self.processing_lock:
                self.is_processing = False
            # Schedule next turn after a short delay (100ms)
            timer = threading.Timer(0.1, self.trigger_next_turn)
            timer.daemon = True
            timer.start()