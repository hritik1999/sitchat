import json
import re
import time
import threading
import math
from application.database.db import db
from application.play.player import Player
from application.play.actor import Actor
from application.play.director import Director
from application.ai.llm import actor_llm, director_llm


class Stage:
    def __init__(self, actors=None, director=None, socketio=None, chat_id=None):
        """Initialize a Stage with actors/director or load from database with chat_id"""
        self.socketio = socketio
        self._gen = 0
        self.dialogue_history = []
        self.is_processing = False

        # Thread management and cancellation
        self.active_threads = {}                    # Track active threads by ID
        self.cancellation_event = threading.Event() # Event for signaling cancellation
        self.next_turn_timer = None                 # Handle to the next-turn timer

        # Story state
        self.story_completed = False
        self.player = None
        self.player_interrupted = False
        self.plot_objectives = []
        self.current_objective_index = 0
        self.context = ""
        self.plot_failure_reason = ''
        self.chat_summary = ''
        self.last_script_data = None
        self.last_outline = None
        self.background = ''
        self.chat_id = None

        if chat_id:
            try:
                self._load_from_database(chat_id)
            except Exception as e:
                print(f"Error loading chat: {str(e)}")
                self.emit_event('error', {"message": f"Error loading chat: {str(e)}"}, self._gen)
                raise
        else:
            self.actors = actors
            self.director = director

    def _parse_json_field(self, field):
        try:
            if isinstance(field, str):
                return json.loads(field)
            return field or []
        except json.JSONDecodeError:
            return []

    def _load_from_database(self, chat_id):
        """Load stage data from database with error handling"""
        self.chat_id = chat_id
        chat_data = db.get_chat(chat_id)
        if not chat_data:
            raise ValueError(f"Chat with ID {chat_id} not found in database")

        self.current_objective_index = chat_data.get('current_objective_index', 0)
        self.plot_failure_reason = chat_data.get('plot_failure_reason', '')
        self.context = chat_data.get('context', '')
        self.chat_summary = chat_data.get('chat_summary', '')
        self.last_script_data = chat_data.get('last_script_data')
        self.last_outline = chat_data.get('last_outline')
        self.story_completed = chat_data.get('story_completed', False) or chat_data.get('completed', False)

        player_name = chat_data.get('player_name', 'Player')
        player_description = chat_data.get('player_description', '')
        self.player = Player(name=player_name, description=player_description)

        episode_id = chat_data.get('episode_id')
        episode_data = db.get_episode(episode_id)
        if not episode_data:
            raise ValueError(f"Episode with ID {episode_id} not found in database")

        self.plot_objectives = self._parse_json_field(episode_data.get('plot_objectives', '[]'))
        if self.chat_summary:
            self.background = self.chat_summary
        else:
            self.background = episode_data.get('background', '')

        show_id = episode_data.get('show_id')
        show_data = db.get_show(show_id)
        if not show_data:
            raise ValueError(f"Show with ID {show_id} not found in database")

        self.show = show_data.get('name', '')
        self.description = show_data.get('description', '')

        characters = self._parse_json_field(show_data.get('characters', '[]'))
        relations = show_data.get('relations', '')
        self.actors = {}
        for character in characters:
            char_name = character.get('name') if isinstance(character, dict) else character.name
            char_desc = character.get('description') if isinstance(character, dict) else character.description
            self.actors[char_name] = Actor(char_name, char_desc, relations, self.background, actor_llm)

        self.director = Director(director_llm, self.show, self.description,
                                 self.background, self.actors, self.player, relations)

        messages = db.get_messages(self.chat_id)
        if messages:
            self.dialogue_history = []
            for msg in messages:
                self.dialogue_history.append({'role': msg['role'], 'content': msg['content'], 'type': msg['type']})
                if msg['type'] != 'system':
                    prefix = 'Narration:' if msg['type']=='narration' else msg['role']+':'
                    line = f"{prefix} {msg['content']}"

    def _clean_json(self, json_str):
        cleaned = json_str.strip()
        if cleaned.startswith("```") and cleaned.endswith("```"):
            cleaned = cleaned.strip("`").strip()
        lines = cleaned.split("\n")
        if lines and lines[0].lower().startswith('json'):
            cleaned = "\n".join(lines[1:])
        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)
        return cleaned

    def save_state_to_db(self):
        if not self.chat_id:
            self.emit_event('error', {"message": "Cannot save state: no chat_id provided"}, self._gen)
            return False
        chat_data = {
            'current_objective_index': self.current_objective_index,
            'plot_failure_reason': self.plot_failure_reason,
            'context': self.context,
            'chat_summary': self.chat_summary,
            'last_script_data': self.last_script_data,
            'last_outline': self.last_outline,
            'story_completed': self.story_completed
        }
        try:
            db.update_chat(self.chat_id, chat_data)
            return True
        except Exception as e:
            print(f"Error saving state: {str(e)}")
            self.emit_event('error', {"message": f"Error saving state: {str(e)}"}, self._gen)
            return False

    def emit_event(self, event_type, data, gen):
        # only emit if this worker is still on the current generation
        if gen == self._gen and self.socketio:
            try:
                self.socketio.emit(event_type, data, room=self.chat_id)
            except Exception:
                print(f"Error emitting event: {event_type}")

    def _cancel_all_operations(self):
        """Cancel all running operations and clear pending timer"""
        my_gen = self._gen
        self.cancellation_event.set()
        if self.next_turn_timer:
            self.next_turn_timer.cancel()
            self.next_turn_timer = None
        self.is_processing = False

        for tid, thread_info in list(self.active_threads.items()):
            if thread_info['type'] in ['advance_turn', 'turn_thread']:
                self.active_threads.pop(tid, None)
        # notify only old generation
        self.emit_event('status', {"message": "Processing interrupted and stopped"}, my_gen)
        for role in self.actors:
            self.emit_event('typing_indicator', {"role": role, "status": "idle"}, my_gen)
            self.emit_event('typing_indicator', {"role": role.lower(), "status": "idle"}, my_gen)
        self.emit_event('typing_indicator', {"role": "Narration", "status": "idle"},my_gen)
        self.emit_event('director_status', {"status": "idle", "message": ""}, my_gen)
        self.emit_event('status', {"message": "Scene reset for player input"}, my_gen)

    def process_director_script(self, script_json, gen):
        dialogue_lines = []
        try:
            script_str = self._clean_json(script_json)
            script_data = json.loads(script_str)
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {script_json}")
            script_data = {"scripts": []}
        seq = len(self.dialogue_history)

        for index, line in enumerate(script_data.get('scripts', [])):
            # drop out if cancelled or superseded
            if self.cancellation_event.is_set() or gen != self._gen:
                return dialogue_lines

            role = line.get('role', '')
            instructions = line.get('instruction') or line.get('content', '')

            if role.lower() == (self.player.name.lower() if self.player else 'player'):
                self.emit_event('player_action', {"role": role,
                                                  "content": instructions,
                                                  "type": "player_prompt",
                                                  "wait_for_response": True}, gen)
                start = time.time()
                while time.time() - start < 10:
                    if self.cancellation_event.is_set() or gen != self._gen:
                        return dialogue_lines
                    time.sleep(0.1)

            elif role.lower() in [actor.name.lower() for actor in self.actors.values()]:
                self.emit_event('typing_indicator', {"role": role, "status": "typing"}, gen)
                actor = self.actors.get(role) or self.actors.get(role.lower())
                reply = actor.reply(self.context, instructions)
                db.add_message(self.chat_id, role, reply, "actor_dialogue", seq)

                # simulate typing delay
                if index != 0:
                    start = time.time()
                    while time.time() - start < math.floor(len(reply.split()) / 2.5):
                        if self.cancellation_event.is_set() or gen != self._gen:
                            self.emit_event('typing_indicator', {"role": role, "status": "typing"}, gen)
                            return dialogue_lines
                        time.sleep(0.1)

                entry = {"role": role, "content": reply, "type": "actor_dialogue"}
                dialogue_lines.append(entry)
                self.dialogue_history.append(f"{role}: {reply}")
                self.context = f"{self.context}\n{role}: {reply}" if self.context else f"{role}: {reply}"
                self.emit_event('typing_indicator', {"role": role, "status": "idle"}, gen)
                self.emit_event('dialogue', entry, gen)
                seq += 1

            elif role.lower() == 'narration':
                self.emit_event('typing_indicator', {"role": "Narration", "status": "typing"}, gen)
                content = line.get('content', '')
                entry = {"role": "Narration", "content": content, "type": "narration"}
                dialogue_lines.append(entry)
                self.dialogue_history.append(f"Narration: {content}")
                self.context = f"{self.context}\nNarration: {content}" if self.context else f"Narration: {content}"
                db.add_message(self.chat_id, "Narration", content, "narration", seq)
                self.emit_event('typing_indicator', {"role": "Narration", "status": "idle"}, gen)
                self.emit_event('dialogue', entry, gen)
                seq += 1

            else:
                # other roles
                self.emit_event('typing_indicator', {"role": role, "status": "typing"}, gen)
                actor = Actor(role, '', '', self.background, actor_llm)
                reply = actor.reply(self.context, instructions)
                db.add_message(self.chat_id, role, reply, "other", seq)

                if index != 0:
                    start = time.time()
                    while time.time() - start < math.floor(len(reply.split()) / 2.5):
                        if self.cancellation_event.is_set() or gen != self._gen:
                            self.emit_event('typing_indicator', {"role": role, "status": "typing"}, gen)
                            return dialogue_lines
                        time.sleep(0.1)

                entry = {"role": role, "content": reply, "type": "other"}
                dialogue_lines.append(entry)
                self.dialogue_history.append(f"{role}: {reply}")
                self.context = f"{self.context}\n{role}: {reply}" if self.context else f"{role}: {reply}"
                self.emit_event('typing_indicator', {"role": role, "status": "idle"}, gen)
                self.emit_event('dialogue', entry, gen)
                seq += 1

        if self.chat_id:
            self.save_state_to_db()
        return dialogue_lines

    def trigger_next_turn(self):
        """Trigger next turn in its own thread"""
        # don't start if another run is in progress or cancelled
        if self.cancellation_event.is_set() or self.is_processing:
            return

        # capture generation
        my_gen = self._gen
        self.is_processing = True
        # clear any old cancellation
        self.cancellation_event.clear()

        def run():
            tid = threading.get_ident()
            self.active_threads[tid] = {'type': 'turn_thread', 'start_time': time.time()}

            # drop out if superseded
            if my_gen != self._gen:
                self.is_processing = False
                return

            # perform the turn
            self.advance_turn(my_gen)

            # cleanup
            self.is_processing = False
            self.active_threads.pop(tid, None)

        threading.Thread(target=run, daemon=True).start()

    def advance_turn(self, gen):
        """Advance the game turn based on current objective or handle player interrupt"""
        # if another generation has been triggered, skip
        if gen != self._gen:
            return
        
        current_thread_id = threading.current_thread().ident
        self.active_threads[current_thread_id] = {
            'type': 'advance_turn',
            'start_time': time.time()
        }

        try:
            if self.cancellation_event.is_set() or gen != self._gen:
                return {"status": "cancelled", "message": "Turn cancelled by player", "dialogue": []}

            self.emit_event('director_status', {"status": "directing", "message": "Director is directing..."}, gen)

            # check completion
            if self.current_objective_index >= len(self.plot_objectives):
                self.story_completed = True
                if self.chat_id:
                    self.save_state_to_db()
                self.emit_event('status', {"message": "No current objective. Story complete."}, gen)
                self.emit_event('objective_status', {
                    "message": "All objectives have been completed! Story is finished.",
                    "index": self.current_objective_index,
                    "total": len(self.plot_objectives),
                    "final": True,
                    "story_completed": True
                }, gen)
                return {"status": "complete", "message": "Story complete", "dialogue": []}

            # outline generation or reuse
            self.emit_event('director_status', {"status": "directing", "message": "Director is writing next scene..."}, gen)
            if not self.plot_failure_reason and not self.player_interrupted:
                outline_str = self.director.generate_outline(self.context, self.plot_objectives[self.current_objective_index])
                outline = json.loads(self._clean_json(outline_str))
                self.context = ''
                self.director.background = self.chat_summary
                for actor_name in self.actors:
                    self.actors[actor_name].background = self.chat_summary
            else:
                outline = self.last_outline if isinstance(self.last_outline, dict) else json.loads(self._clean_json(self.last_outline))

            # writing next scene
            self.last_outline = outline
            self.chat_summary = outline.get('previous_outline', '')

            # cue actors
            if self.player_interrupted:
                self.emit_event('director_status',{'status': 'directing', 'message': 'Director is reseting script for your input..'}, gen)
                self.player_interrupted = False
            else:
                self.emit_event('director_status', {"status": "directing", "message": "Director is cueing the actors..."}, gen)
            script_json = self.director.generate_turn_instructions(self.context, outline.get('new_outline', outline), self.plot_failure_reason)

            # process script
            self.emit_event('director_status', {"status": "idle", "message": ""}, gen)
            dialogue_lines = self.process_director_script(script_json, gen)

            if self.cancellation_event.is_set() or gen != self._gen:
                return dialogue_lines

            # check objective
            self.emit_event('director_status', {"status": "directing", "message": "Checking objective completion..."}, gen)
            check_str = self.director.check_objective(self.context, self.plot_objectives[self.current_objective_index])
            self.emit_event('director_status', {"status": "idle", "message": ""}, gen)
            check = json.loads(self._clean_json(check_str))
            completed = check.get('completed', False)
            if completed:
                self.plot_failure_reason = ''
                self.current_objective_index += 1
                self.story_completed = (self.current_objective_index == len(self.plot_objectives))
            else:
                self.plot_failure_reason = check.get('reason', '')

            objective_status = {
                "completed": completed,
                "reason": self.plot_failure_reason,
                "error": False,
                "index": self.current_objective_index,
                "total": len(self.plot_objectives),
                "final": self.story_completed,
                "story_completed": self.story_completed
            }
            self.emit_event('objective_status', objective_status, gen)
            self.save_state_to_db()

            result = {
                "status": "success",
                "dialogue": dialogue_lines,
                "objective": {
                    "current": self.plot_objectives[self.current_objective_index - (0 if completed else 0)],
                    "index": self.current_objective_index,
                    "total": len(self.plot_objectives),
                    "status": objective_status
                }
            }
            return result

        except Exception as e:
            error_msg = f"Unexpected error in advance_turn: {str(e)}"
            print(error_msg)
            self.emit_event('error', {"message": error_msg}, gen)
            return {'status': 'error', 'dialogue': []}

        finally:
            # schedule next normal turn
            if (self.current_objective_index < len(self.plot_objectives)
                    and not self.cancellation_event.is_set()
                    and gen == self._gen):
                self.next_turn_timer = threading.Timer(0.1, self.trigger_next_turn)
                self.next_turn_timer.daemon = True
                self.next_turn_timer.start()

    def player_interrupt(self, player_input):
        """Handle player interruption and trigger an immediate response"""
        # notify old gen
        self.emit_event('director_status', {'status': 'directing', 'message': 'Director is resetting for your input...'}, self._gen)
        # cancel old work
        self._cancel_all_operations()
        # bump generation so old threads won't emit
        self._gen += 1
        # clear any lingering cancel flag
        self.cancellation_event.clear()
        self.player_interrupted = True

        # record player input
        player_name = self.player.name
        entry = {"role": player_name, "content": player_input, "type": "player_input"}
        self.context = f"{self.context}\n{player_name}: {player_input}" if self.context else f"{player_name}: {player_input}"
        self.dialogue_history.append(entry)
        if self.chat_id:
            try:
                db.add_message(self.chat_id, player_name, player_input, "player_input", len(self.dialogue_history) - 1)
                self.save_state_to_db()
            except Exception as e:
                print(f"Error saving player input: {str(e)}")
                self.emit_event('error', {"message": f"Error saving player input: {str(e)}"}, self._gen)

        # start the new turn right away
        self.trigger_next_turn()