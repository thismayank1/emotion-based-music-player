import cv2
import os
import logging
import eel
import pygame
import threading
import random
import fnmatch
import time  # Added missing import
from light import nolight
from Update_Model import update

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    "model_path": "model2.xml",
    "haarcascade_path": cv2.data.haarcascades + 'haarcascade_frontalface_default.xml',
    "songs_dir": os.path.join("WD", "songs"),
    "emotions": ["angry", "happy", "sad", "neutral"],
    "emotion_songs": {
        "happy": ["ban ja rani.mp3", "Banduk meri laila.mp3"],
        "sad": ["barish.mp3", "phir bhi.mp3"],
        "angry": ["mercy.mp3", "o sathi.mp3"],
        "neutral": ["ik vari aa.mp3", "main tera.mp3"]
    }
}

# Initialize components
eel.init('WD')
face_cascade = cv2.CascadeClassifier(CONFIG["haarcascade_path"])
fishface = cv2.face.FisherFaceRecognizer_create()

# Global variables
current_emotion = None
current_song = None
is_playing = False
camera_active = False

def get_available_songs():
    """Get list of available songs in the songs directory"""
    try:
        return [f for f in os.listdir(CONFIG["songs_dir"]) if f.lower().endswith('.mp3')]
    except Exception as e:
        logger.error(f"Error reading songs directory: {e}")
        return []

def detect_emotion_from_frame(frame):
    """Detect emotion from a captured frame"""
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 1:
            (x,y,w,h) = faces[0]
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (350, 350))
            
            # Predict emotion
            fishface.read(CONFIG["model_path"])
            pred, conf = fishface.predict(face)
            emotion = CONFIG["emotions"][pred]
            logger.info(f"Detected emotion: {emotion} (confidence: {conf})")
            return emotion
    except Exception as e:
        logger.error(f"Emotion detection error: {e}")
    return None

def play_song_for_emotion(emotion):
    """Play a random song matching the detected emotion"""
    global current_song, current_emotion, is_playing
    
    try:
        if emotion not in CONFIG["emotion_songs"]:
            logger.warning(f"No songs defined for emotion: {emotion}")
            eel.show_alert(f"No songs configured for {emotion} mood")
            return False
            
        available_songs = get_available_songs()
        matched_songs = []
        
        # Match songs using fnmatch patterns
        for pattern in CONFIG["emotion_songs"][emotion]:
            matched_songs.extend(
                song for song in available_songs 
                if fnmatch.fnmatch(song.lower(), pattern.lower())
            )
        
        if not matched_songs:
            logger.warning(f"No matching songs found for emotion: {emotion}")
            eel.show_alert(f"No songs found for {emotion} mood")
            return False
            
        song_file = random.choice(matched_songs)
        song_path = os.path.join(CONFIG["songs_dir"], song_file)
        
        pygame.mixer.init()
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        
        current_song = song_file
        current_emotion = emotion
        is_playing = True
        
        eel.update_player(emotion, song_file)
        logger.info(f"Now playing: {song_file} for {emotion}")
        return True
        
    except Exception as e:
        logger.error(f"Error playing song: {e}")
        eel.show_alert(f"Playback error: {str(e)}")
        return False

@eel.expose
def start_emotion_detection():
    """Start the emotion detection process"""
    global camera_active
    
    if camera_active:
        return {"status": "error", "message": "Detection already running"}
    
    camera_active = True
    detection_thread = threading.Thread(target=run_detection)
    detection_thread.daemon = True
    detection_thread.start()
    return {"status": "success"}

def run_detection():
    """Main detection loop"""
    global camera_active
    
    try:
        eel.update_status("Starting camera...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            eel.show_alert("Could not access camera")
            logger.error("Failed to open camera")
            return
            
        eel.update_status("Detecting emotions...")
        logger.info("Emotion detection started")
        
        while camera_active:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to capture frame")
                continue
                
            emotion = detect_emotion_from_frame(frame)
            if emotion:
                if play_song_for_emotion(emotion):
                    # Wait for 10 seconds or until detection is stopped
                    for _ in range(100):
                        if not camera_active:
                            break
                        time.sleep(0.1)
                
    except Exception as e:
        logger.error(f"Detection error: {e}")
        eel.show_alert(f"Detection error: {str(e)}")
    finally:
        if 'cap' in locals():
            cap.release()
        camera_active = False
        cv2.destroyAllWindows()
        eel.update_status("Ready")

@eel.expose
def stop_detection():
    """Stop the emotion detection"""
    global camera_active
    camera_active = False
    return {"status": "success"}

@eel.expose
def get_player_status():
    """Get current player status"""
    return {
        "emotion": current_emotion,
        "song": current_song,
        "is_playing": is_playing
    }

def main():
    """Initialize and start the application"""
    try:
        # Load or train model
        if not os.path.exists(CONFIG["model_path"]):
            logger.info("Training emotion model...")
            update(CONFIG["emotions"])
            
        # Start web interface
        eel.start('main.html', size=(1000, 800), position=(100, 100))
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        pygame.mixer.quit()

if __name__ == "__main__":
    main()