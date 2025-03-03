from flask_restful import Resource, Api, marshal_with, fields, reqparse, marshal
from flask import request, jsonify, g, Response
import threading
from application.database.db import db
from application.auth.auth import get_current_user
import os
import uuid
import json

class ShowsResource(Resource):
    def get(self):
        """Get a list of all shows"""
        shows = db.get_shows()
        return jsonify({"shows": shows})
        
    def post(self):
        """Create a new show"""
        # Get current user from the token
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized"}, 401
            
        # Check if image file is provided
        if 'image' not in request.files:
            return {"error": "No image file provided"}, 400
            
        # Get the image file
        file = request.files['image']
        if file.filename == '':
            return {"error": "No selected file"}, 400
            
        # Get form data from the 'data' field
        form_data = request.form.get('data')
        if not form_data:
            return {"error": "No form data provided"}, 400
            
        # Parse the JSON data
        try:
            data = json.loads(form_data)
        except json.JSONDecodeError:
            return {"error": "Invalid form data format"}, 400
            
        # Validate file type (accept only images)
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in file.filename or \
           file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return {"error": "Invalid file type"}, 400
            
        try:
            # Create a unique filename
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{str(uuid.uuid4())}.{file_ext}"
            
            # Save file temporarily
            temp_path = os.path.join('/tmp', filename)
            file.save(temp_path)
            
            # Upload to Supabase storage
            with open(temp_path, 'rb') as f:
                file_content = f.read()
                
            # Upload to 'show-images' bucket
            result = db.supabase.storage.from_('show-images').upload(
                path=filename,
                file=file_content
            )
            
            # Clean up temp file
            os.remove(temp_path)
            
            # Check for Supabase storage errors
            if result and hasattr(result, 'error') and result.error:
                return {"error": f"Upload failed: {result.error}"}, 500
                
            # Get public URL
            public_url = db.supabase.storage.from_('show-images').get_public_url(filename)
            
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return {"error": f"Upload failed: {str(e)}"}, 500
        
        try:
            # Create the show in the database
            show = db.create_show(
                creator_id=user_id,
                name=data.get('name'),
                description=data.get('description'),
                characters=data.get('characters', []),
                relations=data.get('relations', ''),
                image_url=public_url
            )
        except Exception as e:
            print(f"database error:{str(e)}")
            return {"error":f'database problem: {str(e)}'}, 500

        
        if not show:
            return {"error": "Failed to create show"}, 500
            
        return jsonify({"show": show})
class ShowResource(Resource):
    def get(self, show_id):
        """Get a specific show by ID"""
        show = db.get_show(show_id)
        print(show)
        if not show:
            return {"error": "Show not found"}, 404
        
        return jsonify({"show": show})
    
    def put(self, show_id):
        """Update a show"""
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized"}, 401
        
        data = request.get_json()
        
        # Verify ownership
        show = db.get_show(show_id)
        if not show or show.get('creator_id') != user_id:
            return {"error": "Not authorized to edit this show"}, 403
        
        updated_show = db.update_show(show_id, data)
        
        if not updated_show:
            return {"error": "Failed to update show"}, 500
        
        return jsonify({"show": updated_show})
    
    def delete(self, show_id):
        """Delete a show"""
        user_id = get_current_user()
        
        # Verify ownership
        show = db.get_show(show_id)
        if not show or show.get('creator_id') != user_id:
            return {"error": "Not authorized to delete this show"}, 403
        
        success = db.delete_show(show_id)
        
        if not success:
            return {"error": "Failed to delete show"}, 500
        
        return {"success": True}
    
class EpisodesResource(Resource):
    def get(self, show_id):
        """Get all episodes for a show"""
        episodes = db.get_episodes(show_id)
        return jsonify({"episodes": episodes})

    def post(self, show_id):
        """Create a new episode for a show"""
        user_id = get_current_user()
        data = request.get_json()
        print(data)
        # Verify authentication
        if not user_id:
            return {"error": "Unauthorized"}, 401
        
        # Verify ownership of the show
        show = db.get_show(show_id)
        if not show:
            return {"error": "Show not found"}, 404
        
        episode = db.create_episode(
            show_id=show_id,
            creator_id=user_id,
            name=data.get('name'),
            description=data.get('description', ''),
            background=data.get('background', ''),
            plot_objectives=data.get('plot_objectives', [])
        )
        
        if not episode:
            return {"error": "Failed to create episode"}, 500
        
        return jsonify({"episode": episode})


class EpisodeResource(Resource):
    def get(self, episode_id):
        """Get a specific episode by ID"""
        episode = db.get_episode(episode_id)
        
        if not episode:
            return {"error": "Episode not found"}, 404
        
        return jsonify({"episode": episode})
    
    def put(self, episode_id):
        """Update an episode"""
        user_id = get_current_user()
        data = request.get_json()
        
        # Verify ownership
        episode = db.get_episode(episode_id)
        if not episode or episode.get('creator_id') != user_id:
            return {"error": "Not authorized to edit this episode"}, 403
        
        updated_episode = db.update_episode(episode_id, data)
        
        if not updated_episode:
            return {"error": "Failed to update episode"}, 500
        
        return jsonify({"episode": updated_episode})
    
    def delete(self, episode_id):
        """Delete an episode"""
        user_id = get_current_user()
        
        # Verify ownership
        episode = db.get_episode(episode_id)
        if not episode or episode.get('creator_id') != user_id:
            return {"error": "Not authorized to delete this episode"}, 403
        
        success = db.delete_episode(episode_id)
        
        if not success:
            return {"error": "Failed to delete episode"}, 500
        
        return {"success": True}


# def setup_api(api, socketio):
#     # Add resources to the API with keyword arguments
#     # api.add_resource(StageResource, '/api/stage', '/api/stage/<string:session_id>', 
#     #                 resource_class_kwargs={'socketio': socketio})
#     pass