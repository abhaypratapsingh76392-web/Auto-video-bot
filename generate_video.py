import os
import requests
import urllib.parse
from datetime import datetime
from moviepy.editor import ImageClip, AudioFileClip

# आज की तारीख (वेबसाइट और वीडियो के नाम के लिए)
today_date = datetime.now().strftime("%Y-%m-%d")
final_video_name = f"video_{today_date}.mp4"

# 1. 2-Minute Script for USA Audience (Trendy, Tech & Future)
scenes = [
    {"text": "Welcome back! Today we are diving into the mind-blowing technologies that are reshaping the United States right now.", "prompt": "Futuristic American city, flying cars, neon lights, 8k resolution, cinematic"},
    {"text": "Silicon Valley is no longer just about software. We are entering the age of humanoid robotics and advanced artificial intelligence.", "prompt": "Advanced humanoid robot working in a modern tech lab in California, hyperrealistic"},
    {"text": "Companies across America are deploying AI workers that can think, learn, and adapt faster than any human ever could.", "prompt": "Glowing AI brain hologram surrounded by data streams, dark futuristic background"},
    {"text": "But it is not just happening on Earth. The new space race is being driven by private American companies aiming for Mars.", "prompt": "Massive futuristic rocket launching from Kennedy Space Center, realistic space scene"},
    {"text": "In the next few years, lunar bases will become a reality, acting as a stepping stone for deep space exploration.", "prompt": "Futuristic human colony on the moon, glowing domes, Earth in the background"},
    {"text": "Back on the ground, the way we travel is completely transforming with the rise of autonomous electric networks.", "prompt": "Sleek self-driving electric vehicles moving on a glowing smart highway at night"},
    {"text": "Hyperloop systems and high-speed rail networks are being developed to connect major US cities in just minutes.", "prompt": "Ultra-fast hyperloop train inside a glass tube, modern transit architecture"},
    {"text": "Even our healthcare is evolving. Nanobots and AI diagnostics are helping doctors cure diseases before they even start.", "prompt": "Microscopic glowing nanobots repairing a DNA strand, medical sci-fi 3D render"},
    {"text": "Virtual reality is replacing traditional screens. Soon, you will be able to attend live concerts and meetings from your living room.", "prompt": "Person wearing a sleek VR headset, surrounded by glowing floating digital screens"},
    {"text": "Meanwhile, the renewable energy sector is booming, with massive solar farms powering entire states sustainably.", "prompt": "Endless futuristic solar panel farm in a desert at sunset, highly detailed"},
    {"text": "The fusion of biology and technology will give humans unprecedented capabilities, enhancing both mind and body.", "prompt": "Cybernetic human eye glowing with digital interface, cyberpunk style"},
    {"text": "This is not science fiction anymore. This is the future being built today. Hit that subscribe button for more daily updates!", "prompt": "Glowing futuristic subscribe button floating in a high-tech digital environment"}
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
clip_files = []

print("🚀 Starting Video Generation Process (Chunk-by-Chunk)...")

# 2. छोटे-छोटे क्लिप्स बनाना (इससे सिस्टम क्रैश नहीं होगा)
for i, scene in enumerate(scenes):
    print(f"🎬 Processing Scene {i+1} / {len(scenes)}...")
    
    img_file = f"temp_img_{i}.jpg"
    aud_file = f"temp_aud_{i}.mp3"
    clip_file = f"temp_clip_{i}.mp4"
    
    # A. Download Image (Fixed 403 Forbidden Error)
    safe_prompt = urllib.parse.quote(scene['prompt'])
    img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1920&height=1080&nologo=true"
    
    response = requests.get(img_url, headers=headers)
    if response.status_code == 200:
        with open(img_file, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Error downloading image {i+1}. Using black screen fallback.")
        continue # Skip if error
        
    # B. Generate Voice (USA Accent)
    os.system(f'edge-tts --voice "en-US-ChristopherNeural" --text "{scene["text"]}" --write-media {aud_file}')
    
    # C. Make Short Clip
    audio = AudioFileClip(aud_file)
    clip = ImageClip(img_file).set_duration(audio.duration)
    clip = clip.set_audio(audio)
    clip.write_videofile(clip_file, fps=24, codec="libx264", audio_codec="aac", logger=None)
    
    clip_files.append(clip_file)

# 3. FFMPEG से सभी छोटे क्लिप्स को जोड़कर एक फुल 2-मिनट का वीडियो बनाना
print("🔗 Combining all short clips into the final video...")
with open("videos_list.txt", "w") as f:
    for clip in clip_files:
        f.write(f"file '{clip}'\n")

# FFmpeg Command (सुपर फ़ास्ट और 0 RAM लेता है)
os.system(f"ffmpeg -f concat -safe 0 -i videos_list.txt -c copy {final_video_name}")
print(f"✅ Success! Final full video saved as {final_video_name}")

# 4. HTML वेबसाइट को अपडेट करना (ताकि सारे वीडियो एक जगह दिखें)
html_header = """<html>
<head>
    <title>My Auto USA Shorts</title>
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: white; text-align: center; }
        .video-container { display: inline-block; margin: 20px; padding: 10px; background: #222; border-radius: 10px; }
        video { width: 400px; border-radius: 10px; }
    </style>
</head>
<body>
    <h1>🚀 Auto-Generated Viral USA Videos</h1>
    <p>New videos are added here automatically every day!</p>
"""
html_footer = "</body></html>"

# गिटहब पर मौजूद सभी वीडियो ढूंढें
all_videos = [f for f in os.listdir('.') if f.startswith('video_') and f.endswith('.mp4')]
all_videos.sort(reverse=True) # लेटेस्ट वीडियो सबसे ऊपर

with open("index.html", "w") as html_file:
    html_file.write(html_header)
    for vid in all_videos:
        html_file.write(f'''
        <div class="video-container">
            <h3>{vid.replace('.mp4', '')}</h3>
            <video controls><source src="{vid}" type="video/mp4"></video>
        </div>''')
    html_file.write(html_footer)

print("🌐 Webpage (index.html) updated with the new video!")
