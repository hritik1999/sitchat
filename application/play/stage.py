import json
import re
import time
import threading
from threading import Timer
import logging
import traceback
from contextlib import contextmanager
from application.database.db import db
from application.play.player import Player
from application.play.actor import Actor
from application.play.director import Director
from application.ai.llm import actor_llm, director_llm
import math
# Set root logger to WARNING level to suppress most library logs
logging.basicConfig(
    level=logging.WARNING,  # This makes all loggers use WARNING by default
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create specific logger for Stage with its own level and handlers
logger = logging.getLogger("Stage")
logger.setLevel(logging.WARNING)  # Only Stage logs will show at DEBUG level

# Clear any existing handlers to avoid duplicates
if logger.handlers:
    logger.handlers.clear()

# Add file handler
file_handler = logging.FileHandler("stage.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Make sure this logger doesn't propagate to root
logger.propagate = False

class Stage:
    def __init__(self, actors=None, director=None, socketio=None, chat_id=None):
        """Initialize a Stage with actors/director or load from database with chat_id"""
        logger.info(f"Initializing Stage with chat_id={chat_id}")
        
        self.socketio = socketio
        self.dialogue_history = []
        self.is_processing = False
        
        # Multiple locks for different resources to prevent deadlocks
        self.processing_lock = threading.RLock()  # Use RLock to allow reentrant locking
        self.dialogue_lock = threading.RLock()    # Lock for dialogue history
        self.state_lock = threading.RLock()       # Lock for state changes
        self.db_lock = threading.RLock()          # Lock for database operations
        
        self.story_completed = False
        self.full_chat = ''
        self.chat_id = None
        self.operation_timeouts = {}  # Track operation timeouts
        
        # Default timeout values (seconds)
        self.DEFAULT_TIMEOUT = 120  # 2 minutes
        
        if chat_id:
            try:
                self._load_from_database(chat_id)
            except Exception as e:
                logger.error(f"Error loading from database: {str(e)}", exc_info=True)
                self.emit_event('error', {"message": f"Error loading chat: {str(e)}"})
                raise
        else:
            self._init_with_objects(actors, director)
    
    @contextmanager
    def timed_operation(self, operation_name, timeout=None):
        """Context manager to handle operation timeouts"""
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT
            
        try:
            self.operation_timeouts[operation_name] = {
                'start_time': time.time(),
                'timeout': timeout
            }
            yield
        except Exception as e:
            logger.error(f"Error in {operation_name}: {str(e)}", exc_info=True)
            raise
        finally:
            elapsed = time.time() - self.operation_timeouts[operation_name]['start_time']
            if elapsed > timeout:
                logger.warning(f"Operation {operation_name} took {elapsed:.2f}s, exceeded timeout of {timeout}s")
            else:
                logger.debug(f"Operation {operation_name} completed in {elapsed:.2f}s")
            self.operation_timeouts.pop(operation_name, None)
    
    def _load_from_database(self, chat_id):
        """Load stage data from database with error handling"""
        logger.info(f"Loading stage data from database for chat_id={chat_id}")
        
        with self.timed_operation("load_from_database"):
            with self.db_lock:
                self.chat_id = chat_id
                chat_data = db.get_chat(chat_id)
                
                if not chat_data:
                    error_msg = f"Chat with ID {chat_id} not found in database"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # Load basic chat data
                with self.state_lock:
                    self.current_objective_index = chat_data.get('current_objective_index', 0)
                    self.plot_failure_reason = chat_data.get('plot_failure_reason', '')
                    self.context = chat_data.get('context', '')
                    self.chat_summary = chat_data.get('chat_summary', '')
                    self.last_script_data = chat_data.get('last_script_data', None)
                    self.last_outline = chat_data.get('last_outline', None)
                    self.full_chat = chat_data.get('full_chat', '')
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
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # Parse plot objectives
                self.plot_objectives = self._parse_json_field(episode_data.get('plot_objectives', '[]'))
                background = episode_data.get('background', '')
                
                # Load show data
                show_id = episode_data.get('show_id')
                show_data = db.get_show(show_id)
                
                if not show_data:
                    error_msg = f"Show with ID {show_id} not found in database"
                    logger.error(error_msg)
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
                self.load_messages_from_db()
                logger.info(f"Successfully loaded stage for chat_id={chat_id}")
    
    def _init_with_objects(self, actors, director):
        """Initialize with provided objects"""
        logger.info("Initializing stage with provided objects")
        
        with self.state_lock:
            self.actors = actors
            self.director = director
            self.player = None
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
            logger.warning(f"Error parsing JSON field: {str(e)}")
            return []

    def save_state_to_db(self):
        """Save current state to database with error handling"""
        if not self.chat_id:
            logger.warning("Cannot save state: no chat_id provided")
            self.emit_event('error', {"message": "Cannot save state: no chat_id provided"})
            return False
        
        with self.timed_operation("save_state_to_db"):
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
                    'full_chat': self.full_chat
                }
            
            try:
                with self.db_lock:
                    db.update_chat(self.chat_id, chat_data)
                logger.debug(f"Successfully saved state to database for chat_id={self.chat_id}")
                return True
            except Exception as e:
                error_msg = f"Error saving state: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.emit_event('error', {"message": error_msg})
                return False
            
    def load_messages_from_db(self):
        """Load messages from database into dialogue history with error handling"""
        if not self.chat_id:
            logger.warning("Cannot load messages: no chat_id provided")
            self.emit_event('error', {"message": "Cannot load messages: no chat_id provided"})
            return False
        
        with self.timed_operation("load_messages_from_db"):
            try:
                with self.db_lock:
                    messages = db.get_messages(self.chat_id)
                
                if not messages:
                    logger.info("No messages found in database")
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
                
                logger.info(f"Successfully loaded {len(messages)} messages from database")
                return True
                    
            except Exception as e:
                error_msg = f"Error loading messages: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.emit_event('error', {"message": error_msg})
                return False

    def add_to_chat_history(self, text):
        """Add text to chat history and save state with thread safety"""
        logger.debug(f"Adding to chat history: {text[:50]}...")
        
        with self.dialogue_lock:
            self.context = f"{self.context}\n{text}" if self.context else text
            self.full_chat = f"{self.full_chat}\n{text}" if self.full_chat else text
        
        if self.chat_id:
            self.save_state_to_db()

    def current_objective(self):
        """Get the current objective or None if all completed"""
        with self.state_lock:
            if self.current_objective_index < len(self.plot_objectives):
                return self.plot_objectives[self.current_objective_index]
            return None
    
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
    
    def check_objective_completion(self, check_result, current_obj):
        """Check if an objective is completed and handle the transition with thread safety"""
        logger.info(f"Checking objective completion: {current_obj}")
        
        objective_status = None
        is_completed = False
        
        try:
            # First check outside the lock to avoid unnecessary locking
            if not check_result.get("completed", False):
                logger.info(f"Quick check: Objective '{current_obj}' not completed")
            
            with self.state_lock:
                # Create a snapshot of current state to use outside the lock
                current_index = self.current_objective_index
                total_objectives = len(self.plot_objectives)
                
                if check_result.get("completed", False):
                    # Update objective index atomically
                    logger.info(f"Objective completed: {current_obj}")
                    self.current_objective_index += 1
                    self.plot_failure_reason = ''
                    
                    # Save state immediately after state change
                    if self.chat_id:
                        with self.db_lock:
                            try:
                                db.update_chat(self.chat_id, {'current_objective_index': self.current_objective_index})
                                logger.debug(f"Updated objective index in database to {self.current_objective_index}")
                            except Exception as e:
                                logger.error(f"Database error updating objective index: {str(e)}", exc_info=True)
                    
                    # Get next objective
                    next_objective = None
                    if self.current_objective_index < total_objectives:
                        next_objective = self.plot_objectives[self.current_objective_index]
                        logger.debug(f"Next objective: {next_objective}")
                    else:
                        logger.debug("No more objectives remaining")
                    
                    # Check if final objective
                    is_final = self.current_objective_index >= total_objectives
                    
                    # Create objective status
                    status_msg = f"Objective '{current_obj}' completed: {check_result.get('reason', '')}"
                    objective_status = {
                        "completed": True,
                        "message": status_msg,
                        "reason": check_result.get('reason', ''),
                        "index": self.current_objective_index,
                        "current": next_objective,
                        "total": total_objectives,
                        "story_completed": is_final
                    }
                    
                    is_completed = True
                    
                    # Handle story completion if final objective
                    if is_final:
                        logger.info("All objectives completed. Story complete.")
                        self.story_completed = True
                    
                else:
                    # Objective not completed
                    logger.info(f"Objective not completed: {current_obj}")
                    self.plot_failure_reason = 'Plot objective not met: ' + check_result.get('reason', '')
                    
                    status_msg = f"Objective '{current_obj}' not yet completed: {check_result.get('reason', '')}"
                    objective_status = {
                        "completed": False,
                        "message": status_msg,
                        "reason": check_result.get('reason', ''),
                        "index": current_index,
                        "current": current_obj,
                        "total": total_objectives,
                        "story_completed": False
                    }
                
                # Save complete state
                if self.chat_id:
                    self.save_state_to_db()
            
            # Emit events outside the lock to avoid potential deadlocks
            self.emit_event('objective_status', objective_status)
            
            # Handle story completion notification
            if is_completed and self.current_objective_index >= len(self.plot_objectives):
                self.emit_event('status', {"message": "All objectives completed. Story complete."})
                self.emit_event('objective_status', {
                    "completed": True,
                    "message": "All objectives have been completed! Story is finished.",
                    "index": self.current_objective_index,
                    "total": len(self.plot_objectives),
                    "final": True,
                    "story_completed": True
                })

            # Whether completed or not, schedule the next turn (unless story is complete)
            if not self.story_completed:
                if is_completed:
                    logger.info("Objective completed. Scheduling next turn with timer.")
                else:
                    logger.info("Objective not completed. Scheduling another attempt with timer.")
                    
                # Schedule next turn after a delay
                timer = threading.Timer(0.5, self.trigger_next_turn)
                timer.daemon = True
                timer.start()
                logger.debug(f"Scheduled next turn timer: {timer.name}")
        
            
            return is_completed, objective_status
            
        except Exception as e:
            error_msg = f"Error checking objective completion: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.emit_event('error', {"message": error_msg})
            return False, {"completed": False, "error": True, "message": str(e)}

    def process_director_script(self, script_json):
        """Process the script from director with typing indicators and thread safety"""
        logger.info("Processing director script")
        
        dialogue_lines = []
        messages_to_save = []
        
        with self.timed_operation("process_director_script"):
            # Parse the script first
            try:
                script_str = self._clean_json(script_json)
                script_data = json.loads(script_str)
            except json.JSONDecodeError as e:
                error_msg = f"Error parsing script JSON: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.emit_event('error', {"message": error_msg})
                script_data = {"scripts": []}
            
            # Process each line in the script with proper locks
            with self.dialogue_lock:
                sequence_count = len(self.dialogue_history)
                
                for line in script_data.get("scripts", []):
                    role = line.get("role", "")
                    instructions = line.get("instruction", "") or line.get("content", "")
                    
                    logger.debug(f"Processing script line for role: {role}")
                    
                    if role in self.actors:
                        # Handle actor dialogue
                        self.emit_event('typing_indicator', {"role": role, "status": "typing"})
                        try:
                            actor = self.actors[role]
                            # Release dialogue lock while waiting for actor reply
                            context_snapshot = self.context  # Create snapshot
                        except Exception as e:
                            logger.error(f"Error accessing actor '{role}': {str(e)}", exc_info=True)
                            self.emit_event('error', {"message": f"Error with actor {role}: {str(e)}"})
                            continue
                            
                        # Release the lock during the potentially long actor.reply
                        reply_output = None
                        try:
                            # Get actor reply without holding the lock
                            reply_output = actor.reply(context_snapshot, instructions)
                            time.sleep(math.floor(len(reply_output.split(' '))/4))
                            # Re-acquire lock to update dialogue
                            with self.dialogue_lock:
                                dialogue_line = f"{role}: {reply_output}"
                                self.context = f"{self.context}\n{dialogue_line}" if self.context else dialogue_line
                                self.full_chat = f"{self.full_chat}\n{dialogue_line}" if self.full_chat else dialogue_line
                                
                                dialogue_entry = {
                                    "role": role, 
                                    "content": reply_output, 
                                    "type": "actor_dialogue"
                                }
                                dialogue_lines.append(dialogue_entry)
                                
                                messages_to_save.append({
                                    "role": role,
                                    "content": reply_output,
                                    "type": "actor_dialogue",
                                    "sequence": sequence_count
                                })
                                sequence_count += 1
                        except Exception as e:
                            logger.error(f"Error getting reply from actor '{role}': {str(e)}", exc_info=True)
                            self.emit_event('error', {"message": f"Error with actor reply {role}: {str(e)}"})
                            continue
                            
                        self.emit_event('typing_indicator', {"role": role, "status": "idle"})
                        self.emit_event('dialogue', dialogue_entry)
                        
                    elif role.lower() == "narration":
                        # Handle narration
                        self.emit_event('typing_indicator', {"role": "Narration", "status": "typing"})
                        
                        content = line.get('content', instructions)
                        dialogue_line = f"Narration: {content}"
                        self.context = f"{self.context}\n{dialogue_line}" if self.context else dialogue_line
                        self.full_chat = f"{self.full_chat}\n{dialogue_line}" if self.full_chat else dialogue_line
                        
                        self.emit_event('typing_indicator', {"role": "Narration", "status": "idle"})
                        
                        dialogue_entry = {
                            "role": "Narration", 
                            "content": content, 
                            "type": "narration"
                        }
                        dialogue_lines.append(dialogue_entry)
                        
                        messages_to_save.append({
                            "role": "Narration",
                            "content": content,
                            "type": "narration",
                            "sequence": sequence_count
                        })
                        sequence_count += 1
                        
                        self.emit_event('dialogue', dialogue_entry)
                        
                    else:
                        # Handle other roles
                        self.emit_event('typing_indicator', {"role": role, "status": "typing"})
                        time.sleep(1)  # Small delay for realism
                        
                        dialogue_line = f"{role}: {instructions}"
                        self.context = f"{self.context}\n{dialogue_line}" if self.context else dialogue_line
                        self.full_chat = f"{self.full_chat}\n{dialogue_line}" if self.full_chat else dialogue_line
                        
                        self.emit_event('typing_indicator', {"role": role, "status": "idle"})
                        
                        dialogue_entry = {
                            "role": role, 
                            "content": instructions, 
                            "type": "other"
                        }
                        dialogue_lines.append(dialogue_entry)
                        
                        messages_to_save.append({
                            "role": role,
                            "content": instructions,
                            "type": "other",
                            "sequence": sequence_count
                        })
                        sequence_count += 1
                        
                        self.emit_event('dialogue', dialogue_entry)
                
                # Store dialogue history atomically 
                self.dialogue_history.extend(dialogue_lines)
            
            # Save to database outside of lock to prevent long lock times
            if self.chat_id and messages_to_save:
                try:
                    with self.db_lock:
                        db.add_messages_batch(self.chat_id, messages_to_save)
                except Exception as e:
                    error_msg = f"Error saving messages: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    self.emit_event('error', {"message": error_msg})
            
            if self.chat_id:
                self.save_state_to_db()
                
            logger.info(f"Processed {len(dialogue_lines)} dialogue lines from director script")
            return dialogue_lines

    def trigger_next_turn(self):
        """Trigger the next turn in a non-blocking way with proper thread safety"""
        logger.info("Triggering next turn")
        
        # Immediately check if we should proceed without acquiring the lock first
        # to avoid potential deadlocks
        if self.current_objective_index >= len(self.plot_objectives) or self.story_completed:
            logger.info("All objectives completed or story finished. Not triggering new turn.")
            return
            
        with self.processing_lock:
            if self.is_processing:
                logger.warning("Already processing a turn. Not triggering new turn.")
                return
                
            # Double-check after acquiring the lock
            if self.current_objective_index >= len(self.plot_objectives) or self.story_completed:
                logger.info("All objectives completed or story finished. Not triggering new turn.")
                return
                
            logger.debug("Setting processing flag to True")
            self.is_processing = True
        
        def run_turn():
            try:
                logger.debug("Starting background turn processing")
                self.advance_turn()
            except Exception as e:
                error_msg = f"Error in turn: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.emit_event('error', {"message": error_msg})
            finally:
                with self.processing_lock:
                    was_processing = self.is_processing
                    self.is_processing = False
                    logger.debug(f"Released processing lock. Was processing: {was_processing}")
        
        thread = threading.Thread(target=run_turn)
        thread.daemon = True
        thread.start()
        logger.debug(f"Started thread {thread.name} for next turn")

    def advance_turn(self):
        """Advance the game turn based on current objective with comprehensive error handling"""
        logger.info("Advancing turn")
        
        # Already checked in trigger_next_turn, but double-check for safety
        with self.processing_lock:
            if not self.is_processing:
                logger.warning("Not currently processing. Setting processing flag.")
                self.is_processing = True
        
        result = {"status": "unknown", "message": "Turn not completed", "dialogue": []}

        # Director generates outline and script
        self.emit_event('director_status', {"status": "directing", "message": "Director is directing..."})
        
        try:
            with self.timed_operation("advance_turn", timeout=300):  # 5 minute timeout
                with self.state_lock:
                    objective = self.current_objective()
                    if not objective:
                        logger.info("No current objective. Story complete.")
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
                
                # Get context snapshot to use outside locks
                with self.dialogue_lock:
                    context_snapshot = self.context
                    current_objective = objective  # Keep local reference
                    failure_reason = self.plot_failure_reason
                
                try:
                    self.emit_event('director_status', {"status": "directing", "message": "Analyzing story progress..."})
                    # Generate outline without holding locks
                    logger.debug(f"Generating outline for objective: {current_objective}")
                    outline_str = self.director.generate_outline(context_snapshot, current_objective, failure_reason)
                    
                    try:
                        outline = json.loads(self._clean_json(outline_str))
                        self.emit_event('director_status', {"status": "directing", "message": "Writing next scene..."})
                        
                        with self.state_lock:
                            self.last_outline = outline
                            self.chat_summary = outline.get('previous_outline', '')

                            # Reset context and update backgrounds
                            with self.dialogue_lock:
                                self.context = ''
                            
                            self.director.background = self.chat_summary
                            for actor_name in self.actors:
                                self.actors[actor_name].background = self.chat_summary
                                
                        new_outline = outline.get('new_outline', outline)
                        
                        # Generate turn instructions without holding locks
                        logger.debug("Generating turn instructions from outline")
                        with self.dialogue_lock:
                            latest_context = self.context  # Get fresh context

                        self.emit_event('director_status', {"status": "directing", "message": "Director is cueing the actors..."})
                        script_json = self.director.generate_turn_instructions(latest_context, new_outline)
                        
                        with self.state_lock:
                            self.last_script_data = script_json
                        
                        if self.chat_id:
                            self.save_state_to_db()
                        
                        # Process the director's script
                        logger.debug("Processing director script")
                        self.emit_event('director_status', {"status": "idle", "message": ""})
                        dialogue_lines = self.process_director_script(script_json)
                        
                    except json.JSONDecodeError as e:
                        error_msg = f"Error parsing outline JSON: {str(e)}"
                        logger.error(error_msg, exc_info=True)
                        self.emit_event('error', {"message": error_msg})
                        return {"status": "error", "message": error_msg, "dialogue": []}
                        
                except Exception as e:
                    error_msg = f"Error generating outline or script: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    self.emit_event('error', {"message": error_msg})
                    return {"status": "error", "message": error_msg, "dialogue": []}

                # Check objective completion
                logger.debug(f"Checking objective completion for: {current_objective}")
                with self.dialogue_lock:
                    full_chat_snapshot = self.full_chat
                
                try:
                    self.emit_event('director_status', {"status": "writing", "message": "Checking objective completion..."})
                    check_result_str = self.director.check_objective(full_chat_snapshot, current_objective)
                    self.emit_event('director_status', {"status": "idle", "message": ""})
                    check_result = json.loads(self._clean_json(check_result_str))
                    completed, objective_status = self.check_objective_completion(check_result, current_objective)
                    
                except Exception as e:
                    error_msg = f"Error checking objective: {str(e)}"
                    logger.error(error_msg, exc_info=True)
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
                if completed and self.current_objective_index < len(self.plot_objectives):
                    logger.info("Objective completed. Scheduling next turn with timer.")
                    # Schedule next turn after a short delay (100ms)
                    timer = threading.Timer(0.1, self.trigger_next_turn)
                    timer.daemon = True
                    timer.start()
                    logger.debug(f"Scheduled next turn timer: {timer.name}")
                
                return result
                
        except Exception as e:
            error_msg = f"Unexpected error in advance_turn: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.emit_event('error', {"message": error_msg})
            return {"status": "error", "message": error_msg, "dialogue": []}
        
        finally:
            with self.processing_lock:
                was_processing = self.is_processing
                self.is_processing = False
                logger.debug(f"advance_turn finished. Was processing: {was_processing}")

    def player_interrupt(self, player_input):
        """Handle player interruption with new input and proper thread safety"""
        logger.info(f"Player interrupt: {player_input[:50]}...")
        
        with self.processing_lock:
            if self.is_processing:
                logger.warning("Already processing. Cannot handle player interrupt.")
                self.emit_event('status', {"message": "Already processing. Please wait."})
                return {"status": "waiting", "message": "Already processing", "dialogue": []}
            
            if self.story_completed:
                logger.info("Story is already complete. Cannot handle player interrupt.")
                self.emit_event('status', {"message": "Story is already complete."})
                return {"status": "complete", "message": "Story already complete", "dialogue": []}
                
            self.is_processing = True
            
        result = {"status": "unknown", "message": "Interrupt not processed", "dialogue": []}
            
        try:
            with self.timed_operation("player_interrupt", timeout=300):  # 5 minute timeout
                self.emit_event('status', {"message": "Player interrupts"})
                
                # Add player input to history
                with self.dialogue_lock:
                    player_name = self.player.name
                    interrupt_line = f"{player_name}: {player_input}"
                    self.context = f"{self.context}\n{interrupt_line}" if self.context else interrupt_line
                    self.full_chat = f"{self.full_chat}\n{interrupt_line}" if self.full_chat else interrupt_line
                    
                    player_dialogue = {
                        "role": player_name,
                        "content": player_input,
                        "type": "player_input"
                    }
                    self.dialogue_history.append(player_dialogue)
                
                self.emit_event('dialogue', player_dialogue)
                
                # Save to database
                if self.chat_id:
                    with self.db_lock:
                        sequence = len(self.dialogue_history) - 1
                        try:
                            db.add_message(
                                self.chat_id,
                                player_name,
                                player_input,
                                "player_input",
                                sequence
                            )
                        except Exception as e:
                            error_msg = f"Error saving player message: {str(e)}"
                            logger.error(error_msg, exc_info=True)
                            self.emit_event('error', {"message": error_msg})
                    
                    self.save_state_to_db()
                
                # Generate new script
                self.emit_event('director_status', {"status": "directing", "message": "Director is directing..."})
                
                with self.state_lock:
                    current_obj = self.current_objective()
                    
                if not current_obj:
                    logger.info("No current objective. Story complete.")
                    with self.state_lock:
                        self.story_completed = True
                        if self.chat_id:
                            self.save_state_to_db()
                    self.emit_event('status', {"message": "No current objective."})
                    return {"status": "error", "message": "No current objective", "dialogue": []}
                
                try:
                    # Get context snapshot to use outside locks
                    with self.dialogue_lock:
                        context_snapshot = self.context
                        
                    # Generate outline without holding locks
                    logger.debug(f"Generating outline after player interrupt for objective: {current_obj}")
                    outline_str = self.director.generate_outline(context_snapshot, current_obj)
                    outline = json.loads(self._clean_json(outline_str))
                    
                    with self.state_lock:
                        self.last_outline = outline
                    
                    new_outline = outline.get('new_outline', outline)
                    
                    with self.dialogue_lock:
                        latest_context = self.context  # Get fresh context
                        
                    script_json = self.director.generate_turn_instructions(latest_context, new_outline)
                    
                    with self.state_lock:
                        self.last_script_data = script_json
                    
                    if self.chat_id:
                        self.save_state_to_db()
                    
                    self.emit_event('director_status', {"status": "idle", "message": ""})
                    
                    # Process the director's script
                    dialogue_lines = self.process_director_script(script_json)
                    
                except Exception as e:
                    error_msg = f"Error generating script after player interrupt: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    self.emit_event('error', {"message": error_msg})
                    return {"status": "error", "message": error_msg, "dialogue": []}
                
                # Check objective completion
                try:
                    with self.dialogue_lock:
                        full_chat_snapshot = self.full_chat
                        
                    check_result_str = self.director.check_objective(full_chat_snapshot, current_obj)
                    check_result = json.loads(self._clean_json(check_result_str))
                    completed, objective_status = self.check_objective_completion(check_result, current_obj)
                    
                except Exception as e:
                    error_msg = f"Error checking objective after player interrupt: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    self.emit_event('error', {"message": error_msg})
                
                result = {
                    "status": "success",
                    "dialogue": dialogue_lines,
                    "player_input": player_input
                }
                
                return result
                
        except Exception as e:
            error_msg = f"Unexpected error in player_interrupt: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.emit_event('error', {"message": error_msg})
            return {"status": "error", "message": error_msg, "dialogue": []}
            
        finally:
            with self.processing_lock:
                was_processing = self.is_processing
                self.is_processing = False
                logger.debug(f"player_interrupt finished. Was processing: {was_processing}")

    def get_state(self):
        """Get current state of the stage thread-safely"""
        logger.debug("Getting current stage state")
        
        with self.state_lock:
            completed = (self.current_objective_index >= len(self.plot_objectives) or self.story_completed)
            
            if self.current_objective_index >= len(self.plot_objectives):
                self.story_completed = True
                if self.chat_id:
                    self.save_state_to_db()
            
            current_objective = self.current_objective()
            total_objectives = len(self.plot_objectives)
            plot_failure_reason = self.plot_failure_reason
        
        with self.dialogue_lock:
            dialogue_history = list(self.dialogue_history)  # Create a copy
        
        return {
            "current_objective_index": self.current_objective_index,
            "total_objectives": total_objectives,
            "current_objective": current_objective,
            "plot_failure_reason": plot_failure_reason,
            "completed": completed,
            "story_completed": completed,
            "dialogue_history": dialogue_history,
            "is_processing": self.is_processing
        }
    
    def emit_event(self, event_type, data):
        """Emit an event through Socket.IO if available"""
        if self.socketio:
            try:
                self.socketio.emit(event_type, data, room=self.chat_id)
                logger.debug(f"Emitted {event_type} event: {str(data)[:100]}...")
            except Exception as e:
                logger.error(f"Error emitting {event_type} event: {str(e)}", exc_info=True)
            
    def run_sequence(self):
        """Run through the entire sequence of plot objectives"""
        logger.info("Starting story sequence")
        with self.processing_lock:
            if self.is_processing:
                logger.warning("Already processing. Cannot start sequence.")
                return {
                    "status": "error",
                    "message": "Already processing a turn"
                }
            self.is_processing = False  # Reset to ensure we can start
        
        # Use a timer to schedule the first turn after a small delay
        # This ensures any lock state changes have propagated
        logger.info("Scheduling first turn with timer")
        timer = Timer(0.1, self.trigger_next_turn)
        timer.daemon = True
        timer.start()
        
        return {
            "status": "started",
            "message": "Story sequence started"
        }