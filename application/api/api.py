from flask_restful import Resource, Api, marshal_with, fields, reqparse, marshal
from flask import request, jsonify, g, Response
import threading
from application.database.db import db
from application.auth.auth import get_current_user
import os
import uuid
import json

class UserResource(Resource):

    def get(self):
        # Get current user from the token
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized"}, 401

        # Get user data from the database
        user = db.get_user(user_id)
        if not user:
            return {"error": "User not found"}, 404
        user_shows = db.get_shows_by_creator(user_id)
        user_episodes = db.get_episodes_by_creator(user_id)
        # Return the user data as a JSON response
        return jsonify({"user": user, "user_shows": user_shows, "user_episodes": user_episodes})
    
    def put(self):
        """Update user profile including avatar"""
        try:
            # Get current user from the token
            user_id = get_current_user()
            if not user_id:
                return {"error": "Unauthorized"}, 401

            # Get current user data
            current_user = db.get_user(user_id)
            if not current_user:
                return {"error": "User not found"}, 404

            # Get form data
            form_data = request.form.get('data')
            if not form_data:
                return {"error": "No form data provided"}, 400

            # Parse JSON data
            try:
                data = json.loads(form_data)
            except json.JSONDecodeError:
                return {"error": "Invalid form data format"}, 400

            # Initialize avatar_url with existing URL
            avatar_url = current_user.get('avatar_url')

            # Handle avatar upload if provided
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file.filename != '':
                    # Validate file type
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    if '.' not in file.filename or \
                    file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                        return {"error": "Invalid file type"}, 400

                    try:
                        # Create unique filename
                        file_ext = file.filename.rsplit('.', 1)[1].lower()
                        filename = f"{str(uuid.uuid4())}.{file_ext}"
                        
                        # Save file temporarily
                        temp_path = os.path.join('/tmp', filename)
                        file.save(temp_path)

                        # Upload to storage
                        with open(temp_path, 'rb') as f:
                            file_content = f.read()
                        
                        result = db.supabase.storage.from_('show-images').upload(
                            path=filename,
                            file=file_content
                        )

                        # Clean up temp file
                        os.remove(temp_path)

                        if result and hasattr(result, 'error') and result.error:
                            return {"error": f"Upload failed: {result.error}"}, 500

                        # Get public URL for the new avatar
                        avatar_url = db.supabase.storage.from_('show-images').get_public_url(filename)

                        # Delete old avatar if exists
                        if current_user.get('avatar_url'):
                            try:
                                old_filename = current_user['avatar_url'].split('/')[-1]
                                db.supabase.storage.from_('show-images').remove(old_filename)
                            except Exception as e:
                                print(f"Warning: Failed to delete old avatar: {str(e)}")

                    except Exception as e:
                        print(f"Upload error: {str(e)}")
                        return {"error": f"Upload failed: {str(e)}"}, 500

            # Prepare update data
            update_data = {
                'username': data.get('username'),
                'email': data.get('email')
            }
            
            # Only include avatar_url if it has changed
            if avatar_url != current_user.get('avatar_url'):
                update_data['avatar_url'] = avatar_url

            # Update user profile
            updated_user = db.update_user_profile(user_id, update_data)
            
            if updated_user:
                return jsonify({"user": updated_user})
            else:
                # Try to get the user again to confirm the update
                check_user = db.get_user(user_id)
                if check_user:
                    return jsonify({"user": check_user})
                return {"error": "Failed to update user"}, 500

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {"error": f"An error occurred: {str(e)}"}, 500

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

        # Verify ownership
        show = db.get_show(show_id)
        if not show or show.get('creator_id') != user_id:
            return {"error": "Not authorized to edit this show"}, 403

        # Get form data from the 'data' field
        form_data = request.form.get('data')
        if not form_data:
            return {"error": "No form data provided"}, 400

        # Parse the JSON data
        try:
            data = json.loads(form_data)
        except json.JSONDecodeError:
            return {"error": "Invalid form data format"}, 400

        # Initialize public_url with existing image URL
        public_url = show.get('image_url')

        # Handle image upload if provided
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Validate file type
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

                    # Get new public URL
                    public_url = db.supabase.storage.from_('show-images').get_public_url(filename)

                    # Delete old image if it exists
                    if show.get('image_url'):
                        try:
                            old_filename = show['image_url'].split('/')[-1]
                            db.supabase.storage.from_('show-images').remove(old_filename)
                        except Exception as e:
                            print(f"Warning: Failed to delete old image: {str(e)}")

                except Exception as e:
                    print(f"Upload error: {str(e)}")
                    return {"error": f"Upload failed: {str(e)}"}, 500

        # Update the show data
        update_data = {
            'name': data.get('name'),
            'description': data.get('description'),
            'characters': data.get('characters', []),
            'relations': data.get('relations', ''),
        }
        
        # Only update image_url if a new image was uploaded
        if public_url != show.get('image_url'):
            update_data['image_url'] = public_url

        try:
            updated_show = db.update_show(show_id, update_data)
            if not updated_show:
                return {"error": "Failed to update show"}, 500
            return jsonify({"show": updated_show})
        except Exception as e:
            print(f"Database error: {str(e)}")
            return {"error": f"Database problem: {str(e)}"}, 500
    
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
    def get(self,show_id, episode_id):
        """Get a specific episode by ID"""
        episode = db.get_episode(episode_id)
        if not episode:
            return {"error": "Episode not found"}, 404
        
        return jsonify({"episode": episode})
    
    def put(self, show_id, episode_id):
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
    
    def delete(self,show_id, episode_id):
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