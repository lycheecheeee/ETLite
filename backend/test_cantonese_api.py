"""
Test Cantonese AI TTS API
測試粵語 AI TTS API
"""
import requests
import json
import sys

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "sk-o0sqn7wHhgsSqHoNW0j58q0f0vwcms9"
API_URL = "https://cantonese.ai/api/tts"

def test_tts():
    """Test TTS generation"""
    payload = {
        "api_key": API_KEY,
        "text": "早晨！我係子程，歡迎收聽 Net 仔財經早新聞",
        "frame_rate": "24000",
        "speed": 1,
        "pitch": 0,
        "language": "cantonese",
        "output_extension": "wav",
        "voice_id": "2725cf0f-efe2-4132-9e06-62ad84b2973d",
        "should_return_timestamp": False
    }
    
    print("Testing Cantonese AI TTS API...")
    print(f"Text: {payload['text']}")
    print(f"Voice ID: {payload['voice_id']}")
    
    try:
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            # Save audio file
            with open("test_cantonese_output.wav", "wb") as f:
                f.write(response.content)
            
            print(f"Success! Audio saved to test_cantonese_output.wav")
            print(f"   File size: {len(response.content)} bytes")
            return True
        else:
            print(f"API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    test_tts()
