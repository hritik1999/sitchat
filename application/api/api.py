from flask_restful import Resource, Api, marshal_with, fields, reqparse, marshal
from flask import request, jsonify, g, Response
import threading
from application.ai.llm import actor_llm, director_llm
from application.play.actor import Actor
from application.play.director import Director
from application.play.player import Player
from application.play.stage import Stage 

# Store active stage sessions
active_stages = {}


class StageResource(Resource):
    def __init__(self, socketio):
        self.socketio = socketio
        
    def post(self):
        """Create a new stage session"""
        data = request.get_json()
        
        show = data.get('show')
        description = data.get('description')
        background = data.get('background')
        actors_data = data.get('actors_data')
        relations = data.get('relations')
        player_name = data.get('player_name', 'Player')
        player_description = data.get('player_description')
        plot_objectives = data.get('plot_objectives')
        
        # Create director
        director = Director(
            director_llm,
            show,
            description, 
            background, 
            actors_data, 
            player_description, 
            relations
        )
        
        # Create actors
        actors = {}
        for name, desc in actors_data.items():
            actors[name] = Actor(
                name=name,
                description=desc,
                relations=relations,  # You may want to filter relations per actor
                background=background,
                llm=actor_llm
            )
        
        # Create player
        player = Player(
            name=player_name,
            description=player_description
        )
        
        # Create and store the stage
        session_id = str(len(active_stages) + 1)  # Simple ID generation
        stage = Stage(
            actors=actors, 
            director=director, 
            player=player, 
            plot_objectives=plot_objectives,
            socketio=self.socketio
        )
        
        active_stages[session_id] = stage
        
        # Start the stage sequence in a background thread to not block the response
        def start_sequence():
            # Give the frontend a moment to connect to the socket before starting
            try:
                import time
                time.sleep(1)  # Simpler than using socketio.sleep which might have event loop issues
                stage.advance_turn()  # Just start the first turn, rest is automatic
            except Exception as e:
                self.socketio.emit('error', {'message': f'Error starting sequence: {str(e)}'})
            
        thread = threading.Thread(target=start_sequence)
        thread.daemon = True  # Make thread a daemon so it won't block app shutdown
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'message': 'Stage created and started automatically',
            'state': stage.get_state()
        })
    
    def get(self, session_id):
        """Get the state of a stage session"""
        if session_id not in active_stages:
            return {'error': 'Session not found'}, 404
            
        stage = active_stages[session_id]
        return jsonify({
            'session_id': session_id,
            'state': stage.get_state()
        })
    
class AdvanceTurnResource(Resource):
    def __init__(self, socketio):
        self.socketio = socketio
        
    def post(self, session_id):
        """
        Manual trigger to advance the turn for a stage session
        Note: With the automatic progression, this should rarely be needed
        """
        if session_id not in active_stages:
            return {'error': 'Session not found'}, 404
            
        stage = active_stages[session_id]
        
        # Start advance_turn in a background thread to not block the response
        def advance_in_background():
            try:
                stage.advance_turn()
            except Exception as e:
                self.socketio.emit('error', {'message': f'Error advancing turn: {str(e)}'})
            
        thread = threading.Thread(target=advance_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'message': 'Turn advancement started',
            'state': stage.get_state()
        })
    
class PlayerInterruptResource(Resource):
    def __init__(self, socketio):
        self.socketio = socketio
        
    def post(self, session_id):
        """Handle a player interruption"""
        if session_id not in active_stages:
            return {'error': 'Session not found'}, 404
            
        data = request.get_json()
        player_input = data.get('player_input', '')
        
        if not player_input.strip():
            return {'error': 'Empty player input'}, 400
            
        stage = active_stages[session_id]
        
        # Handle interrupt in a background thread to not block the response
        def interrupt_in_background():
            try:
                stage.player_interrupt(player_input)
            except Exception as e:
                self.socketio.emit('error', {'message': f'Error processing interruption: {str(e)}'})
            
        thread = threading.Thread(target=interrupt_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'message': 'Player interruption processed',
            'state': stage.get_state()
        })
    
def setup_api(api, socketio):
    # Add resources to the API with keyword arguments
    api.add_resource(StageResource, '/api/stage', '/api/stage/<string:session_id>', 
                    resource_class_kwargs={'socketio': socketio})
    api.add_resource(AdvanceTurnResource, '/api/stage/<string:session_id>/advance',
                    resource_class_kwargs={'socketio': socketio})
    api.add_resource(PlayerInterruptResource, '/api/stage/<string:session_id>/interrupt',
                    resource_class_kwargs={'socketio': socketio})