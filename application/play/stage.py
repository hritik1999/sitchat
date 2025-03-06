import json
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto
import logging
from typing import Dict, List, Optional, Any, Tuple, Union

from application.database.db import db
from application.play.player import Player
from application.play.actor import Actor
from application.play.director import Director
from application.ai.llm import actor_llm, director_llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StageState(Enum):
    """Enum representing possible states of the Stage"""
    INITIALIZING = auto()
    IDLE = auto()
    PROCESSING = auto()
    FAILED = auto()
    COMPLETED = auto()

class StageError(Exception):
    """Base exception class for Stage-related errors"""
    pass

class DatabaseError(StageError):
    """Exception raised for database operation failures"""
    pass

class InitializationError(StageError):
    """Exception raised when Stage initialization fails"""
    pass

class ProcessingError(StageError):
    """Exception raised when processing operations fail"""
    pass

class Stage:
    """
    Thread-safe implementation of a Stage that manages actors, director, and story progression.
    """
    # Thread pool for background tasks (limiting concurrency)
    _thread_pool = ThreadPoolExecutor(max_workers=10)
    
    def __init__(self, actors=None, director=None, socketio=None, chat_id=None):
        """
        Initialize a Stage with either explicit actors/director or load from database with chat_id
        
        Parameters:
        actors: dict mapping actor names to Actor objects.
        director: a Director object (with check_objective method).
        socketio: Socket.IO instance for real-time communication.
        chat_id: Optional chat ID to load stage data from database
        
        Raises:
        InitializationError: If initialization fails (e.g., database error, invalid data)
        """
        # Initialize base attributes
        self.socketio = socketio
        self.dialogue_history = []
        self.full_chat = ''
        self.chat_id = None
        
        # Thread safety mechanisms
        self._state_lock = threading.RLock()  # Reentrant lock for state management
        self._state = StageState.INITIALIZING
        self._db_lock = threading.Lock()  # Lock for database operations
        
        # Operation tracking
        self._current_operation_id = None
        self._operation_timestamp = 0
        
        try:
            if chat_id:
                self._initialize_from_database(chat_id)
            else:
                self._initialize_new_stage(actors, director)
                
            # Set state to idle after successful initialization
            with self._state_lock:
                self._state = StageState.IDLE
                
        except Exception as e:
            # Set state to failed on initialization error
            with self._state_lock:
                self._state = StageState.FAILED
                
            error_msg = f"Stage initialization failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.emit_event('error', {"message": error_msg})
            raise InitializationError(error_msg) from e
    
    def _initialize_from_database(self, chat_id: str) -> None:
        """
        Initialize stage data from database
        
        Parameters:
        chat_id: ID of the chat to load
        
        Raises:
        DatabaseError: If database operations fail
        ValueError: If data validation fails
        """
        try:
            self.chat_id = chat_id
            
            # Get chat data with retry logic
            chat_data = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    chat_data = db.get_chat(chat_id)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise DatabaseError(f"Failed to get chat after {max_retries} attempts: {str(e)}")
                    time.sleep(0.5)  # Short delay before retry
            
            if not chat_data:
                raise ValueError(f"Chat with ID {chat_id} not found in database")
            
            # Initialize chat state
            self.current_objective_index = chat_data.get('current_objective_index', 0)
            self.plot_failure_reason = chat_data.get('plot_failure_reason', '')
            self.context = chat_data.get('context', '')
            self.chat_summary = chat_data.get('chat_summary', '')
            self.last_script_data = chat_data.get('last_script_data', None)
            self.last_outline = chat_data.get('last_outline', None)
            self.full_chat = chat_data.get('full_chat', '')
            
            # Consolidate story completion status
            self.story_completed = chat_data.get('story_completed', False) or chat_data.get('completed', False)
            
            # Create player from chat data
            player_name = chat_data.get('player_name', 'Player')
            player_description = chat_data.get('player_description', '')
            self.player = Player(name=player_name, description=player_description)
            
            # Load episode data for plot objectives
            episode_id = chat_data.get('episode_id')
            episode_data = db.get_episode(episode_id)
            if not episode_data:
                raise ValueError(f"Episode with ID {episode_id} not found in database")
            
            # Parse plot objectives
            self.plot_objectives = self._parse_json_or_list(
                episode_data.get('plot_objectives', '[]'),
                default_value=[]
            )
            
            background = episode_data.get('background', '')
            
            # Load show data for character info
            show_id = episode_data.get('show_id')
            show_data = db.get_show(show_id)
            if not show_data:
                raise ValueError(f"Show with ID {show_id} not found in database")
                
            self.show = show_data.get('name', '')
            self.description = show_data.get('description', '')
            
            # Parse characters
            characters = self._parse_json_or_list(
                show_data.get('characters', '[]'),
                default_value=[]
            )
            
            relations = show_data.get('relations', '')
            
            # Create actor instances for each character
            actors = {}
            for character in characters:
                char_name = character.get('name') if isinstance(character, dict) else character.name
                char_desc = character.get('description') if isinstance(character, dict) else character.description
                
                actors[char_name] = Actor(
                    char_name,
                    char_desc,
                    relations,
                    background,
                    actor_llm
                )
            
            self.actors = actors
            
            # Create director with appropriate context
            self.director = Director(
                director_llm,
                self.show,
                self.description,
                background,
                self.actors,
                self.player,
                relations
            )
            
            # Load messages from database into dialogue history
            self._load_messages_from_db()
            
        except (DatabaseError, ValueError) as e:
            # Re-raise these exceptions directly for specific handling
            raise
        except Exception as e:
            # Wrap other exceptions to standardize error handling
            error_msg = f"Error initializing stage from database: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise InitializationError(error_msg) from e
    
    def _initialize_new_stage(self, actors, director):
        """
        Initialize a new stage with provided objects
        
        Parameters:
        actors: Dictionary mapping actor names to Actor objects
        director: Director object
        """
        self.actors = actors or {}
        self.director = director
        self.player = None  # Will be set later
        self.plot_objectives = []
        self.current_objective_index = 0
        self.context = ""
        self.plot_failure_reason = ''
        self.chat_summary = ''
        self.last_script_data = None
        self.last_outline = None
        self.story_completed = False
    
    def _parse_json_or_list(self, data: Union[str, List], default_value: Any = None) -> Any:
        """
        Parse JSON string or return the original data if it's already a list/dict
        
        Parameters:
        data: Data to parse (either string or parsed object)
        default_value: Default value to return if parsing fails
        
        Returns:
        Parsed data or default value on failure
        """
        if not data:
            return default_value
            
        if not isinstance(data, str):
            # Already parsed
            return data
            
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON: {data[:100]}...")
            return default_value
    
    def save_state_to_db(self) -> bool:
        """
        Save current state of the stage to the database
        
        Returns:
        bool: Success status
        
        Raises:
        DatabaseError: If database operation fails
        """
        if not self.chat_id:
            logger.warning("Cannot save state: no chat_id provided")
            return False
            
        # Prepare chat data for save
        chat_data = {
            'current_objective_index': self.current_objective_index,
            'plot_failure_reason': self.plot_failure_reason,
            'context': self.context,
            'chat_summary': self.chat_summary,
            'last_script_data': self.last_script_data,
            'last_outline': self.last_outline,
            'story_completed': self.story_completed,
            'full_chat': self.full_chat,
        }
        
        # Acquire lock before database operation
        with self._db_lock:
            try:
                db.update_chat(self.chat_id, chat_data)
                return True
            except Exception as e:
                error_msg = f"Error saving state to database: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.emit_event('error', {"message": error_msg})
                raise DatabaseError(error_msg) from e
    
    def _load_messages_from_db(self) -> bool:
        """
        Load messages from database and reconstruct dialogue history
        
        Returns:
        bool: Success status
        
        Raises:
        DatabaseError: If database operation fails
        """
        if not self.chat_id:
            logger.warning("Cannot load messages: no chat_id provided")
            return False
            
        # Acquire lock before database operation
        with self._db_lock:
            try:
                # Fetch messages from database
                messages = db.get_messages(self.chat_id)
                
                if not messages:
                    logger.info(f"No messages found for chat {self.chat_id}")
                    return True
                    
                # Clear existing dialogue history
                self.dialogue_history = []
                
                # Reconstruct dialogue history from messages
                for msg in messages:
                    dialogue_entry = {
                        "role": msg['role'],
                        "content": msg['content'],
                        "type": msg['type']
                    }
                    self.dialogue_history.append(dialogue_entry)
                    
                    # Reconstruct chat context
                    if msg['type'] != 'system':  # Skip system messages for context
                        if msg['type'] == 'player_input':
                            line = f"{msg['role']}: {msg['content']}"
                        elif msg['type'] == 'narration':
                            line = f"Narration: {msg['content']}"
                        else:
                            line = f"{msg['role']}: {msg['content']}"
                            
                        if self.context:
                            self.context += "\n" + line
                        else:
                            self.context = line
                            
                return True
                    
            except Exception as e:
                error_msg = f"Error loading messages from database: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.emit_event('error', {"message": error_msg})
                raise DatabaseError(error_msg) from e
    
    def add_to_chat_history(self, text: str) -> None:
        """
        Add text to chat history and persist if needed
        
        Parameters:
        text: Text to add to history
        """
        with self._state_lock:
            if self.context:
                self.context += "\n" + text
            else:
                self.context = text
                
            # Save to database with error handling
            if self.chat_id:
                try:
                    self.save_state_to_db()
                except DatabaseError as e:
                    # Already logged in save_state_to_db
                    pass
    
    def current_objective(self) -> Optional[str]:
        """
        Get the current objective based on the index
        
        Returns:
        str: Current objective or None if complete
        """
        with self._state_lock:
            if self.current_objective_index < len(self.plot_objectives):
                return self.plot_objectives[self.current_objective_index]
            return None
    
    def _clean_json(self, json_str: str) -> str:
        """
        Remove markdown fences and trailing commas from a JSON string.
        
        Parameters:
        json_str: JSON string to clean
        
        Returns:
        str: Cleaned JSON string
        """
        if not json_str:
            return "{}"
            
        cleaned = json_str.strip()
        
        # Remove markdown fences if present
        if cleaned.startswith("```") and cleaned.endswith("```"):
            # Find where the opening fence ends
            first_newline = cleaned.find("\n")
            if first_newline > 0:
                # Check if there's a json prefix
                if "json" in cleaned[:first_newline].lower():
                    # Remove the opening line with ```json
                    cleaned = cleaned[first_newline:].strip()
                else:
                    # Just remove the triple backticks
                    cleaned = cleaned[3:-3].strip()
            else:
                # Just remove the triple backticks if no newline
                cleaned = cleaned[3:-3].strip()
        
        # Check for standalone json prefix line
        lines = cleaned.split("\n")
        if lines and lines[0].lower().startswith('json'):
            cleaned = "\n".join(lines[1:])
        
        # Remove trailing commas before a closing brace/bracket
        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)
        
        # Add enclosing braces if the JSON doesn't have them
        if (not cleaned.startswith("{") and not cleaned.startswith("[")) or \
           (not cleaned.endswith("}") and not cleaned.endswith("]")):
            # If it doesn't look like proper JSON, wrap it
            if ":" in cleaned:  # Likely an object
                cleaned = "{" + cleaned + "}"
            else:  # Likely an array or plain value
                try:
                    # Try to parse as is first
                    json.loads(cleaned)
                except:
                    # If that fails, wrap as a value
                    cleaned = '{"value": ' + cleaned + '}'
        
        return cleaned
    
    def check_objective_completion(self, check_result: Dict, current_obj: str) -> Tuple[bool, Dict]:
        """
        Check if an objective has been completed and handle the transition
        
        Parameters:
        check_result: Result from director's objective check
        current_obj: Current objective text
        
        Returns:
        Tuple[bool, Dict]: (Completion status, Status details)
        """
        with self._state_lock:
            if check_result.get("completed", False):
                # Update the objective index
                old_index = self.current_objective_index
                self.current_objective_index += 1
                self.plot_failure_reason = ''
                
                # Get the next objective (if any)
                next_objective = self.current_objective()
                
                # Prepare status message
                status_msg = f"Objective '{current_obj}' completed: {check_result.get('reason', '')}"
                
                # Check if this was the final objective
                is_final = self.current_objective_index >= len(self.plot_objectives)
                
                # Create objective status with appropriate flags
                objective_status = {
                    "completed": True,
                    "message": status_msg,
                    "reason": check_result.get('reason', ''),
                    "index": self.current_objective_index,
                    "current": next_objective,
                    "total": len(self.plot_objectives),
                    "story_completed": is_final
                }
                
                # Save state to database after objective completion
                try:
                    if self.chat_id:
                        with self._db_lock:
                            self.save_state_to_db()
                except DatabaseError:
                    # Error already logged
                    pass
                
                # Emit the updated status
                self.emit_event('objective_status', objective_status)
                
                # If there are more objectives, trigger the next turn
                if not is_final:
                    # Schedule next turn with a slight delay
                    self._state = StageState.IDLE  # Reset state to allow next turn
                    self._thread_pool.submit(self._delayed_next_turn, 1)
                else:
                    # Mark the story as completed
                    self.story_completed = True
                    self._state = StageState.COMPLETED
                    
                    # Save completion status to database
                    try:
                        if self.chat_id:
                            with self._db_lock:
                                self.save_state_to_db()
                    except DatabaseError:
                        # Error already logged
                        pass
                    
                    self.emit_event('status', {"message": "All objectives completed. Story complete."})
                    # Send a clear completion event
                    self.emit_event('objective_status', {
                        "completed": True,
                        "message": "All objectives have been completed! Story is finished.",
                        "index": self.current_objective_index,
                        "total": len(self.plot_objectives),
                        "final": True,
                        "story_completed": True
                    })
                
                return True, objective_status
            else:
                # Continue with the current objective
                self.plot_failure_reason = 'Plot objective not met due to the following reason: ' + check_result.get('reason', '') + ' Please make the plot so it is addressed and the plot objective is completed'
                
                # Save failure reason to database
                try:
                    if self.chat_id:
                        with self._db_lock:
                            self.save_state_to_db()
                except DatabaseError:
                    # Error already logged
                    pass
                
                # Prepare status message
                status_msg = f"Objective '{current_obj}' not yet completed: {check_result.get('reason', '')}"
                objective_status = {
                    "completed": False,
                    "message": status_msg,
                    "reason": check_result.get('reason', ''),
                    "index": self.current_objective_index,
                    "current": current_obj,
                    "total": len(self.plot_objectives),
                    "story_completed": False
                }
                
                # Emit the status
                self.emit_event('objective_status', objective_status)
                
                # Reset state to IDLE
                self._state = StageState.IDLE
                
                return False, objective_status
    
    def _delayed_next_turn(self, delay_seconds: float = 1.0) -> None:
        """
        Schedule the next turn with a delay
        
        Parameters:
        delay_seconds: Delay in seconds before triggering next turn
        """
        try:
            time.sleep(delay_seconds)
            self.trigger_next_turn()
        except Exception as e:
            logger.error(f"Error in delayed next turn: {str(e)}", exc_info=True)
            self.emit_event('error', {"message": f"Failed to trigger next turn: {str(e)}"})
    
    def process_director_script(self, script_json: str) -> List[Dict]:
        """
        Process the JSON script generated by the director.
        Adds realistic typing delays and indicators.
        
        Parameters:
        script_json: JSON string containing script data
        
        Returns:
        List[Dict]: Dialogue lines processed from the script
        
        Raises:
        ProcessingError: If processing fails
        """
        try:
            # Clean and parse JSON
            script_str = self._clean_json(script_json)
            logger.info(f"Processing director script for chat {self.chat_id}")
            
            try:
                script_data = json.loads(script_str)
                scripts_count = len(script_data.get("scripts", []))
                logger.info(f"Successfully parsed script with {scripts_count} dialogue items")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing script JSON: {str(e)}\nScript: {script_str[:200]}...")
                script_data = {"scripts": []}
                    
            dialogue_lines = []
            messages_to_save = []
            
            with self._state_lock:
                sequence_count = len(self.dialogue_history)
                
                script_items = script_data.get("scripts", [])
                for i, line in enumerate(script_items):
                    logger.info(f"Processing script item {i+1}/{len(script_items)}")
                    role = line.get("role", "")
                    # For actor lines, check for "instruction" then fallback to "content"
                    instructions = line.get("instruction", "") or line.get("content", "")
                    
                    if role in self.actors:
                        # Show typing indicator
                        logger.info(f"Emitting typing indicator for {role}")
                        self.emit_event('typing_indicator', {
                            "role": role,
                            "status": "typing",
                        })
                        
                        # Add artificial delay to simulate typing
                        time.sleep(2)
                        
                        actor = self.actors[role]
                        # Update the actor's chat_history dynamically before calling reply.
                        logger.info(f"Getting reply from actor {role}")
                        reply_output = actor.reply(self.context, instructions)
                        dialogue_line = f"{role}: {reply_output}"
                        self.add_to_chat_history(dialogue_line)
                        
                        if self.full_chat:
                            self.full_chat += "\n" + dialogue_line
                        else:
                            self.full_chat = dialogue_line
                        
                        # Remove typing indicator
                        self.emit_event('typing_indicator', {
                            "role": role,
                            "status": "idle",
                        })
                        
                        # Create dialogue entry for API response
                        dialogue_entry = {
                            "role": role, 
                            "content": reply_output, 
                            "type": "actor_dialogue"
                        }
                        dialogue_lines.append(dialogue_entry)
                        
                        # Add to messages to be saved in database
                        messages_to_save.append({
                            "role": role,
                            "content": reply_output,
                            "type": "actor_dialogue",
                            "sequence": sequence_count
                        })
                        sequence_count += 1
                        
                        # Emit the dialogue line through Socket.IO if available
                        logger.info(f"Emitting dialogue for {role}")
                        self.emit_event('dialogue', dialogue_entry)
                        
                    elif role.lower() == "narration":
                        # Show narration is being added
                        logger.info(f"Emitting typing indicator for Narration")
                        self.emit_event('typing_indicator', {
                            "role": "Narration",
                            "status": "typing",
                        })
                        
                        content = line.get('content', instructions)
                        dialogue_line = f"Narration: {content}"
                        self.add_to_chat_history(dialogue_line)
                        
                        if self.full_chat:
                            self.full_chat += "\n" + dialogue_line
                        else:
                            self.full_chat = dialogue_line
                        
                        # Remove typing indicator
                        self.emit_event('typing_indicator', {
                            "role": "Narration",
                            "status": "idle",
                        })
                        
                        dialogue_entry = {
                            "role": "Narration", 
                            "content": content, 
                            "type": "narration"
                        }
                        dialogue_lines.append(dialogue_entry)
                        
                        # Add to messages to be saved in database
                        messages_to_save.append({
                            "role": "Narration",
                            "content": content,
                            "type": "narration",
                            "sequence": sequence_count
                        })
                        sequence_count += 1
                        
                        logger.info(f"Emitting narration dialogue")
                        self.emit_event('dialogue', dialogue_entry)
                        
                    else:
                        # Unrecognized role; treat as narration.
                        logger.info(f"Processing unknown role: {role}")
                        self.emit_event('typing_indicator', {
                            "role": role,
                            "status": "typing",
                        })
                        
                        time.sleep(1)
                        
                        dialogue_line = f"{role}: {instructions}"
                        self.add_to_chat_history(dialogue_line)
                        
                        if self.full_chat:
                            self.full_chat += "\n" + dialogue_line
                        else:
                            self.full_chat = dialogue_line
                        
                        self.emit_event('typing_indicator', {
                            "role": role,
                            "status": "idle",
                        })
                        
                        dialogue_entry = {
                            "role": role, 
                            "content": instructions, 
                            "type": "other"
                        }
                        dialogue_lines.append(dialogue_entry)
                        
                        # Add to messages to be saved in database
                        messages_to_save.append({
                            "role": role,
                            "content": instructions,
                            "type": "other",
                            "sequence": sequence_count
                        })
                        sequence_count += 1
                        
                        logger.info(f"Emitting dialogue for unknown role: {role}")
                        self.emit_event('dialogue', dialogue_entry)
                
                # Store the dialogue history for API access
                self.dialogue_history.extend(dialogue_lines)
            
            # Save messages to database as a batch operation
            if self.chat_id and messages_to_save:
                logger.info(f"Saving {len(messages_to_save)} messages to database for chat {self.chat_id}")
                with self._db_lock:
                    try:
                        db.add_messages_batch(self.chat_id, messages_to_save)
                        logger.info(f"Successfully saved messages to database for chat {self.chat_id}")
                    except Exception as e:
                        logger.error(f"Error saving messages to database: {str(e)}", exc_info=True)
                        self.emit_event('error', {"message": f"Error saving messages: {str(e)}"})
            
            # Save dialogue history to database
            if self.chat_id:
                try:
                    with self._db_lock:
                        self.save_state_to_db()
                except DatabaseError:
                    # Error already logged
                    pass
            
            logger.info(f"Processed {len(dialogue_lines)} dialogue lines for chat {self.chat_id}")
            return dialogue_lines
                
        except Exception as e:
            error_msg = f"Error processing director script: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.emit_event('error', {"message": error_msg})
            raise ProcessingError(error_msg) from e
    
    def advance_turn(self) -> Dict:
        """
        Advance the game turn based on the current objective.
        Returns dialogue lines generated during this turn.
        
        Returns:
        Dict: Turn result with status and dialogue
        """
        # Generate a unique operation ID
        operation_id = f"turn_{int(time.time() * 1000)}"
        
        # Try to acquire the state lock for status check and update
        with self._state_lock:
            # Check if we can start processing
            if self._state != StageState.IDLE:
                current_state = self._state.name
                msg = f"Cannot advance turn: current state is {current_state}"
                if self._state == StageState.PROCESSING:
                    msg += f" (operation {self._current_operation_id})"
                self.emit_event('status', {"message": msg})
                return {"status": "waiting", "message": msg, "dialogue": []}
            
            # Don't proceed if the story is already completed
            if self.story_completed:
                self.emit_event('status', {"message": "Story is already complete. No more turns."})
                return {"status": "complete", "message": "Story already complete", "dialogue": []}
            
            # Set state to processing and record operation
            self._state = StageState.PROCESSING
            self._current_operation_id = operation_id
            self._operation_timestamp = time.time()
        
        try:
            logger.info(f"Starting advance_turn (operation {operation_id}) for chat {self.chat_id}")
            objective = self.current_objective()
            if not objective:
                with self._state_lock:
                    # Mark the story as completed
                    self.story_completed = True
                    self._state = StageState.COMPLETED
                    
                    # Save completion status to database
                    if self.chat_id:
                        try:
                            with self._db_lock:
                                self.save_state_to_db()
                        except DatabaseError:
                            # Error already logged
                            pass
                
                self.emit_event('status', {"message": "No current objective. Story complete."})
                # Send a clear completion event to the frontend
                self.emit_event('objective_status', {
                    "completed": True,
                    "message": "All objectives have been completed! Story is finished.",
                    "index": self.current_objective_index,
                    "total": len(self.plot_objectives),
                    "final": True,
                    "story_completed": True
                })
                return {"status": "complete", "message": "Story complete", "dialogue": []}
            
            # Emit event that director is working
            logger.info(f"Director starting work for chat {self.chat_id}")
            self.emit_event('director_status', {"status": "directing", "message": "Director is directing..."})
            
            # Set up a timeout protection for director work
            director_timeout = 120  # 2 minutes timeout
            director_start_time = time.time()
            
            # Director generates an outline based on the current chat history and current plot objective
            try:
                logger.info(f"Generating outline for chat {self.chat_id} with objective: {objective[:30]}...")
                outline_str = self.director.generate_outline(self.context, objective, self.plot_failure_reason)
                
                # Check for timeout
                if time.time() - director_start_time > director_timeout:
                    raise TimeoutError("Director outline generation timed out")
                    
                logger.info(f"Outline generated for chat {self.chat_id}, length: {len(outline_str)}")
            except Exception as e:
                error_msg = f"Error generating outline: {str(e)}"
                logger.error(error_msg, exc_info=True)
                # Explicitly return director to idle state
                self.emit_event('director_status', {"status": "idle", "message": ""})
                self.emit_event('error', {"message": error_msg})
                
                with self._state_lock:
                    self._state = StageState.IDLE
                    self._current_operation_id = None
                
                return {"status": "error", "message": error_msg, "dialogue": []}
            
            try:
                cleaned_outline = self._clean_json(outline_str)
                logger.info(f"Parsing outline JSON for chat {self.chat_id}")
                outline = json.loads(cleaned_outline)
                
                with self._state_lock:
                    self.last_outline = outline
                    self.chat_summary = outline.get('previous_outline', '')
                    
                    # Store these updates
                    try:
                        if self.chat_id:
                            with self._db_lock:
                                self.save_state_to_db()
                    except DatabaseError:
                        # Error already logged
                        pass
                
                # Updating the background to include the summary and clearing the chat history to reduce context window
                logger.info(f"Updating context and backgrounds for chat {self.chat_id}")
                with self._state_lock:
                    self.context = ''
                    self.director.background = self.chat_summary
                    for actor_name in self.actors:
                        self.actors[actor_name].background = self.chat_summary
                
                # Get the new outline from the result
                new_outline = outline.get('new_outline', outline)  # Fallback to the entire outline
                
                # Check for timeout again
                if time.time() - director_start_time > director_timeout:
                    raise TimeoutError("Director processing timed out after outline generation")
                    
                # Director generates turn instructions (script) based on the outline
                logger.info(f"Generating turn instructions for chat {self.chat_id}")
                script_json = self.director.generate_turn_instructions(self.context, new_outline)
                logger.info(f"Turn instructions generated for chat {self.chat_id}, length: {len(script_json)}")
                
                with self._state_lock:
                    self.last_script_data = script_json
                    
                    # Save outline and script to database
                    try:
                        if self.chat_id:
                            with self._db_lock:
                                self.save_state_to_db()
                    except DatabaseError:
                        # Error already logged
                        pass
                
                # Director is done, about to process lines - IMPORTANT: This signals the frontend to stop showing "directing"
                logger.info(f"Director finished work for chat {self.chat_id}, switching to idle")
                self.emit_event('director_status', {"status": "idle", "message": ""})
                
                # Process the script and get the dialogue lines
                logger.info(f"Processing director script for chat {self.chat_id}")
                dialogue_lines = self.process_director_script(script_json)
                logger.info(f"Generated {len(dialogue_lines)} dialogue lines for chat {self.chat_id}")
                
            except Exception as e:
                error_msg = f"Error processing outline: {str(e)}"
                logger.error(error_msg, exc_info=True)
                # Make sure we reset the director status in case of error
                self.emit_event('director_status', {"status": "idle", "message": ""})
                self.emit_event('error', {"message": error_msg})
                
                with self._state_lock:
                    self._state = StageState.IDLE
                    self._current_operation_id = None
                
                return {"status": "error", "message": error_msg, "dialogue": []}
            
            # Check if the objective has been reached using the director's check_objective method
            try:
                logger.info(f"Checking objective completion for chat {self.chat_id}")
                check_result_str = self.director.check_objective(self.full_chat, objective)
                logger.info(f"Objective check result received for chat {self.chat_id}")
                objective_status = {}
                
                check_result = json.loads(self._clean_json(check_result_str))
                completed, objective_status = self.check_objective_completion(check_result, objective)
                
            except Exception as e:
                error_msg = f"Error parsing objective check result: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.emit_event('error', {"message": error_msg})
                objective_status = {
                    "completed": False,
                    "message": error_msg,
                    "error": True
                }
                
                with self._state_lock:
                    self._state = StageState.IDLE
                    self._current_operation_id = None
            
            logger.info(f"Advance turn completed for chat {self.chat_id}")
            result = {
                "status": "success",
                "dialogue": dialogue_lines,
                "objective": {
                    "current": objective,
                    "index": self.current_objective_index,
                    "total": len(self.plot_objectives),
                    "status": objective_status
                }
            }
            
            # Note: State has been reset in check_objective_completion
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error in advance_turn: {str(e)}"
            logger.error(error_msg, exc_info=True)
            # Make sure we reset the director status
            self.emit_event('director_status', {"status": "idle", "message": ""})
            self.emit_event('error', {"message": error_msg})
            
            with self._state_lock:
                self._state = StageState.IDLE
                self._current_operation_id = None
            
            return {"status": "error", "message": error_msg, "dialogue": []}
    
    def trigger_next_turn(self) -> bool:
        """
        Helper method to trigger the next turn
        
        Returns:
        bool: True if turn was triggered, False otherwise
        """
        with self._state_lock:
            # Don't start a new turn if:
            # 1. We're not in IDLE state
            # 2. We've reached or exceeded the number of objectives
            # 3. The story has been explicitly marked as completed
            if (self._state != StageState.IDLE or 
                self.current_objective_index >= len(self.plot_objectives) or 
                self.story_completed):
                return False
        
        # Use thread pool to make this non-blocking
        self._thread_pool.submit(self.advance_turn)
        return True
    
    def player_interrupt(self, player_input: str) -> Dict:
        """
        Handle a player interruption.
        
        Parameters:
        player_input: Text input from the player
        
        Returns:
        Dict: Result with status and dialogue
        """
        # Generate a unique operation ID
        operation_id = f"interrupt_{int(time.time() * 1000)}"
        
        # Check state and try to start processing
        with self._state_lock:
            if self._state != StageState.IDLE:
                current_state = self._state.name
                msg = f"Cannot process interruption: current state is {current_state}"
                if self._state == StageState.PROCESSING:
                    msg += f" (operation {self._current_operation_id})"
                self.emit_event('status', {"message": msg})
                return {"status": "waiting", "message": msg, "dialogue": []}
            
            # Don't allow player interruption if the story is already completed
            if self.story_completed:
                self.emit_event('status', {"message": "Story is already complete. No more interactions."})
                return {"status": "complete", "message": "Story already complete", "dialogue": []}
            
            # Input validation
            if not player_input or not player_input.strip():
                self.emit_event('status', {"message": "Empty input cannot be processed."})
                return {"status": "error", "message": "Empty input", "dialogue": []}
            
            # Set state to processing
            self._state = StageState.PROCESSING
            self._current_operation_id = operation_id
            self._operation_timestamp = time.time()
        
        try:
            self.emit_event('status', {"message": "Player interrupts"})
            
            # Add the player's input to the chat history
            interrupt_line = f"{self.player.name}: {player_input}"
            self.add_to_chat_history(interrupt_line)
            
            # Update full chat
            with self._state_lock:
                if self.full_chat:
                    self.full_chat += "\n" + interrupt_line
                else:
                    self.full_chat = interrupt_line
            
            # Add to dialogue history for frontend
            player_dialogue = {
                "role": self.player.name,
                "content": player_input,
                "type": "player_input"
            }
            
            with self._state_lock:
                self.dialogue_history.append(player_dialogue)
            
            self.emit_event('dialogue', player_dialogue)
            
            # Save player input to message database
            if self.chat_id:
                sequence = len(self.dialogue_history) - 1  # Use the current position in history
                try:
                    with self._db_lock:
                        db.add_message(
                            self.chat_id,
                            self.player.name,
                            player_input,
                            "player_input",
                            sequence
                        )
                except Exception as e:
                    logger.error(f"Error saving player message to database: {str(e)}", exc_info=True)
                    self.emit_event('error', {"message": f"Warning: Could not save your message: {str(e)}"})
                
                # Also save overall state
                try:
                    with self._db_lock:
                        self.save_state_to_db()
                except DatabaseError:
                    # Error already logged
                    pass
            
            # Show that director is working
            self.emit_event('director_status', {"status": "directing", "message": "Director is directing..."})
            
            # After the interruption, ask the director to generate a new outline and script
            current_obj = self.current_objective()
            if not current_obj:
                self.emit_event('status', {"message": "No current objective to continue after interruption."})
                
                with self._state_lock:
                    self.story_completed = True  # Mark as completed if there's no objective
                    self._state = StageState.COMPLETED
                    
                    # Save completion status
                    try:
                        if self.chat_id:
                            with self._db_lock:
                                self.save_state_to_db()
                    except DatabaseError:
                        # Error already logged
                        pass
                
                return {"status": "error", "message": "No current objective", "dialogue": []}
            
            outline_str = self.director.generate_outline(self.context, current_obj)
            
            try:
                outline = json.loads(self._clean_json(outline_str))
                
                with self._state_lock:
                    self.last_outline = outline
                
                new_outline = outline.get('new_outline', outline)
                
                script_json = self.director.generate_turn_instructions(self.context, new_outline)
                
                with self._state_lock:
                    self.last_script_data = script_json
                
                # Save new outline and script to database
                try:
                    if self.chat_id:
                        with self._db_lock:
                            self.save_state_to_db()
                except DatabaseError:
                    # Error already logged
                    pass
                
                # Director is done working
                self.emit_event('director_status', {"status": "idle", "message": ""})
                
                dialogue_lines = self.process_director_script(script_json)
                
                # Check objective completion
                check_result_str = self.director.check_objective(self.full_chat, current_obj)
                
                try:
                    check_result = json.loads(self._clean_json(check_result_str))
                    completed, _ = self.check_objective_completion(check_result, current_obj)
                except Exception as e:
                    error_msg = f"Error checking objective: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    self.emit_event('error', {"message": error_msg})
                    
                    with self._state_lock:
                        self._state = StageState.IDLE
                        self._current_operation_id = None
                
                result = {
                    "status": "success",
                    "dialogue": dialogue_lines,
                    "player_input": player_input
                }
                
                # State has been reset in check_objective_completion
                return result
            
            except json.JSONDecodeError as e:
                error_msg = f"Error parsing JSON from director: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.emit_event('error', {"message": error_msg})
                
                with self._state_lock:
                    self._state = StageState.IDLE
                    self._current_operation_id = None
                
                return {"status": "error", "message": error_msg, "dialogue": []}
            
        except Exception as e:
            error_msg = f"Error processing player interruption: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.emit_event('error', {"message": error_msg})
            
            with self._state_lock:
                self._state = StageState.IDLE
                self._current_operation_id = None
            
            return {"status": "error", "message": error_msg, "dialogue": []}
    
    def get_state(self) -> Dict:
        """
        Get the current state of the stage for API responses.
        
        Returns:
        Dict: Current stage state
        """
        with self._state_lock:
            # Calculate completed status
            completed = (self.current_objective_index >= len(self.plot_objectives) or 
                        self.story_completed)
            
            # If index exceeds or equals objectives count, explicitly mark as completed
            if self.current_objective_index >= len(self.plot_objectives):
                self.story_completed = True  # Ensure this flag is set
                
                # Save the completion status to database
                try:
                    if self.chat_id:
                        with self._db_lock:
                            self.save_state_to_db()
                except DatabaseError:
                    # Error already logged
                    pass
            
            return {
                "current_objective_index": self.current_objective_index,
                "total_objectives": len(self.plot_objectives),
                "current_objective": self.current_objective(),
                "plot_failure_reason": self.plot_failure_reason,
                "completed": completed,
                "story_completed": completed,
                "dialogue_history": self.dialogue_history,
                "processing_state": self._state.name,
                "current_operation": self._current_operation_id,
                "last_operation_time": self._operation_timestamp
            }
    
    def emit_event(self, event_type: str, data: Dict) -> None:
        """
        Emit an event through Socket.IO if available.
        
        Parameters:
        event_type: Type of event to emit
        data: Data to send with the event
        """
        if self.socketio:
            try:
                # Ensure we're sending to the correct room (chat_id)
                if self.chat_id:
                    self.socketio.emit(event_type, data, room=self.chat_id)
                else:
                    # Fallback to broadcast if no chat_id (should be rare)
                    self.socketio.emit(event_type, data)
                    logger.warning(f"Emitting {event_type} without chat_id room specification")
            except Exception as e:
                logger.error(f"Error emitting event {event_type}: {str(e)}", exc_info=True)
        
    def run_sequence(self) -> Dict:
        """
        Run through the entire sequence of plot objectives.
        This is an API-friendly version of run_stage.
        
        Returns:
        Dict: Status of the sequence start
        """
        # Start the first turn, the rest will be triggered automatically
        result = self.advance_turn()
        
        if result.get("status") == "error":
            return {
                "status": "error",
                "message": result.get("message", "Error starting sequence")
            }
        
        return {
            "status": "started",
            "message": "Story sequence started"
        }
    
    def create_new_chat(self, player_name: str, player_description: str, episode_id: str, user_id: str) -> Optional[str]:
        """
        Create a new chat entry in the database and initialize this stage with it
        
        Parameters:
        player_name: Name of the player character
        player_description: Description of the player character
        episode_id: ID of the episode to play
        user_id: ID of the user creating this chat
        
        Returns:
        Optional[str]: New chat_id or None on failure
        
        Raises:
        DatabaseError: If database operation fails
        """
        try:
            # Input validation
            if not player_name or not episode_id or not user_id:
                error_msg = "Missing required parameters for creating chat"
                logger.error(error_msg)
                self.emit_event('error', {"message": error_msg})
                return None
            
            # Create chat in database using the database method
            with self._db_lock:
                chat_result = db.create_chat(
                    episode_id=episode_id,
                    user_id=user_id,
                    player_name=player_name,
                    player_description=player_description
                )
            
            if not chat_result:
                error_msg = "Failed to create chat in database"
                logger.error(error_msg)
                self.emit_event('error', {"message": error_msg})
                return None
            
            chat_id = chat_result['id']
            self.chat_id = chat_id
            
            # Reinitialize this stage with the new chat_id
            self.__init__(chat_id=chat_id, socketio=self.socketio)
            
            # Add initial system message
            try:
                with self._db_lock:
                    db.add_message(
                        chat_id=chat_id,
                        role="system",
                        content="Chat started",
                        type="system",
                        sequence=0
                    )
            except Exception as e:
                logger.warning(f"Could not add initial system message: {str(e)}")
                self.emit_event('error', {"message": f"Warning: Could not add initial system message: {str(e)}"})
            
            logger.info(f"Created new chat with ID: {chat_id}")
            return chat_id
            
        except Exception as e:
            error_msg = f"Error creating new chat: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.emit_event('error', {"message": error_msg})
            raise DatabaseError(error_msg) from e
    
    def reset_stuck_state(self) -> bool:
        """
        Reset the stage state if it appears to be stuck in processing
        This is a safety mechanism for hung operations
        
        Returns:
        bool: True if state was reset, False if not needed
        """
        with self._state_lock:
            # Check if we're in processing state and operation is old
            if self._state == StageState.PROCESSING:
                current_time = time.time()
                operation_age = current_time - self._operation_timestamp
                
                # If operation has been running for more than 5 minutes, consider it stuck
                if operation_age > 300:  # 5 minutes in seconds
                    logger.warning(f"Resetting stuck operation: {self._current_operation_id} (age: {operation_age:.1f}s)")
                    self._state = StageState.IDLE
                    self._current_operation_id = None
                    return True
            
            return False
    
    def cleanup(self) -> None:
        """
        Clean up resources when stage is no longer needed
        """
        logger.info(f"Cleaning up stage for chat_id: {self.chat_id}")
        # Nothing needed here currently, but useful hook for future resource cleanup
        pass