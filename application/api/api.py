from flask_restful import Resource, Api, marshal_with, fields, reqparse, marshal
from flask import request, jsonify, g, Response
from application.ai.llm import actor_llm, director_llm
from application.play.actor import Actor
from application.play.director import Director
from application.play.player import Player
from application.play.stage import Stage 

# Store active stage sessions
active_stages = {}


class StageResource(Resource):
    def __init__(self, **kwargs):
        self.socketio = kwargs.get('socketio')
        super().__init__()
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
        
        return jsonify({
            'session_id': session_id,
            'message': 'Stage created successfully',
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
    def __init__(self, **kwargs):
        self.socketio = kwargs.get('socketio')
        super().__init__()
    def post(self, session_id):
        """Advance the turn for a stage session"""
        if session_id not in active_stages:
            return {'error': 'Session not found'}, 404
            
        stage = active_stages[session_id]
        result = stage.advance_turn()
        
        return jsonify({
            'session_id': session_id,
            'result': result,
            'state': stage.get_state()
        })
    
class PlayerInterruptResource(Resource):
    def __init__(self, **kwargs):
        self.socketio = kwargs.get('socketio')
        super().__init__()
    def post(self, session_id):
        """Handle a player interruption"""
        if session_id not in active_stages:
            return {'error': 'Session not found'}, 404
            
        data = request.get_json()
        player_input = data.get('player_input', '')
        
        stage = active_stages[session_id]
        result = stage.player_interrupt(player_input)
        
        return jsonify({
            'session_id': session_id,
            'result': result,
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