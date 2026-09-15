import os
import urllib.request
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# 1. आपकी कहानी और इमेज के Prompts (आप इसे और बड़ा कर सकते हैं)
scenes = [
    {
        "text": "Hello friends! Today we are talking about the mysteries of the universe.", 
        "prompt": "Beautiful glowing galaxy in deep space, cinematic lighting, 8k resolution"
    },
    {
        "text": "Did you know that there are more stars in the universe than grains of sand on Earth?", 
        "prompt": "Millions of stars in the night sky above a desert, highly detailed"
    },
    {
        "text": "The universe is constantly expanding, creating new galaxies every second.", 
        "prompt": "A colorful nebula expanding in space, sci-fi digital art"
    }
]

video_clips = []

print("Starting video generation process...")

for i, scene in enumerate(scenes):
    print(f"Processing Scene {i+1} / {len(scenes)}...")
    
    image_file = f"image_{i}.jpg"
    audio_file = f"audio_{i}.mp3"
    
    # A. Generate & Download Image (Using Pollinations AI - 100% Free)
    safe_prompt = scene['prompt'].replace(' ', '%20')
    # 1920x1080 resolution for YouTube/Desktop format
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1920&height=1080&nologo=true"
    urllib.request.urlretrieve(image_url, image_file)
    print(f"Downloaded Image {i+1}")
    
    # B. Generate Voice (Using Edge-TTS - Free Microsoft Neural Voice)
    # Voice options: en-US-ChristopherNeural (Male), en-US-JennyNeural (Female)
    os.system(f'edge-tts --voice "en-US-ChristopherNeural" --text "{scene["text"]}" --write-media {audio_file}')
    print(f"Generated Audio {i+1}")
    
    # C. Merge Image and Audio into a Clip
    audio = AudioFileClip(audio_file)
    # Set image duration exactly equal to audio duration
    clip = ImageClip(image_file).set_duration(audio.duration)
    clip = clip.set_audio(audio)
    
    video_clips.append(clip)

# 2. Combine all scenes into one final video
print("Combining all scenes into final video...")
final_video = concatenate_videoclips(video_clips, method="compose")

# 3. Export as MP4
output_filename = "final_video.mp4"
final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")

print(f"Success! Video saved as {output_filename}")
