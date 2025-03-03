from flask_restful import Resource, Api, marshal_with, fields, reqparse, marshal
from flask import request, jsonify, g, Response
import threading


# def setup_api(api, socketio):
#     # Add resources to the API with keyword arguments
#     # api.add_resource(StageResource, '/api/stage', '/api/stage/<string:session_id>', 
#     #                 resource_class_kwargs={'socketio': socketio})
#     pass