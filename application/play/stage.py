import json
import re
import time
import threading
from application.ai.llm import actor_llm, director_llm
from application.play.actor import Actor
from application.play.director import Director
from application.play.player import Player
from application.database.db import db

class Stage:
    def __init__(self, actors, director, player, plot_objectives, socketio=None):
        """
        actors: dict mapping actor names to Actor objects.
        director: a Director object (with check_objective method).
        player: a Player object.
        plot_objectives: list of plot objective strings.
        socketio: Socket.IO instance for real-time communication.
        """
        self.actors = actors
        self.director = director
        self.player = player
        self.plot_objectives = plot_objectives
        self.current_objective_index = 0
        self.context = ""
        self.plot_failure_reason = ''
        self.chat_summary = ''
        self.full_chat = ''
        self.last_script_data = None
        self.last_outline = None
        self.socketio = socketio
        self.dialogue_history = []
        self.is_processing = False  # Flag to prevent concurrent processing
        self.processing_lock = threading.Lock()  # Lock for thread safety
        self.story_completed = False  # Flag to track if the story is complete
        self.chat_id = None  # Database reference ID for persistence
        self.next_message_sequence = 0  # For tracking message sequence in the database

    def add_to_chat_history(self, text):
        if self.context:
            self.context += "\n" + text
        else:
            self.context = text

    def current_objective(self):
        if self.current_objective_index < len(self.plot_objectives):
            return self.plot_objectives[self.current_objective_index]
        return None
    
    def _clean_json(self, json_str):
        """
        Remove markdown fences and trailing commas from a JSON string.
        """
        cleaned = json_str.strip()
        # Remove markdown fences if present.
        if cleaned.startswith("```") and cleaned.endswith("```"):
            cleaned = cleaned.strip("```").strip()
            
        # Check if there's a json prefix line
        lines = cleaned.split("\n")
        if lines and lines[0].lower().startswith('json'):
            cleaned = "\n".join(lines[1:])
            
        # Remove trailing commas before a closing brace/bracket.
        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)
        return cleaned
    
    def check_objective_completion(self, check_result, current_obj):
        """
        Check if an objective has been completed and handle the transition
        """
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
                "story_completed": is_final  # Add this flag for the frontend
            }
            
            # Emit the updated status
            self.emit_event('objective_status', objective_status)
            
            # Update database if we have a chat_id
            if self.chat_id:
                try:
                    db.update_chat(self.chat_id, {
                        'current_objective_index': self.current_objective_index,
                        'completed': is_final
                    })
                except Exception as e:
                    print(f"Error updating chat progress in database: {str(e)}")
            
            # If there are more objectives, trigger the next turn
            if not is_final:
                def schedule_next_turn():
                    with self.processing_lock:
                        self.is_processing = False
                    self.trigger_next_turn()
                    
                schedule_next_turn()
            else:
                # Mark the story as completed
                self.story_completed = True
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
                with self.processing_lock:
                    self.is_processing = False
            
            return True, objective_status
        else:
            # Continue with the current objective
            self.plot_failure_reason = 'Plot objective not met due to the following reason: ' + check_result.get('reason', '') + ' Please make the plot so it is addressed and the plot objective is completed'
            
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
            
            return False, objective_status


    def process_director_script(self, script_json):
        """
        Process the JSON script generated by the director.
        Adds realistic typing delays and indicators.
        """        
        try:
            script_str = self._clean_json(script_json)
            script_data = json.loads(script_str)
        except Exception as e:
            self.emit_event('error', {"message": f"Error parsing director script JSON: {str(e)}"})
            script_data = {"scripts": []}
        
        dialogue_lines = []
        
        for line in script_data.get("scripts", []):
            role = line.get("role", "")
            # For actor lines, check for "instruction" then fallback to "content"
            instructions = line.get("instruction", "") or line.get("content", "")
                
            if role in self.actors:
                # Show typing indicator
                self.emit_event('typing_indicator', {
                    "role": role,
                    "status": "typing",
                })
                
                # Add artificial delay to simulate typing
                time.sleep(2)
                
                actor = self.actors[role]
                # Update the actor's chat_history dynamically before calling reply.
                reply_output = actor.reply(self.context, instructions)
                dialogue_line = f"{role}: {reply_output}"
                self.add_to_chat_history(dialogue_line)
                self.full_chat += "\n" + dialogue_line
                
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
                
                # Emit the dialogue line through Socket.IO if available
                self.emit_event('dialogue', dialogue_entry)
                
                # Save to database if we have a chat_id
                if self.chat_id:
                    try:
                        db.add_message(
                            chat_id=self.chat_id,
                            role=role,
                            content=reply_output,
                            type="actor_dialogue",
                            sequence=self.next_message_sequence
                        )
                        self.next_message_sequence += 1
                    except Exception as e:
                        print(f"Error saving message to database: {str(e)}")
                
            elif role.lower() == "narration":
                # Show narration is being added
                self.emit_event('typing_indicator', {
                    "role": "Narration",
                    "status": "typing",
                })
                
                
                content = line.get('content', instructions)
                dialogue_line = f"Narration: {content}"
                self.add_to_chat_history(dialogue_line)
                self.full_chat += "\n" + dialogue_line
                
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
                self.emit_event('dialogue', dialogue_entry)
                
                # Save to database if we have a chat_id
                if self.chat_id:
                    try:
                        db.add_message(
                            chat_id=self.chat_id,
                            role="Narration",
                            content=content,
                            type="narration",
                            sequence=self.next_message_sequence
                        )
                        self.next_message_sequence += 1
                    except Exception as e:
                        print(f"Error saving narration to database: {str(e)}")
                
            else:
                # Unrecognized role; treat as narration.
                self.emit_event('typing_indicator', {
                    "role": role,
                    "status": "typing",
                })
                
                time.sleep(1)
                
                dialogue_line = f"{role}: {instructions}"
                self.add_to_chat_history(dialogue_line)
                self.full_chat += "\n" + dialogue_line
                
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
                self.emit_event('dialogue', dialogue_entry)
                
                # Save to database if we have a chat_id
                if self.chat_id:
                    try:
                        db.add_message(
                            chat_id=self.chat_id,
                            role=role,
                            content=instructions,
                            type="other",
                            sequence=self.next_message_sequence
                        )
                        self.next_message_sequence += 1
                    except Exception as e:
                        print(f"Error saving dialogue to database: {str(e)}")
        
        # Store the dialogue history for API access
        self.dialogue_history.extend(dialogue_lines)
        return dialogue_lines

    def advance_turn(self):
        """
        Advance the game turn based on the current objective.
        Returns dialogue lines generated during this turn.
        """
        # Use a lock to ensure thread safety
        with self.processing_lock:
            if self.is_processing:
                self.emit_event('status', {"message": "Already processing a turn. Please wait."})
                return {"status": "waiting", "message": "Already processing a turn", "dialogue": []}
            
            # Don't proceed if the story is already completed
            if self.story_completed:
                self.emit_event('status', {"message": "Story is already complete. No more turns."})
                return {"status": "complete", "message": "Story already complete", "dialogue": []}
                
            self.is_processing = True
        
        try:
            objective = self.current_objective()
            if not objective:
                # Mark the story as completed
                self.story_completed = True
                self.emit_event('status', {"message": "No current objective. Story complete."})
                # Send a clear completion event to the frontend
                self.emit_event('objective_status', {
                    "completed": True,
                    "message": "All objectives have been completed! Story is finished.",
                    "index": self.current_objective_index,
                    "total": len(self.plot_objectives),
                    "final": True,
                    "story_completed": True  # Add this flag to indicate story completion
                })
                
                # Update database if we have a chat_id
                if self.chat_id:
                    try:
                        db.update_chat(self.chat_id, {
                            'current_objective_index': self.current_objective_index,
                            'completed': True
                        })
                    except Exception as e:
                        print(f"Error updating chat completion in database: {str(e)}")
                
                with self.processing_lock:
                    self.is_processing = False
                return {"status": "complete", "message": "Story complete", "dialogue": []}

            # Emit event that director is working
            self.emit_event('director_status', {"status": "directing", "message": "Director is directing..."})
            
            # Director generates an outline based on the current chat history and current plot objective
            outline_str = self.director.generate_outline(self.context, objective, self.plot_failure_reason)
            
            try:
                outline = json.loads(self._clean_json(outline_str))
                self.last_outline = outline
                self.chat_summary = outline.get('previous_outline')

                # Updating the background to include the summary and clearing the chat history to reduce context window
                self.context = ''
                self.director.background = self.chat_summary
                for actor in self.actors:
                    self.actors[actor].background = self.chat_summary
                    
                # Get the new outline from the result
                new_outline = outline.get('new_outline', outline)  # Fallback to the entire outline
                
                # Director generates turn instructions (script) based on the outline
                script_json = self.director.generate_turn_instructions(self.context, new_outline)
                self.last_script_data = script_json

                # Director is done, about to process lines
                self.emit_event('director_status', {"status": "idle", "message": ""})
                
                # Process the script and get the dialogue lines
                dialogue_lines = self.process_director_script(script_json)
                
            except Exception as e:
                error_msg = f"Error processing outline: {str(e)}"
                self.emit_event('error', {"message": error_msg})
                with self.processing_lock:
                    self.is_processing = False
                return {"status": "error", "message": error_msg, "dialogue": []}

            # Check if the objective has been reached using the director's check_objective method
            check_result_str = self.director.check_objective(self.full_chat, objective)
            objective_status = {}
            
            try:
                check_result = json.loads(self._clean_json(check_result_str))
                completed, objective_status = self.check_objective_completion(check_result, objective)
                
            except Exception as e:
                error_msg = f"Error parsing objective check result: {str(e)}"
                self.emit_event('error', {"message": error_msg})
                objective_status = {
                    "completed": False,
                    "message": error_msg,
                    "error": True
                }
                with self.processing_lock:
                    self.is_processing = False
                
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
            
            # Note: Don't reset is_processing here if we're scheduling the next turn
            # It will be reset in the scheduled function
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error in advance_turn: {str(e)}"
            self.emit_event('error', {"message": error_msg})
            with self.processing_lock:
                self.is_processing = False
            return {"status": "error", "message": error_msg, "dialogue": []}

    def trigger_next_turn(self):
        """Helper method to trigger the next turn in a non-blocking way"""
        with self.processing_lock:
            # Don't start a new turn if:
            # 1. We're already processing something
            # 2. We've reached or exceeded the number of objectives
            # 3. The story has been explicitly marked as completed
            if (self.is_processing or 
                self.current_objective_index >= len(self.plot_objectives) or 
                self.story_completed):
                return
        
        # Use threading to make this non-blocking
        threading.Thread(target=self.advance_turn).start()

    def player_interrupt(self, player_input):
        """
        Handle a player interruption.
        """
        with self.processing_lock:
            if self.is_processing:
                self.emit_event('status', {"message": "Already processing. Please wait before interrupting."})
                return {"status": "waiting", "message": "Already processing", "dialogue": []}
            
            # Don't allow player interruption if the story is already completed
            if self.story_completed:
                self.emit_event('status', {"message": "Story is already complete. No more interactions."})
                return {"status": "complete", "message": "Story already complete", "dialogue": []}
                
            self.is_processing = True
            
        try:
            self.emit_event('status', {"message": "Player interrupts"})
            
            # Add the player's input to the chat history
            interrupt_line = f"{self.player.name}: {player_input}"
            self.add_to_chat_history(interrupt_line)
            
            # Add to dialogue history for frontend
            player_dialogue = {
                "role": self.player.name,
                "content": player_input,
                "type": "player_input"
            }
            self.dialogue_history.append(player_dialogue)
            self.emit_event('dialogue', player_dialogue)
            
            # Save to database if we have a chat_id
            if self.chat_id:
                try:
                    db.add_message(
                        chat_id=self.chat_id,
                        role=self.player.name,
                        content=player_input,
                        type="player_input",
                        sequence=self.next_message_sequence
                    )
                    self.next_message_sequence += 1
                except Exception as e:
                    print(f"Error saving player input to database: {str(e)}")
            
            # Show that director is working
            self.emit_event('director_status', {"status": "directing", "message": "Director is directing..."})
            
            # After the interruption, ask the director to generate a new outline and script
            current_obj = self.current_objective()
            if not current_obj:
                self.emit_event('status', {"message": "No current objective to continue after interruption."})
                self.story_completed = True  # Mark as completed if there's no objective
                
                # Update database if we have a chat_id
                if self.chat_id:
                    try:
                        db.update_chat(self.chat_id, {
                            'current_objective_index': self.current_objective_index,
                            'completed': True
                        })
                    except Exception as e:
                        print(f"Error updating chat completion in database: {str(e)}")
                
                with self.processing_lock:
                    self.is_processing = False
                return {"status": "error", "message": "No current objective", "dialogue": []}
                    
            outline_str = self.director.generate_outline(self.context, current_obj)
            outline = json.loads(self._clean_json(outline_str))
            self.last_outline = outline
            
            new_outline = outline.get('new_outline', outline)
            
            script_json = self.director.generate_turn_instructions(self.context, new_outline)
            self.last_script_data = script_json
            
            # Director is done working
            self.emit_event('director_status', {"status": "idle", "message": ""})
            
            dialogue_lines = self.process_director_script(script_json)
            
            # Check objective completion
            check_result_str = self.director.check_objective(self.full_chat, current_obj)
            
            try:
                check_result = json.loads(self._clean_json(check_result_str))
                completed, _ = self.check_objective_completion(check_result, current_obj)
                
            except Exception as e:
                self.emit_event('error', {"message": f"Error checking objective: {str(e)}"})
                with self.processing_lock:
                    self.is_processing = False
            
            result = {
                "status": "success",
                "dialogue": dialogue_lines,
                "player_input": player_input
            }
            
            # Note: is_processing flag is reset in scheduled functions or above on error
            return result
            
        except Exception as e:
            error_msg = f"Error processing outline after interruption: {str(e)}"
            self.emit_event('error', {"message": error_msg})
            with self.processing_lock:
                self.is_processing = False
            return {"status": "error", "message": error_msg, "dialogue": []}

    def get_state(self):
        """
        Get the current state of the stage for API responses.
        """
        # Calculate completed status
        completed = (self.current_objective_index >= len(self.plot_objectives) or 
                    self.story_completed)
        
        # If index exceeds or equals objectives count, explicitly mark as completed
        if self.current_objective_index >= len(self.plot_objectives):
            self.story_completed = True  # Ensure this flag is set
        
        return {
            "current_objective_index": self.current_objective_index,
            "total_objectives": len(self.plot_objectives),
            "current_objective": self.current_objective(),
            "plot_failure_reason": self.plot_failure_reason,
            "completed": completed,
            "story_completed": completed,  # Add this explicit flag
            "dialogue_history": self.dialogue_history,
            "chat_id": self.chat_id  # Include database reference if available
        }
    
    def emit_event(self, event_type, data):
        """
        Emit an event through Socket.IO if available.
        """
        if self.socketio:
            self.socketio.emit(event_type, data)
            
    def run_sequence(self):
        """
        Run through the entire sequence of plot objectives.
        This is an API-friendly version of run_stage.
        """
        # We don't need to check is_processing here since advance_turn will do it
        
        # Just start the first turn, the rest will be triggered automatically
        result = self.advance_turn()
        
        # If we have a chat_id, ensure we save the initial dialogue
        if self.chat_id and result.get('dialogue'):
            try:
                messages = []
                for idx, msg in enumerate(result['dialogue']):
                    messages.append({
                        'chat_id': self.chat_id,
                        'role': msg['role'],
                        'content': msg['content'],
                        'type': msg['type'],
                        'sequence': idx
                    })
                
                if messages:
                    db.add_messages_batch(self.chat_id, messages)
            except Exception as e:
                print(f"Error saving initial dialogue to database: {str(e)}")
        
        return {
            "status": "started",
            "message": "Story sequence started"
        }
    
    def load_chat_history(self):
        """
        Load chat history from the database if a chat_id is available
        """
        if not self.chat_id:
            return False
        
        try:
            # Get the messages for this chat
            messages = db.get_messages(self.chat_id)
            
            if not messages:
                return False
            
            # Add messages to dialogue history
            self.dialogue_history = []
            self.context = ""
            self.full_chat = ""
            
            for msg in messages:
                dialogue_entry = {
                    "role": msg['role'],
                    "content": msg['content'],
                    "type": msg['type']
                }
                self.dialogue_history.append(dialogue_entry)
                
                # Add to chat context
                dialogue_line = f"{msg['role']}: {msg['content']}"
                self.add_to_chat_history(dialogue_line)
                self.full_chat += "\n" + dialogue_line
            
            # Set the next message sequence
            self.next_message_sequence = len(messages)
            
            return True
            
        except Exception as e:
            print(f"Error loading chat history from database: {str(e)}")
            return False