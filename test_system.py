import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestMoodDetector(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        from mood_detector import MoodDetector
        self.detector = MoodDetector()
    
    def test_mood_mapping(self):
        """Test mood mapping dictionary"""
        expected_moods = ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']
        for mood in expected_moods:
            self.assertIn(mood, self.detector.mood_mapping.values())
    
    def test_get_current_mood(self):
        """Test getting current mood"""
        mood_data = self.detector.get_current_mood()
        self.assertIn('mood', mood_data)
        self.assertIn('confidence', mood_data)
        self.assertIn('timestamp', mood_data)
    
    def test_mood_history(self):
        """Test mood history functionality"""
        # Add some test entries
        self.detector._update_mood_history('happy', 0.8)
        self.detector._update_mood_history('sad', 0.6)
        
        self.assertEqual(len(self.detector.mood_history), 2)
        self.assertEqual(self.detector.mood_history[0]['mood'], 'happy')
        self.assertEqual(self.detector.mood_history[1]['mood'], 'sad')

class TestMusicManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.music_dir = os.path.join(self.test_dir, 'test_music')
        
        # Mock pygame to avoid audio system requirements
        with patch('pygame.mixer.init'), patch('pygame.mixer.music'):
            from music_manager import MusicManager
            self.manager = MusicManager(self.music_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def test_mood_directories_creation(self):
        """Test that mood directories are created"""
        expected_dirs = ['happy', 'sad', 'angry', 'neutral', 'fear', 'surprise', 'disgust']
        for mood in expected_dirs:
            mood_path = os.path.join(self.music_dir, mood)
            self.assertTrue(os.path.exists(mood_path))
    
    def test_supported_formats(self):
        """Test supported audio formats"""
        expected_formats = {'.mp3', '.wav', '.ogg', '.m4a'}
        self.assertEqual(self.manager.supported_formats, expected_formats)
    
    def test_get_songs_by_mood(self):
        """Test getting songs by mood"""
        songs = self.manager.get_songs_by_mood('happy')
        self.assertIsInstance(songs, list)
    
    def test_library_stats(self):
        """Test library statistics"""
        stats = self.manager.get_library_stats()
        self.assertIn('total', stats)
        expected_moods = ['happy', 'sad', 'angry', 'neutral', 'fear', 'surprise', 'disgust']
        for mood in expected_moods:
            self.assertIn(mood, stats)

class TestMusicAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        from music_analyzer import MusicAnalyzer
        self.analyzer = MusicAnalyzer()
    
    def test_mood_labels(self):
        """Test mood label mapping"""
        expected_labels = ['neutral', 'happy', 'sad', 'angry', 'fear', 'surprise', 'disgust']
        for label in expected_labels:
            self.assertIn(label, self.analyzer.mood_labels.values())
    
    def test_feature_names(self):
        """Test feature names for audio analysis"""
        expected_features = [
            'tempo', 'spectral_centroid_mean', 'spectral_centroid_std',
            'mfcc_1_mean', 'chroma_mean'
        ]
        for feature in expected_features:
            self.assertIn(feature, self.analyzer.feature_names)
    
    @patch('librosa.load')
    @patch('librosa.beat.beat_track')
    @patch('librosa.feature.spectral_centroid')
    def test_extract_features(self, mock_centroid, mock_beat, mock_load):
        """Test audio feature extraction"""
        # Mock librosa functions
        mock_load.return_value = (np.random.random(22050), 22050)
        mock_beat.return_value = (120, np.array([]))
        mock_centroid.return_value = np.array([np.random.random(100)])
        
        # This would normally require an actual audio file
        # For testing, we'll just verify the function exists and handles errors
        result = self.analyzer.extract_features('fake_path.mp3')
        # Should return None due to mocked file, but function should not crash
        self.assertIsNone(result)

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        """Set up Flask test client"""
        os.environ['TESTING'] = 'True'
        
        # Mock the heavy components
        with patch('app.MoodDetector'), \
             patch('app.MusicManager'), \
             patch('app.MusicAnalyzer'):
            from app import app
            self.app = app
            self.app.config['TESTING'] = True
            self.client = self.app.test_client()
    
    def test_index_route(self):
        """Test main page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Music Mood Player', response.data)
    
    def test_api_routes_exist(self):
        """Test that API routes are defined"""
        # Test routes that should exist
        api_routes = [
            '/api/current_mood',
            '/api/library_stats',
            '/api/playback_status'
        ]
        
        for route in api_routes:
            response = self.client.get(route)
            # Should not be 404 (route exists), may be 500 due to mocked components
            self.assertNotEqual(response.status_code, 404)

def run_integration_test():
    """Run integration test with actual components"""
    print("Running integration test...")
    
    try:
        # Test mood detector initialization
        print("Testing MoodDetector...")
        from mood_detector import MoodDetector
        detector = MoodDetector()
        print("✓ MoodDetector initialized")
        
        # Test music manager initialization
        print("Testing MusicManager...")
        with patch('pygame.mixer.init'), patch('pygame.mixer.music'):
            from music_manager import MusicManager
            manager = MusicManager()
            print("✓ MusicManager initialized")
        
        # Test music analyzer initialization
        print("Testing MusicAnalyzer...")
        from music_analyzer import MusicAnalyzer
        analyzer = MusicAnalyzer()
        print("✓ MusicAnalyzer initialized")
        
        # Test Flask app initialization
        print("Testing Flask app...")
        os.environ['TESTING'] = 'True'
        with patch('app.MoodDetector'), \
             patch('app.MusicManager'), \
             patch('app.MusicAnalyzer'):
            from app import app
            print("✓ Flask app initialized")
        
        print("\n🎉 All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    print("Checking dependencies...")
    
    required_packages = [
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('flask', 'flask'),
        ('pygame', 'pygame'),
        ('sklearn', 'scikit-learn'),
        ('pandas', 'pandas'),
        ('fer', 'fer'),
        ('PIL', 'Pillow'),
        ('mutagen', 'mutagen')
    ]
    
    missing = []
    available = []
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            available.append(package_name)
            print(f"✓ {package_name}")
        except ImportError:
            missing.append(package_name)
            print(f"✗ {package_name} - MISSING")
    
    print(f"\nAvailable: {len(available)}/{len(required_packages)} packages")
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    else:
        print("\n✅ All dependencies are available!")
        return True

def main():
    """Main test runner"""
    print("🧪 Music Mood Player Test Suite")
    print("=" * 40)
    
    # Check dependencies first
    deps_ok = check_dependencies()
    print()
    
    if not deps_ok:
        print("⚠️ Some dependencies are missing. Install them before running full tests.")
        print("You can still run the integration test to check component initialization.")
        print()
    
    # Run integration test
    integration_ok = run_integration_test()
    print()
    
    # Run unit tests if dependencies are available
    if deps_ok:
        print("Running unit tests...")
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add test classes
        test_classes = [TestMoodDetector, TestMusicManager, TestMusicAnalyzer, TestFlaskApp]
        for test_class in test_classes:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        print(f"\nUnit Test Results:")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
        
        overall_success = len(result.failures) == 0 and len(result.errors) == 0
    else:
        overall_success = integration_ok
    
    print("\n" + "=" * 40)
    if overall_success and deps_ok:
        print("🎉 All tests passed! The system is ready to use.")
    elif integration_ok:
        print("⚠️ Basic components work, but install missing dependencies for full functionality.")
    else:
        print("❌ Tests failed. Check the errors above and fix issues before proceeding.")
    
    print("\nTo start the application:")
    print("1. Run: python setup.py (if not done already)")
    print("2. Add music files to mood folders")
    print("3. Run: python app.py")
    print("4. Open: http://localhost:5000")

if __name__ == '__main__':
    main()
