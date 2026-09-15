import os
import sys
import json
import requests
import urllib.parse
from datetime import datetime

# 1. API Keys Setup (Only Gemini Needed!)
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in GitHub Secrets!")
    exit(1)

mode = "auto"
custom_prompt = ""
if len(sys.argv) > 2 and sys.argv[1] == "--custom":
    mode = "custom"
    custom_prompt = sys.argv[2]

today_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
final_video_name = f"video_{mode}_{today_date}.mp4"

# 2. Gemini AI: Script, Search Keywords & Auto-Language Voice
if mode == "custom":
    print(f"🛠️ Custom Video Mode! Prompt: {custom_prompt}")
    ai_prompt = f"""You are a video scriptwriter. The user wants a video about: "{custom_prompt}".
    Output STRICTLY as a JSON array. Each object must have:
    1. "text": The narration in the exact language the user used (Hindi or English).
    2. "keyword": 1-2 word simple English search term to find real stock video (e.g. "hacker", "forest", "city night").
    3. "voice": If the text is Hindi, use "hi-IN-MadhurNeural". If English, use "en-US-ChristopherNeural".
    Limit to 4-6 scenes. No markdown wrappers."""
else:
    print("🤖 Auto Daily Mode!")
    ai_prompt = """Write an engaging script for a YouTube Shorts video about a trending USA topic.
    Output STRICTLY as a JSON array. 
    1. "text": English narration.
    2. "keyword": 1-2 word simple English search term for real stock video (e.g. "robot", "space", "new york").
    3. "voice": "en-US-ChristopherNeural"
    Limit to 5-7 scenes. No markdown wrappers."""

url = "https://generativelanguage.googleapis.com/v1beta/interactions"
headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
payload = {"model": "gemini-3.6-flash", "input": [{"type": "user_input", "content": [{"type": "text", "text": ai_prompt}]}], "store": False}

try:
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    json_text = ""
    for step in data.get("steps", []):
        if step.get("type") == "model_output":
            for item in step.get("content", []):
                if item.get("type") == "text":
                    json_text += item.get("text", "")
    
    json_text = json_text.strip().replace("```json", "").replace("```", "").strip()
    scenes = json.loads(json_text)
except Exception as e:
    print(f"❌ API Error: {e}")
    exit(1)

clip_files = []

# 3. THE MAGIC: Download REAL Videos directly from Web & Generate Voice
for i, scene in enumerate(scenes):
    print(f"🎬 Scene {i+1} | Keyword: {scene['keyword']} | Voice: {scene['voice']}")
    vid_file = f"temp_raw_vid_{i}.mp4"
    aud_file = f"temp_aud_{i}.mp3"
    clip_file = f"temp_clip_{i}.mp4"
    
    # A. Magic Video Search (yt-dlp) - Finds No Copyright Stock footage
    search_query = f"{scene['keyword']} stock footage no copyright"
    print(f"🔍 Extracting Magic Video for: {search_query}")
    
    # yt-dlp command to download best short mp4 video silently
    yt_cmd = f'yt-dlp "ytsearch1:{search_query}" --match-filter "duration < 180" -f "best[ext=mp4]/bestvideo[ext=mp4]" -o "{vid_file}" --force-overwrites --quiet'
    os.system(yt_cmd)
    
    # Fallback if first search failed
    if not os.path.exists(vid_file):
        os.system(f'yt-dlp "ytsearch1:{scene["keyword"]}" --match-filter "duration < 120" -f "best[ext=mp4]" -o "{vid_file}" --force-overwrites --quiet')

    if os.path.exists(vid_file):
        # B. Generate Voice (Hindi or English automatically)
        os.system(f'edge-tts --voice "{scene["voice"]}" --text "{scene["text"]}" --write-media {aud_file}')
        
        # C. FFMPEG MAGIC: Crop horizontal video to Vertical Shorts (1080x1920) & Merge
        ffmpeg_cmd = (
            f'ffmpeg -y -stream_loop -1 -i "{vid_file}" -i "{aud_file}" '
            f'-map 0:v:0 -map 1:a:0 '
            f'-vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" '
            f'-c:v libx264 -preset fast -pix_fmt yuv420p -c:a aac -shortest "{clip_file}" -loglevel error'
        )
        os.system(ffmpeg_cmd)
        clip_files.append(clip_file)
    else:
        print(f"⚠️ Magic failed for {scene['keyword']}, skipping scene.")

# 4. Merge All Clips into Final Video
print("🔗 Combining clips into Full Video...")
with open("videos_list.txt", "w") as f:
    for clip in clip_files:
        f.write(f"file '{clip}'\n")

os.system(f"ffmpeg -f concat -safe 0 -i videos_list.txt -c copy {final_video_name} -loglevel error")
print(f"✅ Real Video Saved: {final_video_name}")

# 5. HTML GENERATION (Updates your Web Page)
all_videos = [f for f in os.listdir('.') if f.startswith('video_') and f.endswith('.mp4')]
auto_vids = sorted([v for v in all_videos if 'auto' in v], reverse=True)
custom_vids = sorted([v for v in all_videos if 'custom' in v], reverse=True)

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Video Studio</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ background: #0f0f0f; color: white; font-family: Arial; margin: 0; padding: 20px; text-align: center; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; background: #222; border-radius: 10px; margin-bottom: 20px; }}
        .btn {{ background: #4285f4; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 8px; cursor: pointer; font-weight: bold; text-decoration: none; }}
        .btn:hover {{ background: #3367d6; }}
        .grid {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }}
        .vid-card {{ background: #1a1a1a; padding: 15px; border-radius: 12px; width: 320px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
        video {{ width: 100%; border-radius: 8px; background: black; }}
        
        #modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 100; align-items: center; justify-content: center; }}
        .modal-box {{ background: linear-gradient(135deg, #1d0033, #001a33); width: 90%; max-width: 400px; padding: 30px; border-radius: 20px; text-align: center; }}
        input[type="text"], input[type="password"] {{ width: 90%; padding: 12px; margin-bottom: 15px; border-radius: 8px; border: none; font-size: 16px; }}
        #loading-screen {{ display: none; }}
        .spinner {{ width: 60px; height: 60px; border: 6px solid #444; border-top: 6px solid #4285f4; border-radius: 50%; animation: spin 1s linear infinite; margin: 20px auto; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🎬 AI Real Video Studio</h2>
        <button class="btn" onclick="document.getElementById('modal').style.display='flex'">+ Create Custom Video</button>
    </div>

    <h3 style="text-align:left; color:#4285f4;">🎯 My Custom Videos (Hindi/Eng)</h3>
    <div class="grid">
        {"".join([f'<div class="vid-card"><h4>{v.replace(".mp4", "")}</h4><video src="{v}" controls preload="metadata"></video><br><a href="{v}" download class="btn" style="display:block; margin-top:10px;">⬇️ Download</a></div>' for v in custom_vids]) or "<p style='color:#777;'>No custom videos. Create one!</p>"}
    </div>

    <h3 style="text-align:left; color:#00ffcc; margin-top:40px;">🌍 Daily Auto Videos</h3>
    <div class="grid">
        {"".join([f'<div class="vid-card"><h4>{v.replace(".mp4", "")}</h4><video src="{v}" controls preload="metadata"></video><br><a href="{v}" download class="btn" style="display:block; margin-top:10px;">⬇️ Download</a></div>' for v in auto_vids])}
    </div>

    <!-- CREATE CUSTOM VIDEO UI -->
    <div id="modal">
        <div class="modal-box" id="input-screen">
            <h3>Make Real Video</h3>
            <input type="text" id="repo_name" placeholder="Your GitHub (e.g. user/repo)">
            <input type="password" id="gh_token" placeholder="GitHub Personal Access Token">
            <input type="text" id="prompt" placeholder="Write topic (Hindi / English)">
            <button class="btn" onclick="startGeneration()" style="width: 100%;">Generate Magic Video</button>
            <button class="btn" onclick="document.getElementById('modal').style.display='none'" style="width: 100%; margin-top: 10px; background: #555;">Cancel</button>
        </div>
        
        <!-- LOADING SCREEN -->
        <div class="modal-box" id="loading-screen">
            <h3>Generating Real Video...</h3>
            <div class="spinner"></div>
            <h2 id="progress-text">0%</h2>
            <p style="color:#aaa;">Downloading real videos via Magic Search... Please wait 2-3 mins.</p>
        </div>
    </div>

    <script>
        function startGeneration() {{
            let repo = document.getElementById('repo_name').value;
            let token = document.getElementById('gh_token').value;
            let prompt = document.getElementById('prompt').value;
            
            if(!repo || !token || !prompt) {{ alert("Saari details bharna zaroori hai!"); return; }}
            
            document.getElementById('input-screen').style.display = 'none';
            document.getElementById('loading-screen').style.display = 'block';
            
            fetch(`https://api.github.com/repos/${{repo}}/actions/workflows/custom_video.yml/dispatches`, {{
                method: "POST",
                headers: {{ "Authorization": "token " + token, "Accept": "application/vnd.github.v3+json" }},
                body: JSON.stringify({{ ref: "main", inputs: {{ custom_prompt: prompt }} }})
            }}).then(res => {{
                if(res.ok) {{ simulateProgress(); }} 
                else {{ alert("Error! GitHub Token ya Repo name check karo."); location.reload(); }}
            }});
        }}

        function simulateProgress() {{
            let prog = 0;
            let interval = setInterval(() => {{
                prog += Math.floor(Math.random() * 5) + 1;
                if(prog > 96) prog = 96;
                document.getElementById('progress-text').innerText = prog + "%";
            }}, 4000);
            setTimeout(() => {{ clearInterval(interval); location.reload(); }}, 150000);
        }}
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("🌐 Webpage Updated!")
