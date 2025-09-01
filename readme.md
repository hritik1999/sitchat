# SitChat

An interactive storytelling platform where you can experience your favorite shows.

## Features

- **One-Click Show Creation**: Create existing shows with one click or new shows by providing show details and character information
- **Flexible Episode Creation**: Generate episodes with a single idea and one click, or by defining a sequential list of plot objectives
- **AI Group Experience**: Join an AI group chat to experience episodes from start to finish
- **Achievement System**: Earn achievements based on your interactions and compete on the leaderboard

## Future Plans

- **Voice Mode**: Add voice models and voice cloning capabilities
- **Podcast Mode**: Allow users to listen to episodes in audio format
- **Video Mode**: Create full 20-minute videos using Nano Banana, Veo 3, and advanced prompt engineering

## Tech Stack

- **Frontend**: Vue.js with Tailwind CSS and shadcn/vue for styling
- **Backend**: Flask
- **Database & Auth**: Supabase
- **LLM**: OpenAI

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js and npm
- Supabase account
- OpenAI API key

### Backend Setup

1. **Set up Python environment**
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Set environment variables**
Create a .env file in your project root and add:
```bash 
    SUPABASE_URL=your_supabase_project_url
    SUPABASE_KEY=your_supabase_anon_key
    OPENAI_API_KEY=your_openai_api_key
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the Flask backend**
```bash
python app.py
```


### Frontend Setup

1. **Navigate to the frontend directory**
```bash
cd frontend 
```
2. **Install Node.js dependencies**
```bash
npm install
```
3. **Start the development server**
```bash
npm run dev
```

### Access the Application

Frontend: http://localhost:5173 (or the port shown in your terminal)

Backend API: http://localhost:5000 (or your configured Flask port)

### Contributing
We welcome contributions! Please feel free to submit a Pull Request.
