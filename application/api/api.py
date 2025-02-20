from flask_restful import Resource, Api, marshal_with, fields, reqparse, marshal
from flask import request, jsonify, g, Response


class test(Resource):

    def get(self):
        return 'ok'