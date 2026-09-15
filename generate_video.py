import os
import json
import requests
import urllib.parse
from datetime import datetime
from moviepy.editor import ImageClip, AudioFileClip

# आज की तारीख
today_date = datetime.now().strftime("%Y-%m-%d")
final_video_name = f"video_{today_date}.mp4"

# 1. Gemini Direct REST API Call (No SDK required - 100% Error Free)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in GitHub Secrets.")
    exit(1)

prompt = """
You are an expert YouTube Shorts scriptwriter for a USA audience. 
Find a highly trending, fascinating, or mysterious topic in the USA right now.
Write an engaging script for a 1.5 to 2-minute video.

IMPORTANT: Output the response STRICTLY as a JSON array of objects. Do NOT wrap it in markdown block.
Each object must have exactly two keys:
1. "text": The narration for the scene.
2. "prompt": A highly detailed, realistic image generation prompt for that scene.

Example format:
[
  {"text": "Did you know the US is secretly building...", "prompt": "Cinematic shot of a secret base, 8k"},
  {"text": "This technology will change everything.", "prompt": "Glowing AI microchip, neon lights, 4k"}
]
Generate around 10 to 12 scenes.
"""

print("🧠 Asking Gemini AI via Direct API (Like your HTML code)...")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
payload = {
    "contents": [{"parts": [{"text": prompt}]}]
}

try:
    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
    data = response.json()
    
    # Extracting text from API response
    json_text = data['candidates'][0]['content']['parts'][0]['text'].strip()
    
    if json_text.startswith("```json"):
        json_text = json_text[7:-3].strip()
    elif json_text.startswith("```"):
        json_text = json_text[3:-3].strip()
        
    scenes = json.loads(json_text)
    print(f"✅ Gemini successfully generated script with {len(scenes)} scenes!")
except Exception as e:
    print("❌ API Error or Parsing Failed.")
    print("Response Data:", response.text if 'response' in locals() else e)
    exit(1)

headers = {'User-Agent': 'Mozilla/5.0'}
clip_files = []

print("🚀 Starting Video Generation Process (Chunk-by-Chunk)...")

# 2. छोटे-छोटे क्लिप्स बनाना
for i, scene in enumerate(scenes):
    print(f"🎬 Processing Scene {i+1} / {len(scenes)}...")
    
    img_file = f"temp_img_{i}.jpg"
    aud_file = f"temp_aud_{i}.mp3"
    clip_file = f"temp_clip_{i}.mp4"
    
    # A. Download Image
    safe_prompt = urllib.parse.quote(scene['prompt'])
    img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1920&height=1080&nologo=true"
    
    img_response = requests.get(img_url, headers=headers)
    if img_response.status_code == 200:
        with open(img_file, 'wb') as f:
            f.write(img_response.content)
    else:
        print(f"⚠️ Error downloading image {i+1}. Skipping scene.")
        continue 
        
    # B. Generate Voice (USA Accent)
    os.system(f'edge-tts --voice "en-US-ChristopherNeural" --text "{scene["text"]}" --write-media {aud_file}')
    
    # C. Make Short Clip
    try:
        audio = AudioFileClip(aud_file)
        clip = ImageClip(img_file).set_duration(audio.duration)
        clip = clip.set_audio(audio)
        clip.write_videofile(clip_file, fps=24, codec="libx264", audio_codec="aac", logger=None)
        clip_files.append(clip_file)
    except Exception as e:
        print(f"⚠️ Error creating clip {i+1}: {e}")

# 3. FFMPEG से सभी क्लिप्स जोड़ना
print("🔗 Combining all short clips into the final video...")
with open("videos_list.txt", "w") as f:
    for clip in clip_files:
        f.write(f"file '{clip}'\n")

os.system(f"ffmpeg -f concat -safe 0 -i videos_list.txt -c copy {final_video_name}")
print(f"✅ Success! Final video saved as {final_video_name}")

# 4. HTML वेबसाइट को अपडेट करना (WITH DOWNLOAD BUTTON)
html_header = """<html>
<head>
    <title>Auto Viral USA Videos</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; background: #0f0f0f; color: white; text-align: center; margin: 0; padding: 20px; }
        h1 { color: #ff0000; }
        .video-container { display: inline-block; margin: 15px; padding: 20px; background: #222; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }
        video { width: 100%; max-width: 500px; border-radius: 10px; margin-bottom: 15px; }
        
        /* Download Button CSS */
        .download-btn {
            display: inline-block;
            background: #4285f4;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            transition: background 0.3s;
        }
        .download-btn:hover { background: #3367d6; }
    </style>
</head>
<body>
    <h1>🔥 Auto-Generated Viral USA Updates</h1>
    <p>100% AI Generated Content - New video drops every day!</p>
"""
html_footer = "</body></html>"

all_videos = [f for f in os.listdir('.') if f.startswith('video_') and f.endswith('.mp4')]
all_videos.sort(reverse=True) # लेटेस्ट वीडियो ऊपर दिखेगा

with open("index.html", "w") as html_file:
    html_file.write(html_header)
    for vid in all_videos:
        # यहाँ पर डाउनलोड बटन (download attribute के साथ) जोड़ा गया है
        html_file.write(f'''
        <div class="video-container">
            <h3>Date: {vid.replace('video_', '').replace('.mp4', '')}</h3>
            <video controls preload="metadata"><source src="{vid}" type="video/mp4"></video>
            <br>
            <a href="{vid}" download="{vid}" class="download-btn">⬇️ Download Video</a>
        </div>''')
    html_file.write(html_footer)

print("🌐 Webpage (index.html) successfully updated with Download buttons!")
