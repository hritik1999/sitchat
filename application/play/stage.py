import json
import re
import time
import threading
from application.database.db import db
from application.play.player import Player
from application.play.actor import Actor
from application.play.director import Director
from application.ai.llm import actor_llm, director_llm

class Stage:
    def __init__(self, actors=None, director=None, socketio=None, chat_id=None):
        """Initialize a Stage with actors/director or load from database with chat_id"""
        self.socketio = socketio
        self.dialogue_history = []
        self.is_processing = False
        self.processing_lock = threading.Lock()
        self.story_completed = False
        self.full_chat = ''
        self.chat_id = None

        if chat_id:
            self._load_from_database(chat_id)
        else:
            self._init_with_objects(actors, director)
    
    def _load_from_database(self, chat_id):
        """Load stage data from database"""
        self.chat_id = chat_id
        chat_data = db.get_chat(chat_id)
        
        if not chat_data:
            raise ValueError(f"Chat with ID {chat_id} not found in database")
            
        # Load basic chat data
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
        
        # Parse plot objectives
        self.plot_objectives = self._parse_json_field(episode_data.get('plot_objectives', '[]'))
        background = episode_data.get('background', '')

        # Load show data
        show_id = episode_data.get('show_id')
        show_data = db.get_show(show_id)
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
    
    def _init_with_objects(self, actors, director):
        """Initialize with provided objects"""
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
        """Parse a potential JSON string field"""
        if isinstance(field, str):
            try:
                return json.loads(field)
            except:
                return []
        return field or []

    def save_state_to_db(self):
        """Save current state to database"""
        if not self.chat_id:
            self.emit_event('error', {"message": "Cannot save state: no chat_id provided"})
            return False
            
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
            db.update_chat(self.chat_id, chat_data)
            return True
        except Exception as e:
            self.emit_event('error', {"message": f"Error saving state: {str(e)}"})
            return False
            
    def load_messages_from_db(self):
        """Load messages from database into dialogue history"""
        if not self.chat_id:
            self.emit_event('error', {"message": "Cannot load messages: no chat_id provided"})
            return False
            
        try:
            messages = db.get_messages(self.chat_id)
            
            if not messages:
                return True
                
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
                        
            return True
                
        except Exception as e:
            self.emit_event('error', {"message": f"Error loading messages: {str(e)}"})
            return False

    def add_to_chat_history(self, text):
        """Add text to chat history and save state"""
        self.context = f"{self.context}\n{text}" if self.context else text
        if self.chat_id:
            self.save_state_to_db()

    def current_objective(self):
        """Get the current objective or None if all completed"""
        if self.current_objective_index < len(self.plot_objectives):
            return self.plot_objectives[self.current_objective_index]
        return None
    
    def _clean_json(self, json_str):
        """Clean JSON string by removing markdown and fixing common issues"""
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
        """Check if an objective is completed and handle the transition"""
        try:
            if check_result.get("completed", False):
                # Update objective index
                self.current_objective_index += 1
                self.plot_failure_reason = ''
                
                # Get next objective
                next_objective = self.current_objective()
                
                # Status message
                status_msg = f"Objective '{current_obj}' completed: {check_result.get('reason', '')}"
                
                # Check if final objective
                is_final = self.current_objective_index + 1 > len(self.plot_objectives)
                
                # Create objective status
                objective_status = {
                    "completed": True,
                    "message": status_msg,
                    "reason": check_result.get('reason', ''),
                    "index": self.current_objective_index,
                    "current": next_objective,
                    "total": len(self.plot_objectives),
                    "story_completed": is_final
                }
                
                # Save state
                if self.chat_id:
                    self.save_state_to_db()
                    
                # Emit status
                self.emit_event('objective_status', objective_status)
                
                # Handle next steps
                if not is_final:
                    try:
                        with self.processing_lock:
                            self.is_processing = False
                        self.trigger_next_turn()
                    except Exception as e:
                        self.emit_event('error', {"message": f"Error triggering next turn: {str(e)}"})
                        with self.processing_lock:
                            self.is_processing = False
                else:
                    # Mark story as complete
                    self.story_completed = True
                    if self.chat_id:
                        self.save_state_to_db()
                        
                    self.emit_event('status', {"message": "All objectives completed. Story complete."})
                    self.emit_event('objective_status', {
                        "completed": True,
                        "message": "All objectives have been completed! Story is finished.",
                        "index": self.current_objective_index,
                        "total": len(self.plot_objectives),
                        "final": True,
                        "story_completed": True
                    })
                    with self.processing_lock:
                        self.is_processing = False
                
                return True, objective_status
            else:
                # Continue with current objective
                self.plot_failure_reason = 'Plot objective not met: ' + check_result.get('reason', '')
                
                if self.chat_id:
                    self.save_state_to_db()
                    
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

                with self.processing_lock:
                    self.is_processing = False
                
                self.emit_event('objective_status', objective_status)
                return False, objective_status
        except Exception as e:
            self.emit_event('error', {"message": f"Error checking objective completion: {str(e)}"})
            with self.processing_lock:
                self.is_processing = False
            return False, {"completed": False, "error": True, "message": str(e)}
        
        finally:
            with self.processing_lock:
                self.is_processing = False

    def process_director_script(self, script_json):
        """Process the script from director with typing indicators"""
        try:
            script_str = self._clean_json(script_json)
            script_data = json.loads(script_str)
        except Exception as e:
            self.emit_event('error', {"message": f"Error parsing script JSON: {str(e)}"})
            script_data = {"scripts": []}
        
        dialogue_lines = []
        messages_to_save = []
        sequence_count = len(self.dialogue_history)
        
        try:
            for line in script_data.get("scripts", []):
                role = line.get("role", "")
                instructions = line.get("instruction", "") or line.get("content", "")
                    
                if role in self.actors:
                    # Handle actor dialogue
                    self.emit_event('typing_indicator', {"role": role, "status": "typing"})
                    time.sleep(2)
                    
                    actor = self.actors[role]
                    reply_output = actor.reply(self.context, instructions)
                    dialogue_line = f"{role}: {reply_output}"
                    self.add_to_chat_history(dialogue_line)
                    self.full_chat = f"{self.full_chat}\n{dialogue_line}" if self.full_chat else dialogue_line
                    
                    self.emit_event('typing_indicator', {"role": role, "status": "idle"})
                    
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
                    
                    self.emit_event('dialogue', dialogue_entry)
                    
                elif role.lower() == "narration":
                    # Handle narration
                    self.emit_event('typing_indicator', {"role": "Narration", "status": "typing"})
                    
                    content = line.get('content', instructions)
                    dialogue_line = f"Narration: {content}"
                    self.add_to_chat_history(dialogue_line)
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
                    time.sleep(1)
                    
                    dialogue_line = f"{role}: {instructions}"
                    self.add_to_chat_history(dialogue_line)
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
            
            # Store dialogue history
            self.dialogue_history.extend(dialogue_lines)
            
            # Save to database
            if self.chat_id and messages_to_save:
                try:
                    db.add_messages_batch(self.chat_id, messages_to_save)
                except Exception as e:
                    self.emit_event('error', {"message": f"Error saving messages: {str(e)}"})
            
            if self.chat_id:
                self.save_state_to_db()
                
            return dialogue_lines
        
        except Exception as e:
            self.emit_event('error', {"message": f"Error processing director script: {str(e)}"})
            return dialogue_lines or []
        
        finally:
            with self.processing_lock:
                self.is_processing = False

    def trigger_next_turn(self):
        """Trigger the next turn in a non-blocking way"""
        with self.processing_lock:
            if (self.is_processing or 
                self.current_objective_index + 1 > len(self.plot_objectives) or 
                self.story_completed):
                return
        
        def run_turn():
            try:
                self.advance_turn()
            except Exception as e:
                self.emit_event('error', {"message": f"Error in turn: {str(e)}"})
                with self.processing_lock:
                    self.is_processing = False
            finally:
                with self.processing_lock:
                    self.is_processing = False
        
        thread = threading.Thread(target=run_turn)
        thread.daemon = True
        thread.start()

    def advance_turn(self):
        """Advance the game turn based on current objective"""
        with self.processing_lock:
            if self.is_processing:
                self.emit_event('status', {"message": "Already processing a turn. Please wait."})
                return {"status": "waiting", "message": "Already processing a turn", "dialogue": []}
            
            if self.story_completed:
                self.emit_event('status', {"message": "Story is already complete."})
                return {"status": "complete", "message": "Story already complete", "dialogue": []}
                
            self.is_processing = True
        
        try:
            objective = self.current_objective()
            if not objective:
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

            # Director generates outline and script
            self.emit_event('director_status', {"status": "directing", "message": "Director is directing..."})
            
            outline_str = self.director.generate_outline(self.context, objective, self.plot_failure_reason)
            
            try:
                outline = json.loads(self._clean_json(outline_str))
                self.last_outline = outline
                self.chat_summary = outline.get('previous_outline')

                # Reset context and update backgrounds
                self.context = ''
                self.director.background = self.chat_summary
                for actor_name in self.actors:
                    self.actors[actor_name].background = self.chat_summary
                    
                new_outline = outline.get('new_outline', outline)
                
                script_json = self.director.generate_turn_instructions(self.context, new_outline)
                self.last_script_data = script_json
                
                if self.chat_id:
                    self.save_state_to_db()

                self.emit_event('director_status', {"status": "idle", "message": ""})
                
                dialogue_lines = self.process_director_script(script_json)
                
            except Exception as e:
                error_msg = f"Error processing outline: {str(e)}"
                self.emit_event('error', {"message": error_msg})
                return {"status": "error", "message": error_msg, "dialogue": []}

            # Check objective completion
            check_result_str = self.director.check_objective(self.full_chat, objective)
            
            try:
                check_result = json.loads(self._clean_json(check_result_str))
                completed, objective_status = self.check_objective_completion(check_result, objective)
                
            except Exception as e:
                error_msg = f"Error parsing objective check: {str(e)}"
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
                    "current": objective,
                    "index": self.current_objective_index,
                    "total": len(self.plot_objectives),
                    "status": objective_status
                }
            }
            
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error in advance_turn: {str(e)}"
            self.emit_event('error', {"message": error_msg})
            return {"status": "error", "message": error_msg, "dialogue": []}
        
        finally:
            with self.processing_lock:
                self.is_processing = False

    def trigger_next_turn(self):
        """Trigger the next turn in a non-blocking way"""
        with self.processing_lock:
            if (self.is_processing or 
                self.current_objective_index + 1 > len(self.plot_objectives) or 
                self.story_completed):
                return
        
        threading.Thread(target=self.advance_turn).start()

    def player_interrupt(self, player_input):
        """Handle player interruption with new input"""
        with self.processing_lock:
            if self.is_processing:
                self.emit_event('status', {"message": "Already processing. Please wait."})
                return {"status": "waiting", "message": "Already processing", "dialogue": []}
            
            if self.story_completed:
                self.emit_event('status', {"message": "Story is already complete."})
                return {"status": "complete", "message": "Story already complete", "dialogue": []}
                
            self.is_processing = True
            
        try:
            self.emit_event('status', {"message": "Player interrupts"})
            
            # Add player input to history
            interrupt_line = f"{self.player.name}: {player_input}"
            self.add_to_chat_history(interrupt_line)
            
            player_dialogue = {
                "role": self.player.name,
                "content": player_input,
                "type": "player_input"
            }
            self.dialogue_history.append(player_dialogue)
            self.emit_event('dialogue', player_dialogue)
            
            # Save to database
            if self.chat_id:
                sequence = len(self.dialogue_history) - 1
                try:
                    db.add_message(
                        self.chat_id,
                        self.player.name,
                        player_input,
                        "player_input",
                        sequence
                    )
                except Exception as e:
                    self.emit_event('error', {"message": f"Error saving player message: {str(e)}"})
                
                self.save_state_to_db()
                
            # Generate new script
            self.emit_event('director_status', {"status": "directing", "message": "Director is directing..."})
            
            current_obj = self.current_objective()
            if not current_obj:
                self.emit_event('status', {"message": "No current objective."})
                self.story_completed = True
                if self.chat_id:
                    self.save_state_to_db()
                return {"status": "error", "message": "No current objective", "dialogue": []}
                    
            outline_str = self.director.generate_outline(self.context, current_obj)
            outline = json.loads(self._clean_json(outline_str))
            self.last_outline = outline
            
            new_outline = outline.get('new_outline', outline)
            
            script_json = self.director.generate_turn_instructions(self.context, new_outline)
            self.last_script_data = script_json
            
            if self.chat_id:
                self.save_state_to_db()
                
            self.emit_event('director_status', {"status": "idle", "message": ""})
            
            dialogue_lines = self.process_director_script(script_json)
            
            # Check objective completion
            check_result_str = self.director.check_objective(self.full_chat, current_obj)
            
            try:
                check_result = json.loads(self._clean_json(check_result_str))
                completed, _ = self.check_objective_completion(check_result, current_obj)
                
            except Exception as e:
                self.emit_event('error', {"message": f"Error checking objective: {str(e)}"})
            
            result = {
                "status": "success",
                "dialogue": dialogue_lines,
                "player_input": player_input
            }
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing outline after interruption: {str(e)}"
            self.emit_event('error', {"message": error_msg})
            with self.processing_lock:
                self.is_processing = False
            return {"status": "error", "message": error_msg, "dialogue": []}
        finally:
            # Ensure processing flag is reset even if an exception occurs
            with self.processing_lock:
                self.is_processing = False

    def get_state(self):
        """Get current state of the stage"""
        completed = (self.current_objective_index + 1 > len(self.plot_objectives) or self.story_completed)
        
        if self.current_objective_index + 1> len(self.plot_objectives):
            self.story_completed = True
            if self.chat_id:
                self.save_state_to_db()
        
        return {
            "current_objective_index": self.current_objective_index,
            "total_objectives": len(self.plot_objectives),
            "current_objective": self.current_objective(),
            "plot_failure_reason": self.plot_failure_reason,
            "completed": completed,
            "story_completed": completed,
            "dialogue_history": self.dialogue_history
        }
    
    def emit_event(self, event_type, data):
        """Emit an event through Socket.IO if available"""
        if self.socketio:
            self.socketio.emit(event_type, data,room=self.chat_id)
            
    def run_sequence(self):
        """Run through the entire sequence of plot objectives"""
        self.advance_turn()
        return {
            "status": "started",
            "message": "Story sequence started"
        }
        