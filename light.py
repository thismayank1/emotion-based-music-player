import cv2

def nolight():
    """Capture frame from webcam with error handling"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False, None
        
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return False, None
        
    return True, frame