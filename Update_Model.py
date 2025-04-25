import cv2
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_sets(emotions, dataset_dir):
    training_data = []
    training_labels = []
    
    for emotion in emotions:
        path = f"{dataset_dir}/{emotion}"
        if not os.path.exists(path):
            continue
            
        for image in os.listdir(path):
            try:
                img = cv2.imread(f"{path}/{image}", 0)
                if img is None:
                    continue
                training_data.append(img)
                training_labels.append(emotions.index(emotion))
            except Exception as e:
                logger.error(f"Error processing {path}/{image}: {e}")
    
    return training_data, training_labels

def update(emotions, dataset_dir="dataset", model_path="model2.xml"):
    logger.info("Updating model...")
    try:
        training_data, training_labels = make_sets(emotions, dataset_dir)
        
        if not training_data:
            logger.error("No training data found")
            return False
            
        model = cv2.face.FisherFaceRecognizer_create()
        model.train(np.asarray(training_data), np.asarray(training_labels))
        model.save(model_path)
        logger.info("Model updated successfully")
        return True
    except Exception as e:
        logger.error(f"Model update failed: {e}")
        return False