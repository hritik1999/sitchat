from flask_restful import Resource, Api, marshal_with, fields, reqparse, marshal
from flask import request, jsonify, g, Response, session
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
            return {"error": "Unauthorized. Please login again"}, 401

        # Get user data from the database
        user = db.get_user(user_id)
        if not user:
            return {"error": "User not found"}, 404
        user_shows = db.get_shows_by_creator(user_id)
        user_episodes = db.get_episodes_by_creator(user_id)
        user_achievements = db.get_achievements(user_id=user_id)
        # Return the user data as a JSON response
        return jsonify({"user": user, "user_shows": user_shows, "user_episodes": user_episodes, "user_achievements": user_achievements})
    
    def put(self):
        """Update user profile including avatar"""
        try:
            # Get current user from the token
            user_id = get_current_user()
            if not user_id:
                return {"error": "Unauthorized.Please login again"}, 401

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
        """Create a new show with character images"""
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401

        # Parse form and files
        form_data = request.form.get('data')
        if not form_data:
            return {"error": "No form data provided"}, 400
        try:
            data = json.loads(form_data)
        except json.JSONDecodeError:
            return {"error": "Invalid form data format"}, 400

        # Validate and upload main show image
        public_urls = {}
        if 'image' not in request.files:
            return {"error": "No image file provided"}, 400
        file = request.files['image']
        if file.filename == '':
            return {"error": "No selected file"}, 400
        allowed = {'png','jpg','jpeg','gif'}
        ext = file.filename.rsplit('.',1)[-1].lower()
        if ext not in allowed:
            return {"error": "Invalid file type"}, 400
        filename = f"{uuid.uuid4()}.{ext}"
        tmp = os.path.join('/tmp', filename)
        file.save(tmp)
        with open(tmp,'rb') as f:
            content = f.read()
        res = db.supabase.storage.from_('show-images').upload(path=filename, file=content)
        os.remove(tmp)
        if getattr(res, 'error', None):
            return {"error": f"Upload failed: {res.error}"}, 500
        pub = db.supabase.storage.from_('show-images').get_public_url(filename)
        public_urls['show'] = pub

        # Handle character images
        chars = data.get('characters', [])
        for idx, char in enumerate(chars):
            key = f"characters[{idx}].image"
            if key in request.files:
                cfile = request.files[key]
                if cfile and cfile.filename:
                    cext = cfile.filename.rsplit('.',1)[-1].lower()
                    if cext not in allowed:
                        return {"error": f"Invalid file type for character {idx}"}, 400
                    cname = f"{uuid.uuid4()}.{cext}"
                    tmp_c = os.path.join('/tmp', cname)
                    cfile.save(tmp_c)
                    with open(tmp_c,'rb') as cf:
                        ccontent = cf.read()
                    cres = db.supabase.storage.from_('show-images').upload(path=cname, file=ccontent)
                    os.remove(tmp_c)
                    if getattr(cres, 'error', None):
                        return {"error": f"Character {idx} upload failed: {cres.error}"}, 500
                    cpub = db.supabase.storage.from_('show-images').get_public_url(cname)
                    char['image_url'] = cpub
            # else leave char as-is if no file provided

        # Create show record
        try:
            show = db.create_show(
                creator_id=user_id,
                name=data.get('name'),
                description=data.get('description'),
                characters=chars,
                relations=data.get('relations',''),
                image_url=public_urls['show']
            )
        except Exception as e:
            return {"error": f"Database problem: {str(e)}"}, 500

        if not show:
            return {"error": "Failed to create show"}, 500
        return jsonify({"show": show})
class ShowResource(Resource):
    def get(self, show_id):
        """Get a specific show by ID"""
        show = db.get_show(show_id)
        if not show:
            return {"error": "Show not found"}, 404
        
        return jsonify({"show": show})
    
    def put(self, show_id):
        """Update a show with character images"""
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401
        show = db.get_show(show_id)
        if not show or show.get('creator_id') != user_id:
            return {"error": "Not authorized to edit this show"}, 403

        form_data = request.form.get('data')
        if not form_data:
            return {"error": "No form data provided"}, 400
        try:
            data = json.loads(form_data)
        except json.JSONDecodeError:
            return {"error": "Invalid form data format"}, 400

        # Initialize update payload
        update_chars = data.get('characters', [])
        allowed = {'png','jpg','jpeg','gif'}

        # Handle main image replacement
        public_url = show.get('image_url')
        if 'image' in request.files:
            mf = request.files['image']
            if mf and mf.filename:
                ext = mf.filename.rsplit('.',1)[-1].lower()
                if ext not in allowed:
                    return {"error": "Invalid file type"}, 400
                fname = f"{uuid.uuid4()}.{ext}"
                tmp = os.path.join('/tmp', fname)
                mf.save(tmp)
                with open(tmp,'rb') as f:
                    cont = f.read()
                mres = db.supabase.storage.from_('show-images').upload(path=fname, file=cont)
                os.remove(tmp)
                if getattr(mres,'error',None):
                    return {"error": f"Upload failed: {mres.error}"}, 500
                public_url = db.supabase.storage.from_('show-images').get_public_url(fname)
                # cleanup old main image
                try:
                    old = show.get('image_url').split('/')[-1]
                    db.supabase.storage.from_('show-images').remove(old)
                except: pass

        # Handle character images replacement
        for idx, char in enumerate(update_chars):
            key = f"characters[{idx}].image"
            if key in request.files:
                cf = request.files[key]
                if cf and cf.filename:
                    cext = cf.filename.rsplit('.',1)[-1].lower()
                    if cext not in allowed:
                        return {"error": f"Invalid file type for character {idx}"}, 400
                    cname = f"{uuid.uuid4()}.{cext}"
                    tmp_c = os.path.join('/tmp', cname)
                    cf.save(tmp_c)
                    with open(tmp_c,'rb') as f:
                        ccont = f.read()
                    cres = db.supabase.storage.from_('show-images').upload(path=cname, file=ccont)
                    os.remove(tmp_c)
                    if getattr(cres,'error',None):
                        return {"error": f"Character {idx} upload failed: {cres.error}"}, 500
                    new_pub = db.supabase.storage.from_('show-images').get_public_url(cname)
                    char['image_url'] = new_pub
                    # Optionally delete old character image

        # Build update data
        update_data = {
            'name': data.get('name'),
            'description': data.get('description'),
            'characters': update_chars,
            'relations': data.get('relations',''),
        }
        if public_url != show.get('image_url'):
            update_data['image_url'] = public_url

        try:
            updated_show = db.update_show(show_id, update_data)
            if not updated_show:
                return {"error": "Failed to update show"}, 500
            return jsonify({"show": updated_show})
        except Exception as e:
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
        # Verify authentication
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401
        
        # Verify ownership of the show
        show = db.get_show(show_id)
        if not show:
            return {"error": "Show not found"}, 404
        
        episode = db.create_episode(
            show_id=show_id,
            creator_id=user_id,
            name=data.get('name'),
            description=data.get('description', ''),
            player_role=data.get('player_role', ''),
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
    
    
class ChatResource(Resource):
    def post(self, episode_id):
        """Create a new chat session for an episode"""
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401
            
        data = request.get_json()
        player_name = data.get('player_name', 'Player')
        player_description = data.get('player_description', '')
        chat_speed = data.get('chat_speed', 2.25)
        # Fetch episode details
        episode = db.get_episode(episode_id)
        if not episode:
            return {"error": "Episode not found"}, 404
            
        # Create a new chat in the database
        chat = db.create_chat(
            episode_id=episode_id,
            show_id=episode.get('show_id'),
            user_id=user_id,
            player_name=player_name,
            player_description=player_description,
            chat_speed=chat_speed
        )
        
        if not chat:
            return {"error": "Failed to create chat session"}, 500

        return jsonify({
            "chat": chat,
        })
    
    def get(self, chat_id=None):
        """Get chat sessions"""
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401
        
        # If chat_id is provided, get that specific chat
        if chat_id:
            chat = db.get_chat(chat_id)
            if not chat:
                return {"error": "Chat not found"}, 404
                
            # Verify ownership
            if chat.get('user_id') != user_id:
                return {"error": "Not authorized to access this chat"}, 403
                
            # Get messages for this chat
            messages = db.get_messages(chat_id)

            return jsonify({
                "chat": chat,
                "messages": messages
            })
        
        # Otherwise, get all chats for the user
        chats = db.get_chats(user_id)
        return jsonify({"chats": chats})

class RatingResource(Resource):
    def post(self, episode_id):
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401
        
        data = request.get_json()
        rating = data.get('rating')
        feedback = data.get('feedback')
        if not rating:
            return {"error": "Rating not provided"}, 400
        # get show id
        show_id = db.get_episode(episode_id).get('show_id')
        success = db.add_rating(episode_id,show_id, user_id, rating,feedback)
        if not success:
            return {"error": "Failed to add rating"}, 500
        
        return {"success": True}, 201
    
    def get(self, episode_id):
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401
        
        show_id = db.get_episode(episode_id).get('show_id')
        if not show_id:
            return {"error": "Episode not found"}, 404
        
        rating = db.get_rating(episode_id, show_id, user_id)
        if not rating:
            return {"message":"No rating by user"}, 200
        
        return {"rating": rating}, 200
    
class AchievementsResource(Resource):
    def get(self,chat_id):
        user_id = get_current_user()
        if not user_id:
            return {"error": "Unauthorized. Please login again"}, 401
        achievements = db.get_achievements(chat_id=chat_id)
        return jsonify({"achievements": achievements})
    
class LeaderboardResource(Resource):
    def get(self):
        leaderboard = db.get_all_users()
        return jsonify({"leaderboard": leaderboard})
        
    