import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any, Union
from flask import g

# Load environment variables
load_dotenv()

class SupabaseDB:
    """
    Supabase database client for sitchat application.
    Handles all database operations for shows, episodes, chats, and messages.
    """
    def __init__(self):
        """Initialize the Supabase client"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and key must be provided in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    # ---- User Operations ----
    
    def get_user(self, user_id: str) -> dict:
        """Get a user by ID"""
        response = self.supabase.table('users').select('*').eq('id', user_id).execute()
        
        if not response.data:
            return None
        
        return response.data[0]
    
    def get_all_users(self) -> List[dict]:
        """Get all users"""
        response = self.supabase.table('users').select('*').execute()
        return response.data
    
    def create_user_profile(self, user_id: str, username: str, avatar_url: Optional[str] = None) -> dict:
        """Create a new user profile after signup"""
        user_data = {
            'id': user_id,
            'username': username,
            'avatar_url': avatar_url
        }
        
        response = self.supabase.table('users').insert(user_data).execute()
        return response.data[0] if response.data else None
    
    def update_user_profile(self, user_id: str, data: dict) -> dict:
        """Update a user's profile"""
        try:            
            # Remove None values from the update data
            update_data = {k: v for k, v in data.items() if v is not None}
            
            # Execute the update
            response = self.supabase.table('users').update(update_data).eq('id', user_id).execute()
            
            if hasattr(response, 'data') and response.data:
                return response.data[0]
            else:
                # Try to fetch the user to see if update actually worked
                get_response = self.supabase.table('users').select('*').eq('id', user_id).execute()
                if hasattr(get_response, 'data') and get_response.data:
                    return get_response.data[0]
            return None
        except Exception as e:
            print(f"Error in update_user_profile: {str(e)}")
            return None
        
    # ---- Show Operations ----
    
    def get_shows(self, limit: int = 20, offset: int = 0) -> List[dict]:
        """Get a list of shows with pagination"""
        response = self.supabase.table('shows') \
            .select('*, users(username)') \
            .order('created_at', desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return response.data
    
    def get_show(self, show_id: str) -> dict:
        """Get a show by ID"""
        response = self.supabase.table('shows') \
            .select('*, users(username)') \
            .eq('id', show_id) \
            .execute()
        
        if not response.data:
            return None
        
        return response.data[0]
    
    def get_shows_by_creator(self, creator_id: str, limit: int = 20, offset: int = 0) -> List[dict]:
        """Get shows created by a specific user"""
        response = self.supabase.table('shows') \
            .select('*') \
            .eq('creator_id', creator_id) \
            .order('created_at', desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return response.data
    
    def create_show(self, creator_id: str, name: str, description: str, 
                   characters: dict, relations: str, image_url: Optional[str] = None) -> dict:
        """Create a new show"""
        show_data = {
            'creator_id': creator_id,
            'name': name,
            'description': description,
            'characters': json.dumps(characters),
            'relations': relations,
            'image_url': image_url
        }
        
        response = self.supabase.table('shows').insert(show_data).execute()
        return response.data[0] if response.data else None
    
    def update_show(self, show_id: str, data: dict) -> dict:
        """Update a show's data"""
        # Convert characters to JSON string if provided
        if 'characters' in data and isinstance(data['characters'], dict):
            data['characters'] = json.dumps(data['characters'])
            
        response = self.supabase.table('shows').update(data).eq('id', show_id).execute()
        return response.data[0] if response.data else None
    
    def delete_show(self, show_id: str) -> bool:
        """Delete a show and all associated episodes and chats"""
        # This would ideally be a transaction, but we'll just do sequential deletes
        # Delete associated episodes first (cascading delete will remove chats and messages)
        self.supabase.table('episodes').delete().eq('show_id', show_id).execute()
        
        # Now delete the show
        response = self.supabase.table('shows').delete().eq('id', show_id).execute()
        return len(response.data) > 0
    
    # ---- Episode Operations ----
    
    def get_episodes(self, show_id: str) -> List[dict]:
        """Get all episodes for a show"""
        response = self.supabase.table('episodes') \
            .select('*') \
            .eq('show_id', show_id) \
            .order('created_at', desc=True) \
            .execute()
        
        return response.data
    
    def get_episode(self, episode_id: str) -> dict:
        """Get an episode by ID"""
        response = self.supabase.table('episodes') \
            .select('*, shows(name, description)') \
            .eq('id', episode_id) \
            .execute()
        
        if not response.data:
            return None
        
        return response.data[0]
    
    def get_episodes_by_creator(self, creator_id: str) -> List[dict]:
        """Get episodes created by a specific user"""
        response = self.supabase.table('episodes') \
            .select('*') \
            .eq('creator_id', creator_id) \
            .order('created_at', desc=True) \
            .execute()
        return response.data
    
    def create_episode(self, show_id: str, creator_id: str, name: str, 
                      description: str,player_role:str, background: str, plot_objectives: list) -> dict:
        """Create a new episode"""
        episode_data = {
            'show_id': show_id,
            'creator_id': creator_id,
            'name': name,
            'description': description,
            'player_role': player_role,
            'background': background,
            'plot_objectives': json.dumps(plot_objectives)
        }
        
        response = self.supabase.table('episodes').insert(episode_data).execute()
        return response.data[0] if response.data else None
    
    def update_episode(self, episode_id: str, data: dict) -> dict:
        """Update an episode's data"""
        # Convert plot_objectives to JSON string if provided
        if 'plot_objectives' in data and isinstance(data['plot_objectives'], list):
            data['plot_objectives'] = json.dumps(data['plot_objectives'])
            
        response = self.supabase.table('episodes').update(data).eq('id', episode_id).execute()
        return response.data[0] if response.data else None
    
    def delete_episode(self, episode_id: str) -> bool:
        """Delete an episode and all associated chats"""
        # Delete associated chats first (cascading delete will remove messages)
        self.supabase.table('chats').delete().eq('episode_id', episode_id).execute()
        
        # Now delete the episode
        response = self.supabase.table('episodes').delete().eq('id', episode_id).execute()
        return len(response.data) > 0
    
    # ---- Chat Operations ----
    
    def get_chats(self, user_id: str = None, episode_id: str = None, limit: int = 20, offset: int = 0) -> List[dict]:
        """Get a list of chats with optional filters"""
        query = self.supabase.table('chats').select('*, episodes(name), users(username)')
        
        if user_id:
            query = query.eq('user_id', user_id)
        
        if episode_id:
            query = query.eq('episode_id', episode_id)
        
        response = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        return response.data
    
    def get_chat(self, chat_id: str) -> dict:
        """Get a chat by ID"""
        response = self.supabase.table('chats') \
            .select('*, episodes(name, plot_objectives, show_id), users(username)') \
            .eq('id', chat_id) \
            .execute()
        
        if not response.data:
            return None
        
        return response.data[0]
    
    def create_chat(self, episode_id: str,show_id: str, user_id: str, player_name: str, player_description: str) -> dict:
        """Create a new chat session"""
        chat_data = {
            'episode_id': episode_id,
            'show_id': show_id,
            'user_id': user_id,
            'player_name': player_name,
            'player_description': player_description,
            'story_completed': False,
            'current_objective_index': 0
        }
        
        response = self.supabase.table('chats').insert(chat_data).execute()
        return response.data[0] if response.data else None
    
    def update_chat(self, chat_id: str, data: dict) -> dict:
        """Update a chat's data (e.g., progress, completion)"""
        response = self.supabase.table('chats').update(data).eq('id', chat_id).execute()
        return response.data[0] if response.data else None
    
    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat and all associated messages"""
        # Delete associated messages first
        self.supabase.table('messages').delete().eq('chat_id', chat_id).execute()
        
        # Now delete the chat
        response = self.supabase.table('chats').delete().eq('id', chat_id).execute()
        return len(response.data) > 0
    
    # ---- Message Operations ----
    
    def get_messages(self, chat_id: str) -> List[dict]:
        """Get all messages for a chat, ordered by sequence"""
        response = self.supabase.table('messages') \
            .select('*') \
            .eq('chat_id', chat_id) \
            .order('sequence', desc=False) \
            .execute()
        
        return response.data
    
    def add_message(self, chat_id: str, role: str, content: str, type: str, sequence: int) -> dict:
        """Add a new message to a chat"""
        message_data = {
            'chat_id': chat_id,
            'role': role,
            'content': content,
            'type': type,
            'sequence': sequence
        }
        
        response = self.supabase.table('messages').insert(message_data).execute()
        return response.data[0] if response.data else None
    
    def add_messages_batch(self, chat_id: str, messages: List[dict]) -> List[dict]:
        """Add multiple messages at once"""
        # Prepare message data
        message_data = []
        for idx, msg in enumerate(messages):
            message_data.append({
                'chat_id': chat_id,
                'role': msg['role'],
                'content': msg['content'],
                'type': msg['type'],
                'sequence': msg.get('sequence', idx)  # Use provided sequence or auto-increment
            })
        
        if not message_data:
            return []
        
        response = self.supabase.table('messages').insert(message_data).execute()
        return response.data
    
    def add_rating(self, episode_id: str,show_id: str, user_id: str,rating: int,feedback: str) -> dict:
        """Add a rating for an episode"""
        rating_data = {
            'episode_id': episode_id,
            'show_id': show_id,
            'rating': rating,
            'user_id': user_id,
            'feedback': feedback,
        }
        
        response = self.supabase.table('ratings').insert(rating_data).execute()
        return response.data[0] if response.data else None
    
    
    def get_rating(self, episode_id: str,show_id: str, user_id: str) -> dict:
        """Get a rating for an episode"""
        response = self.supabase.table('ratings') \
            .select('*') \
            .eq('episode_id', episode_id) \
            .eq('show_id', show_id) \
            .eq('user_id', user_id) \
            .execute()
        
        return response.data[0] if response.data else None
    
    def get_achievements(self, chat_id: str = None, user_id: str = None) -> List[dict]:
        """Get all achievements for a chat"""
        if chat_id:
            response = self.supabase.table('achievements') \
                .select('*') \
                .eq('chat_id', chat_id) \
                .execute()
            return response.data
        if user_id:
            response = self.supabase.table('achievements') \
                .select('*') \
                .eq('user_id', user_id) \
                .execute()
            return response.data
    
    def add_achievement(self, chat_id: str, achievement_title: str,score: int) -> dict:
        """Add an achievement for a user"""
        data = self.supabase.table('chats').select('*').eq('id', chat_id).execute()
        achievement_data = {
            'chat_id': chat_id,
            'user_id': data.data[0]['user_id'],
            'show_id': data.data[0]['show_id'],
            'title': achievement_title,
            'score': score
        }

        response = self.supabase.table('achievements').insert(achievement_data).execute()
        return response.data[0] if response.data else None
    
    # ---- Authentication Operations ----
    
    def sign_up(self, email: str, password: str) -> dict:
        """Register a new user"""
        response = self.supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return response
    
    def sign_in(self, email: str, password: str) -> dict:
        """Sign in a user"""
        response = self.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    
    def sign_out(self) -> None:
        """Sign out the current user"""
        return self.supabase.auth.sign_out()
    
    def get_current_user(self) -> dict:
        """Get the currently authenticated user"""
        return self.supabase.auth.get_user()


# Create a singleton instance
db = SupabaseDB()