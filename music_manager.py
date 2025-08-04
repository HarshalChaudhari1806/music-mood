import os
import random
import pygame
import time
import threading
from pathlib import Path
import logging
from mutagen import File
import json

class MusicManager:
    def __init__(self, music_directory="music"):
        """Initialize the music manager"""
        self.music_directory = Path(music_directory)
        self.current_song = None
        self.current_mood = "neutral"
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        self.playlist = []
        self.current_index = 0
        self.repeat_mode = False
        self.shuffle_mode = False
        
        # Initialize pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Supported audio formats
        self.supported_formats = {'.mp3', '.wav', '.ogg', '.m4a'}
        
        # Mood directories
        self.mood_directories = {
            'happy': self.music_directory / 'happy',
            'sad': self.music_directory / 'sad',
            'angry': self.music_directory / 'angry',
            'neutral': self.music_directory / 'neutral',
            'fear': self.music_directory / 'fear',
            'surprise': self.music_directory / 'surprise',
            'disgust': self.music_directory / 'disgust'
        }
        
        # Initialize logging first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Create mood directories if they don't exist
        self._create_mood_directories()
        
        # Load music library
        self.music_library = self._scan_music_library()
    
    def _create_mood_directories(self):
        """Create mood directories if they don't exist"""
        self.music_directory.mkdir(exist_ok=True)
        for mood_dir in self.mood_directories.values():
            mood_dir.mkdir(exist_ok=True)
    
    def _scan_music_library(self):
        """Scan and categorize music files by mood"""
        music_library = {}
        
        for mood, directory in self.mood_directories.items():
            music_library[mood] = []
            
            if directory.exists():
                for file_path in directory.rglob('*'):
                    if file_path.suffix.lower() in self.supported_formats:
                        song_info = self._get_song_info(file_path)
                        music_library[mood].append(song_info)
        
        self.logger.info(f"Music library loaded: {sum(len(songs) for songs in music_library.values())} songs")
        return music_library
    
    def _get_song_info(self, file_path):
        """Extract song information from file"""
        try:
            audio_file = File(file_path)
            title = "Unknown Title"
            artist = "Unknown Artist"
            duration = 0
            
            if audio_file:
                title = audio_file.get('TIT2', [file_path.stem])[0] if audio_file.get('TIT2') else file_path.stem
                artist = audio_file.get('TPE1', ["Unknown Artist"])[0] if audio_file.get('TPE1') else "Unknown Artist"
                duration = audio_file.info.length if hasattr(audio_file.info, 'length') else 0
            
            return {
                'path': str(file_path),
                'title': str(title),
                'artist': str(artist),
                'duration': duration,
                'filename': file_path.name
            }
        
        except Exception as e:
            self.logger.error(f"Error reading song info for {file_path}: {e}")
            return {
                'path': str(file_path),
                'title': file_path.stem,
                'artist': "Unknown Artist",
                'duration': 0,
                'filename': file_path.name
            }
    
    def get_songs_by_mood(self, mood):
        """Get all songs for a specific mood"""
        return self.music_library.get(mood, [])
    
    def play_mood_music(self, mood):
        """Play music based on detected mood"""
        if mood != self.current_mood:
            self.current_mood = mood
            songs = self.get_songs_by_mood(mood)
            
            if songs:
                if self.shuffle_mode:
                    random.shuffle(songs)
                
                self.playlist = songs
                self.current_index = 0
                self.play_current_song()
                self.logger.info(f"Started playing {mood} music")
            else:
                self.logger.warning(f"No songs found for mood: {mood}")
                # Fallback to neutral mood
                if mood != 'neutral':
                    self.play_mood_music('neutral')
    
    def play_current_song(self):
        """Play the current song in playlist"""
        if not self.playlist:
            return False
        
        try:
            current_song = self.playlist[self.current_index]
            self.current_song = current_song
            
            pygame.mixer.music.load(current_song['path'])
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            
            self.is_playing = True
            self.is_paused = False
            
            self.logger.info(f"Playing: {current_song['title']} by {current_song['artist']}")
            
            # Start monitoring thread to handle song end
            monitor_thread = threading.Thread(target=self._monitor_playback, daemon=True)
            monitor_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error playing song: {e}")
            return False
    
    def _monitor_playback(self):
        """Monitor playback and handle song transitions"""
        while self.is_playing:
            if not pygame.mixer.music.get_busy() and not self.is_paused:
                # Song ended, play next
                self.next_song()
                break
            time.sleep(1)
    
    def pause(self):
        """Pause music playback"""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.logger.info("Music paused")
    
    def resume(self):
        """Resume music playback"""
        if self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.logger.info("Music resumed")
    
    def stop(self):
        """Stop music playback"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_song = None
        self.logger.info("Music stopped")
    
    def next_song(self):
        """Play next song in playlist"""
        if not self.playlist:
            return
        
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
        elif self.repeat_mode:
            self.current_index = 0
        else:
            self.stop()
            return
        
        self.play_current_song()
    
    def previous_song(self):
        """Play previous song in playlist"""
        if not self.playlist:
            return
        
        if self.current_index > 0:
            self.current_index -= 1
        elif self.repeat_mode:
            self.current_index = len(self.playlist) - 1
        else:
            self.current_index = 0
        
        self.play_current_song()
    
    def set_volume(self, volume):
        """Set playback volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
    
    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        self.shuffle_mode = not self.shuffle_mode
        if self.shuffle_mode and self.playlist:
            # Reshuffle current playlist
            current_song = self.playlist[self.current_index] if self.playlist else None
            random.shuffle(self.playlist)
            if current_song:
                # Find new index of current song
                for i, song in enumerate(self.playlist):
                    if song['path'] == current_song['path']:
                        self.current_index = i
                        break
        
        self.logger.info(f"Shuffle mode: {'ON' if self.shuffle_mode else 'OFF'}")
    
    def toggle_repeat(self):
        """Toggle repeat mode"""
        self.repeat_mode = not self.repeat_mode
        self.logger.info(f"Repeat mode: {'ON' if self.repeat_mode else 'OFF'}")
    
    def get_current_song_info(self):
        """Get information about currently playing song"""
        return self.current_song
    
    def get_playback_status(self):
        """Get current playback status"""
        return {
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'current_song': self.current_song,
            'current_mood': self.current_mood,
            'volume': self.volume,
            'shuffle': self.shuffle_mode,
            'repeat': self.repeat_mode,
            'playlist_length': len(self.playlist),
            'current_index': self.current_index
        }
    
    def get_library_stats(self):
        """Get statistics about music library"""
        stats = {}
        total_songs = 0
        
        for mood, songs in self.music_library.items():
            stats[mood] = len(songs)
            total_songs += len(songs)
        
        stats['total'] = total_songs
        return stats
    
    def add_song_to_mood(self, file_path, mood):
        """Add a song to a specific mood category"""
        try:
            file_path = Path(file_path)
            mood_dir = self.mood_directories.get(mood)
            
            if not mood_dir:
                raise ValueError(f"Invalid mood: {mood}")
            
            # Copy file to mood directory
            destination = mood_dir / file_path.name
            destination.write_bytes(file_path.read_bytes())
            
            # Update music library
            song_info = self._get_song_info(destination)
            self.music_library[mood].append(song_info)
            
            self.logger.info(f"Added song {file_path.name} to {mood} category")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding song to mood: {e}")
            return False
    
    def refresh_library(self):
        """Refresh the music library"""
        self.music_library = self._scan_music_library()
        self.logger.info("Music library refreshed")
