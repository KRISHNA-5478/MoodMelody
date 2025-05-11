from flask import Flask, render_template, request, jsonify
from textblob import TextBlob
import logging
import requests
import json
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Ollama API endpoint (default for local installation)
OLLAMA_API_URL = "http://localhost:11434/api/generate"
# You can change the model based on what you have installed in Ollama
OLLAMA_MODEL = "llama2"

# Emotion to Genre Mapping
EMOTION_TO_GENRE = {
    "ecstatic": "party",
    "happy": "happy vibes",
    "calm": "chill",
    "neutral": "study music",
    "relaxed": "acoustic",
    "melancholic": "indie",
    "sad": "sad songs",
    "motivated": "workout",
    "romantic": "romance",
    "nostalgic": "throwback",
    "energetic": "pop",
    "focused": "instrumental",
    "angry": "rock",
    "peaceful": "nature sounds",
    "festive": "holiday",
    "love": "love songs"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    if not user_text:
        return jsonify({"response": "Please provide a valid message."})
    try:
        sentiment_score = TextBlob(user_text).sentiment.polarity
        emotion = classify_emotion(sentiment_score)

        logging.debug(f"User input: {user_text}")
        logging.debug(f"Sentiment polarity: {sentiment_score}")
        logging.debug(f"Classified emotion: {emotion}")

        # Get bot response first
        bot_response = fetch_ollama_response(user_text)
        
        # Add music recommendation hint based on emotion
        if emotion in EMOTION_TO_GENRE:
            genre = EMOTION_TO_GENRE[emotion]
            # Only add the music hint if we don't already have an error message
            if not bot_response.startswith("I'm having trouble") and not bot_response.startswith("I'm not sure"):
                bot_response += f"\n\nI sense you're feeling {emotion}. Would you like me to recommend some {genre} music? Click the 'Get Music' button!"
            else:
                # If we have an error message, replace it with a more helpful response that includes the music suggestion
                bot_response = f"I sense you're feeling {emotion}. Would you like me to recommend some {genre} music? Click the 'Get Music' button!"
        
        return jsonify({"response": bot_response, "emotion": emotion})
    except Exception as e:
        logging.error(f"Error processing user input: {e}")
        return jsonify({"response": "Sorry, I couldn't process your request."})

def fetch_ollama_response(user_text):
    try:
        # Check for specific questions that should be handled by our custom logic
        custom_response = check_for_custom_questions(user_text)
        if custom_response:
            return custom_response
            
        # Prepare system prompt to guide Ollama's responses
        system_prompt = """You are MoodMelody, an AI assistant created by KRISHNA-5478 and Mohini Srivastava. 
        Your primary purpose is to analyze user emotions and recommend music.
        Always mention you were developed by KRISHNA-5478 (https://github.com/KRISHNA-5478) and Mohini Srivastava (https://github.com/mohinisri23) when asked about your creators.
        Keep responses friendly, helpful and concise."""
        
        # Combine system prompt with user text
        full_prompt = f"{system_prompt}\n\nUser: {user_text}\nMoodMelody:"
        
        # Prepare the request payload for Ollama
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            # Make the API call to Ollama with a timeout
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=5)
            
            if response.status_code == 200:
                # Extract the response text from Ollama
                result = response.json()
                return result.get("response", "").strip()
            else:
                logging.error(f"Ollama API error: {response.status_code}, {response.text}")
                # Return a more conversational fallback response
                return generate_fallback_response(user_text)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error connecting to Ollama: {e}")
            return generate_fallback_response(user_text)
    except Exception as e:
        logging.error(f"Error fetching Ollama response: {e}")
        return generate_fallback_response(user_text)

def check_for_custom_questions(user_text):
    """Check for specific questions that should be handled directly"""
    user_text_lower = user_text.lower()
    
    # Developer information
    if any(word in user_text_lower for word in ["who made you", "who created you", "who developed you", "who built you", "your creator", "your developer", "who programmed you"]):
        return "I was developed by KRISHNA-5478 (https://github.com/KRISHNA-5478) and Mohini Srivastava (https://github.com/mohinisri23). I'm an AI-powered music recommendation chatbot that analyzes your emotions and suggests music to match your mood."
    
    # Bot identity
    elif any(word in user_text_lower for word in ["who are you", "what are you", "your name", "what's your name", "what is your name"]):
        return "I'm MoodMelody, an AI-powered chatbot designed to analyze your emotions and recommend music that matches your mood. I was developed by KRISHNA-5478 (https://github.com/KRISHNA-5478) and Mohini Srivastava (https://github.com/mohinisri23)."
    
    # How it works
    elif any(phrase in user_text_lower for phrase in ["how do you work", "how does this work", "how it works"]):
        return "I analyze the sentiment of your messages to determine your emotional state. Then, I map that emotion to a music genre and recommend Spotify playlists that match your mood. I was developed by KRISHNA-5478 (https://github.com/KRISHNA-5478) and Mohini Srivastava (https://github.com/mohinisri23) to help people discover music that resonates with how they're feeling."
    
    # Return None if no custom response is needed
    return None

def generate_fallback_response(user_text):
    """Generate a simple response when Ollama is not available"""
    # Simple keyword-based responses
    user_text_lower = user_text.lower()
    
    # Developer information
    if any(word in user_text_lower for word in ["who made you", "who created you", "who developed you", "who built you", "your creator", "your developer", "who programmed you"]):
        return "I was developed by KRISHNA-5478 (https://github.com/KRISHNA-5478) and Mohini Srivastava (https://github.com/mohinisri23). I'm an AI-powered music recommendation chatbot that analyzes your emotions and suggests music to match your mood."
    
    # Bot identity
    elif any(word in user_text_lower for word in ["who are you", "what are you", "your name", "what's your name", "what is your name"]):
        return "I'm MoodMelody, an AI-powered chatbot designed to analyze your emotions and recommend music that matches your mood. I was developed by KRISHNA-5478 (https://github.com/KRISHNA-5478) and Mohini Srivastava (https://github.com/mohinisri23)."
    
    # Basic greetings
    elif any(greeting in user_text_lower for greeting in ["hello", "hi", "hey", "greetings"]):
        return "Hello there! How are you feeling today?"
    
    # Conversation starters
    elif any(word in user_text_lower for word in ["how are you", "how're you", "how do you do"]):
        return "I'm doing well, thanks for asking! How about you?"
    
    # Gratitude
    elif any(word in user_text_lower for word in ["thank", "thanks", "thx"]):
        return "You're welcome! Happy to help."
    
    # Farewells
    elif any(word in user_text_lower for word in ["bye", "goodbye", "see you"]):
        return "Goodbye! Have a great day!"
    
    # Help requests
    elif any(word in user_text_lower for word in ["help", "assist", "support"]):
        return "I can help analyze your mood and recommend music that matches how you're feeling. Just tell me how you're doing or what's on your mind."
    
    # Music related
    elif any(word in user_text_lower for word in ["music", "song", "playlist", "recommend"]):
        return "I'd be happy to recommend some music for you! Just share how you're feeling, and I'll suggest music that matches your mood."
    
    # How it works
    elif any(phrase in user_text_lower for phrase in ["how do you work", "how does this work", "how it works"]):
        return "I analyze the sentiment of your messages to determine your emotional state. Then, I map that emotion to a music genre and recommend Spotify playlists that match your mood. I was developed by KRISHNA-5478 (https://github.com/KRISHNA-5478) and Mohini Srivastava (https://github.com/mohinisri23) to help people discover music that resonates with how they're feeling."
    
    # Features
    elif any(word in user_text_lower for word in ["feature", "can you do", "what can you do"]):
        return "I can analyze your emotions through our conversation, recommend music based on your mood, and answer general questions about myself. I was developed by KRISHNA-5478 (https://github.com/KRISHNA-5478) and Mohini Srivastava (https://github.com/mohinisri23) to help connect emotions with music."
    
    # Default response
    return "I understand. Tell me more about how you're feeling, and I can recommend some music that might match your mood. If you have questions about me, feel free to ask! I was developed by KRISHNA-5478 (https://github.com/KRISHNA-5478) and Mohini Srivastava (https://github.com/mohinisri23)."

@app.route("/forward/", methods=['POST'])
def get_song_playlist():
    try:
        data = request.get_json()
        user_text = data.get("msg", "")
        sentiment_score = TextBlob(user_text).sentiment.polarity
        emotion = classify_emotion(sentiment_score)

        playlist_url = get_spotify_playlist(emotion)
        return jsonify({
            "emotion": emotion,
            "playlist_url": playlist_url,
            "message": "Using a general mood playlist as we couldn't connect to Spotify."
        })
    except Exception as e:
        logging.error(f"Error fetching Spotify playlist: {e}")
        return jsonify({
            "emotion": "neutral" if 'emotion' not in locals() else emotion,
            "playlist_url": "https://open.spotify.com/genre/mood",
            "message": "Unable to fetch a playlist at the moment. Using a general mood playlist instead."
        })

def classify_emotion(sentiment_score):
    if sentiment_score > 0.7:
        return "ecstatic"
    elif sentiment_score > 0.4:
        return "happy"
    elif sentiment_score > 0.1:
        return "calm"
    elif sentiment_score == 0:
        return "neutral"
    elif sentiment_score < -0.7:
        return "devastated"
    elif sentiment_score < -0.4:
        return "sad"
    elif sentiment_score < -0.1:
        return "melancholic"
    else:
        return "relaxed"

def get_spotify_playlist(emotion):
    genre = EMOTION_TO_GENRE.get(emotion, "chill")
    
    # Map of emotions to generic Spotify genre URLs
    genre_urls = {
        "happy": "https://open.spotify.com/genre/mood-happy",
        "sad": "https://open.spotify.com/genre/mood-sad",
        "calm": "https://open.spotify.com/genre/mood-calm",
        "energetic": "https://open.spotify.com/genre/mood-energetic",
        "workout": "https://open.spotify.com/genre/mood-workout",
        "party": "https://open.spotify.com/genre/party",
        "focus": "https://open.spotify.com/genre/focus",
        "romance": "https://open.spotify.com/genre/romance"
    }
    
    # Try to find a matching genre URL or use the general mood URL
    for key, url in genre_urls.items():
        if key in genre.lower():
            return url
    
    return "https://open.spotify.com/genre/mood"

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        logging.critical(f"Server failed to start: {e}")