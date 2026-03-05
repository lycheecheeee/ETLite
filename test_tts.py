import requests
import json

url = "https://cantonese.ai/api/tts"

payload = json.dumps({
    "api_key": "sk-o0sqn7wHhgsSqHoNW0j58q0f0vwcms9",
    "text": "你今日食咗飯未？",
    "frame_rate": "24000",
    "language": "cantonese",
    "output_extension": "wav",
    "voice_id": "2725cf0f-efe2-4132-9e06-62ad84b2973d"
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

with open('output.wav', 'wb') as f:
    f.write(response.content)
