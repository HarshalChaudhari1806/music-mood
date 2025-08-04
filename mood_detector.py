import cv2
import numpy as np
from fer import FER
import time
from threading import Thread, Lock
import logging

class MoodDetector:
    def __init__(self):
        """Initialize the mood detector with FER (Facial Emotion Recognition)"""
        self.detector = FER(mtcnn=True)
        self.current_mood = "neutral"
        self.mood_confidence = 0.0
        self.mood_history = []
        self.is_detecting = False
        self.mood_lock = Lock()
        self.camera = None
        
        # Enhanced detection parameters - optimized for sad detection
        self.confidence_threshold = 0.20  # Even lower threshold for sad emotions
        self.stability_threshold = 2  # Reduced for faster sad detection
        self.emotion_smoothing = 0.6  # Less smoothing for more responsive sad detection
        
        # Enhanced mood mapping for music categories
        self.mood_mapping = {
            'happy': 'happy',
            'sad': 'sad',
            'angry': 'angry',
            'fear': 'fear',
            'surprise': 'surprise',
            'disgust': 'disgust',
            'neutral': 'neutral'
        }
        
        # Emotion intensity mapping - boosted sad emotion sensitivity
        self.emotion_intensity = {
            'happy': 1.0,
            'surprise': 0.8,
            'neutral': 0.5,
            'disgust': 0.6,
            'fear': 0.7,
            'sad': 1.2,  # Increased sensitivity for sad emotions
            'angry': 1.0
        }
        
        # Special thresholds for different emotions
        self.emotion_thresholds = {
            'sad': 0.15,      # Very low threshold for sad detection
            'happy': 0.25,
            'angry': 0.30,
            'fear': 0.25,
            'surprise': 0.25,
            'disgust': 0.25,
            'neutral': 0.20
        }
        
        # Recent emotion scores for smoothing
        self.emotion_history = {emotion: [] for emotion in self.mood_mapping.keys()}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def start_detection(self, camera_index=0):
        """Start real-time mood detection"""
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                raise Exception("Could not open camera")
            
            self.is_detecting = True
            detection_thread = Thread(target=self._detection_loop, daemon=True)
            detection_thread.start()
            self.logger.info("Mood detection started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start mood detection: {e}")
            return False
    
    def stop_detection(self):
        """Stop mood detection"""
        self.is_detecting = False
        if self.camera:
            self.camera.release()
        self.logger.info("Mood detection stopped")
    
    def _detection_loop(self):
        """Main detection loop running in separate thread"""
        frame_skip = 3  # Process every 3rd frame for better performance
        frame_count = 0
        
        while self.is_detecting and self.camera.isOpened():
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            frame_count += 1
            if frame_count % frame_skip != 0:
                continue
            
            try:
                # Enhance frame quality for better detection
                enhanced_frame = self._enhance_frame(frame)
                
                # Detect emotions in the frame
                emotions = self.detector.detect_emotions(enhanced_frame)
                
                if emotions and len(emotions) > 0:
                    # Process all detected faces and use the most confident one
                    best_emotion_data = self._get_best_emotion_detection(emotions)
                    
                    if best_emotion_data:
                        emotion_scores = best_emotion_data['emotions']
                        
                        # Apply emotion smoothing
                        smoothed_scores = self._smooth_emotions(emotion_scores)
                        
                        # Get dominant emotion with enhanced logic
                        dominant_emotion, confidence = self._get_dominant_emotion(smoothed_scores)
                        
                        # Use emotion-specific thresholds
                        emotion_threshold = self.emotion_thresholds.get(dominant_emotion, self.confidence_threshold)
                        
                        # Update mood if confidence is high enough for this specific emotion
                        if confidence > emotion_threshold:
                            with self.mood_lock:
                                new_mood = self.mood_mapping.get(dominant_emotion, 'neutral')
                                
                                # More lenient stability check for sad emotions
                                if self._is_mood_stable(new_mood, confidence):
                                    self.current_mood = new_mood
                                    self.mood_confidence = confidence
                                    self._update_mood_history(self.current_mood, confidence)
                
            except Exception as e:
                self.logger.error(f"Error in mood detection: {e}")
            
            time.sleep(0.05)  # Faster processing for better responsiveness
    
    def _update_mood_history(self, mood, confidence):
        """Update mood history for trend analysis"""
        timestamp = time.time()
        self.mood_history.append({
            'mood': mood,
            'confidence': confidence,
            'timestamp': timestamp
        })
        
        # Keep only last 50 entries
        if len(self.mood_history) > 50:
            self.mood_history.pop(0)
    
    def _enhance_frame(self, frame):
        """Enhance frame quality for better emotion detection"""
        import cv2
        # Convert to RGB (FER expects RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Apply histogram equalization to improve contrast
        yuv = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2YUV)
        yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
        enhanced = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
        
        return enhanced
    
    def _get_best_emotion_detection(self, emotions):
        """Get the most confident emotion detection from multiple faces"""
        if not emotions:
            return None
        
        # Find the detection with highest overall confidence
        best_detection = None
        best_total_confidence = 0
        
        for detection in emotions:
            emotion_scores = detection['emotions']
            total_confidence = sum(emotion_scores.values())
            
            if total_confidence > best_total_confidence:
                best_total_confidence = total_confidence
                best_detection = detection
        
        return best_detection
    
    def _smooth_emotions(self, emotion_scores):
        """Apply temporal smoothing to emotion scores"""
        smoothed_scores = {}
        
        for emotion, score in emotion_scores.items():
            # Add current score to history
            if emotion in self.emotion_history:
                self.emotion_history[emotion].append(score)
                # Keep only last 5 scores for smoothing
                if len(self.emotion_history[emotion]) > 5:
                    self.emotion_history[emotion].pop(0)
                
                # Apply exponential moving average
                if len(self.emotion_history[emotion]) > 1:
                    weights = [self.emotion_smoothing ** i for i in range(len(self.emotion_history[emotion]))]
                    weights.reverse()
                    
                    weighted_sum = sum(w * s for w, s in zip(weights, self.emotion_history[emotion]))
                    weight_sum = sum(weights)
                    smoothed_scores[emotion] = weighted_sum / weight_sum
                else:
                    smoothed_scores[emotion] = score
            else:
                smoothed_scores[emotion] = score
        
        return smoothed_scores
    
    def _get_dominant_emotion(self, emotion_scores):
        """Get dominant emotion with enhanced logic"""
        if not emotion_scores:
            return 'neutral', 0.0
        
        # Sort emotions by score
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_emotion, primary_score = sorted_emotions[0]
        
        # Check if the primary emotion is significantly stronger than others
        if len(sorted_emotions) > 1:
            secondary_score = sorted_emotions[1][1]
            
            # If primary emotion is not significantly stronger, consider it neutral
            if primary_score - secondary_score < 0.1 and primary_score < 0.4:
                return 'neutral', primary_score
        
        # Apply intensity weighting
        intensity_weighted_score = primary_score * self.emotion_intensity.get(primary_emotion, 0.5)
        
        return primary_emotion, intensity_weighted_score
    
    def _is_mood_stable(self, new_mood, confidence):
        """Check if the mood change is stable enough with special handling for sad emotions"""
        # Special handling for sad emotions - more lenient
        if new_mood == 'sad':
            # Allow sad mood with lower stability requirements
            if confidence > 0.25:
                return True
            # Check if sad appeared recently with any confidence
            recent_moods = [entry['mood'] for entry in self.mood_history[-2:]]
            if 'sad' in recent_moods:
                return confidence > 0.15
        
        # Always allow high confidence detections
        if confidence > 0.7:
            return True
        
        # Check recent history for consistency
        recent_moods = [entry['mood'] for entry in self.mood_history[-3:]]
        
        # If this mood appeared recently, lower the threshold
        if new_mood in recent_moods:
            return confidence > 0.3
        
        # For new moods, require higher confidence
        return confidence > 0.5
    
    def get_current_mood(self):
        """Get the current detected mood"""
        with self.mood_lock:
            return {
                'mood': self.current_mood,
                'confidence': self.mood_confidence,
                'timestamp': time.time()
            }
    
    def get_stable_mood(self, window_seconds=15):
        """Get the most stable mood over a time window with enhanced algorithm"""
        current_time = time.time()
        recent_moods = [
            entry for entry in self.mood_history 
            if current_time - entry['timestamp'] <= window_seconds
        ]
        
        if not recent_moods:
            return self.current_mood
        
        # Enhanced mood stability calculation
        mood_weights = {}
        mood_counts = {}
        total_entries = len(recent_moods)
        
        for i, entry in enumerate(recent_moods):
            mood = entry['mood']
            confidence = entry['confidence']
            
            # Give more weight to recent entries
            time_weight = (i + 1) / total_entries
            
            # Combine confidence and time weighting
            final_weight = confidence * time_weight * self.emotion_intensity.get(mood, 0.5)
            
            if mood in mood_weights:
                mood_weights[mood] += final_weight
                mood_counts[mood] += 1
            else:
                mood_weights[mood] = final_weight
                mood_counts[mood] = 1
        
        if not mood_weights:
            return self.current_mood
        
        # Find the mood with highest weighted score
        best_mood = max(mood_weights.items(), key=lambda x: x[1])
        
        # Require minimum consistency for non-neutral moods
        if best_mood[0] != 'neutral' and mood_counts[best_mood[0]] < 2:
            return 'neutral'
        
        return best_mood[0]
    
    def get_mood_statistics(self):
        """Get statistics about mood detection"""
        if not self.mood_history:
            return {}
        
        mood_counts = {}
        total_confidence = 0
        
        for entry in self.mood_history:
            mood = entry['mood']
            confidence = entry['confidence']
            
            if mood in mood_counts:
                mood_counts[mood] += 1
            else:
                mood_counts[mood] = 1
            
            total_confidence += confidence
        
        avg_confidence = total_confidence / len(self.mood_history)
        
        return {
            'mood_distribution': mood_counts,
            'average_confidence': avg_confidence,
            'total_detections': len(self.mood_history),
            'current_mood': self.current_mood
        }

    def update_sad_sensitivity(self, sensitivity_factor):
        """Update sad emotion detection sensitivity (1.0 = normal, higher = more sensitive)"""
        base_threshold = 0.15
        self.emotion_thresholds['sad'] = max(0.1, base_threshold / sensitivity_factor)
        self.emotion_intensity['sad'] = min(2.0, 1.2 * sensitivity_factor)
        self.logger.info(f"Updated sad sensitivity: threshold={self.emotion_thresholds['sad']:.3f}, intensity={self.emotion_intensity['sad']:.3f}")

    def get_detection_debug_info(self):
        """Get debug information about current detection parameters"""
        return {
            'confidence_threshold': self.confidence_threshold,
            'emotion_thresholds': self.emotion_thresholds,
            'emotion_intensity': self.emotion_intensity,
            'stability_threshold': self.stability_threshold,
            'emotion_smoothing': self.emotion_smoothing,
            'recent_history': self.mood_history[-5:] if self.mood_history else []
        }

    def detect_mood_from_image(self, image_path):
        """Detect mood from a static image file"""
        try:
            image = cv2.imread(image_path)
            emotions = self.detector.detect_emotions(image)
            
            if emotions:
                emotion_scores = emotions[0]['emotions']
                dominant_emotion = max(emotion_scores, key=emotion_scores.get)
                confidence = emotion_scores[dominant_emotion]
                
                return {
                    'mood': self.mood_mapping.get(dominant_emotion, 'neutral'),
                    'confidence': confidence,
                    'all_emotions': emotion_scores
                }
            
            return {'mood': 'neutral', 'confidence': 0.0, 'all_emotions': {}}
            
        except Exception as e:
            self.logger.error(f"Error detecting mood from image: {e}")
            return {'mood': 'neutral', 'confidence': 0.0, 'all_emotions': {}}
