import librosa
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd
import pickle
import os
import logging
from pathlib import Path

class MusicAnalyzer:
    def __init__(self):
        """Initialize the music analyzer for automatic mood classification"""
        self.scaler = StandardScaler()
        self.classifier = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=15)
        self.is_trained = False
        
        # Enhanced feature set for better mood classification
        self.feature_names = [
            'tempo', 'tempo_variance',
            'spectral_centroid_mean', 'spectral_centroid_std',
            'spectral_rolloff_mean', 'spectral_rolloff_std',
            'spectral_bandwidth_mean', 'spectral_bandwidth_std',
            'zero_crossing_rate_mean', 'zero_crossing_rate_std',
            'mfcc_1_mean', 'mfcc_1_std', 'mfcc_2_mean', 'mfcc_2_std',
            'mfcc_3_mean', 'mfcc_3_std', 'mfcc_4_mean', 'mfcc_4_std',
            'mfcc_5_mean', 'mfcc_5_std', 'mfcc_6_mean', 'mfcc_6_std',
            'mfcc_7_mean', 'mfcc_7_std',
            'chroma_mean', 'chroma_std', 'chroma_var',
            'tonnetz_mean', 'tonnetz_std',
            'spectral_contrast_mean', 'spectral_contrast_std',
            'rms_energy_mean', 'rms_energy_std',
            'harmonic_mean', 'percussive_mean'
        ]
        
        self.mood_labels = {
            0: 'neutral', 1: 'happy', 2: 'sad', 3: 'angry',
            4: 'fear', 5: 'surprise', 6: 'disgust'
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def extract_features(self, audio_path, duration=30):
        """Extract enhanced audio features from a music file"""
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, duration=duration)
            
            # Extract features
            features = {}
            
            # Tempo and rhythm features
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = tempo
            
            # Tempo variance (rhythm stability)
            if len(beats) > 1:
                beat_times = librosa.frames_to_time(beats, sr=sr)
                tempo_var = np.var(np.diff(beat_times))
                features['tempo_variance'] = tempo_var
            else:
                features['tempo_variance'] = 0
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroid)
            features['spectral_centroid_std'] = np.std(spectral_centroid)
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
            features['spectral_rolloff_std'] = np.std(spectral_rolloff)
            
            # Spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            features['spectral_bandwidth_mean'] = np.mean(spectral_bandwidth)
            features['spectral_bandwidth_std'] = np.std(spectral_bandwidth)
            
            # Zero Crossing Rate
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            features['zero_crossing_rate_mean'] = np.mean(zero_crossing_rate)
            features['zero_crossing_rate_std'] = np.std(zero_crossing_rate)
            
            # Enhanced MFCCs (first 7 coefficients)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=7)
            for i in range(7):
                features[f'mfcc_{i+1}_mean'] = np.mean(mfccs[i])
                features[f'mfcc_{i+1}_std'] = np.std(mfccs[i])
            
            # Chroma features (harmony)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            features['chroma_mean'] = np.mean(chroma)
            features['chroma_std'] = np.std(chroma)
            features['chroma_var'] = np.var(chroma)
            
            # Tonnetz features (tonal space)
            tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
            features['tonnetz_mean'] = np.mean(tonnetz)
            features['tonnetz_std'] = np.std(tonnetz)
            
            # Spectral contrast
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            features['spectral_contrast_mean'] = np.mean(spectral_contrast)
            features['spectral_contrast_std'] = np.std(spectral_contrast)
            
            # RMS Energy
            rms_energy = librosa.feature.rms(y=y)[0]
            features['rms_energy_mean'] = np.mean(rms_energy)
            features['rms_energy_std'] = np.std(rms_energy)
            
            # Harmonic and percussive components
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            features['harmonic_mean'] = np.mean(np.abs(y_harmonic))
            features['percussive_mean'] = np.mean(np.abs(y_percussive))
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting features from {audio_path}: {e}")
            return None
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            features['chroma_mean'] = np.mean(chroma)
            features['chroma_std'] = np.std(chroma)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting features from {audio_path}: {e}")
            return None
    
    def analyze_music_directory(self, music_directory):
        """Analyze all music files in a directory and create training data"""
        music_path = Path(music_directory)
        training_data = []
        
        mood_mapping = {
            'happy': 1, 'sad': 2, 'angry': 3, 'neutral': 0,
            'fear': 4, 'surprise': 5, 'disgust': 6
        }
        
        for mood_dir in music_path.iterdir():
            if mood_dir.is_dir() and mood_dir.name in mood_mapping:
                mood_label = mood_mapping[mood_dir.name]
                
                self.logger.info(f"Analyzing {mood_dir.name} music...")
                
                for audio_file in mood_dir.glob('*'):
                    if audio_file.suffix.lower() in ['.mp3', '.wav', '.ogg', '.m4a']:
                        features = self.extract_features(str(audio_file))
                        
                        if features:
                            features['mood'] = mood_label
                            features['file_path'] = str(audio_file)
                            training_data.append(features)
        
        return pd.DataFrame(training_data)
    
    def train_classifier(self, music_directory, save_model=True):
        """Train the mood classifier on music data"""
        try:
            # Analyze music directory
            self.logger.info("Analyzing music files for training...")
            df = self.analyze_music_directory(music_directory)
            
            if df.empty:
                self.logger.warning("No training data found. Please add music files to mood directories.")
                return False
            
            # Prepare features and labels
            X = df[self.feature_names].values
            y = df['mood'].values
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train classifier
            self.logger.info("Training mood classifier...")
            self.classifier.fit(X_scaled, y)
            self.is_trained = True
            
            # Save model if requested
            if save_model:
                self.save_model()
            
            # Print training stats
            unique, counts = np.unique(y, return_counts=True)
            self.logger.info("Training completed!")
            self.logger.info("Training data distribution:")
            for mood_id, count in zip(unique, counts):
                mood_name = self.mood_labels[mood_id]
                self.logger.info(f"  {mood_name}: {count} songs")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error training classifier: {e}")
            return False
    
    def predict_mood(self, audio_path):
        """Predict the mood of a music file"""
        if not self.is_trained:
            self.logger.warning("Classifier not trained. Loading pre-trained model...")
            if not self.load_model():
                return 'neutral'
        
        try:
            features = self.extract_features(audio_path)
            if not features:
                return 'neutral'
            
            # Prepare feature vector
            feature_vector = np.array([features[name] for name in self.feature_names]).reshape(1, -1)
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Predict mood
            prediction = self.classifier.predict(feature_vector_scaled)[0]
            mood = self.mood_labels[prediction]
            
            # Get prediction confidence
            probabilities = self.classifier.predict_proba(feature_vector_scaled)[0]
            confidence = np.max(probabilities)
            
            self.logger.info(f"Predicted mood for {Path(audio_path).name}: {mood} (confidence: {confidence:.2f})")
            
            return mood
            
        except Exception as e:
            self.logger.error(f"Error predicting mood for {audio_path}: {e}")
            return 'neutral'
    
    def save_model(self, model_path="music_mood_model.pkl"):
        """Save the trained model and scaler"""
        try:
            model_data = {
                'classifier': self.classifier,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'mood_labels': self.mood_labels,
                'is_trained': self.is_trained
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            self.logger.info(f"Model saved to {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, model_path="music_mood_model.pkl"):
        """Load a pre-trained model"""
        try:
            if not os.path.exists(model_path):
                self.logger.warning(f"Model file {model_path} not found")
                return False
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.classifier = model_data['classifier']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.mood_labels = model_data['mood_labels']
            self.is_trained = model_data['is_trained']
            
            self.logger.info(f"Model loaded from {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False
    
    def batch_classify_music(self, music_directory, output_csv="music_classifications.csv"):
        """Classify all music files in a directory and save results"""
        music_path = Path(music_directory)
        results = []
        
        for audio_file in music_path.rglob('*'):
            if audio_file.suffix.lower() in ['.mp3', '.wav', '.ogg', '.m4a']:
                predicted_mood = self.predict_mood(str(audio_file))
                
                results.append({
                    'file_path': str(audio_file),
                    'filename': audio_file.name,
                    'predicted_mood': predicted_mood
                })
        
        # Save results to CSV
        df = pd.DataFrame(results)
        df.to_csv(output_csv, index=False)
        
        self.logger.info(f"Classification results saved to {output_csv}")
        return df
    
    def get_mood_distribution(self, music_directory):
        """Get the distribution of predicted moods in a music directory"""
        df = self.batch_classify_music(music_directory)
        
        mood_counts = df['predicted_mood'].value_counts()
        mood_percentages = (mood_counts / len(df) * 100).round(2)
        
        distribution = {}
        for mood, count in mood_counts.items():
            distribution[mood] = {
                'count': count,
                'percentage': mood_percentages[mood]
            }
        
        return distribution
