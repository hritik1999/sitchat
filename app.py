from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api
from application.api import api

# instantiate the app
app = Flask(__name__)
web_api = Api(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


web_api.add_resource(api.test, '/test')

if __name__ == '__main__':
    app.run()