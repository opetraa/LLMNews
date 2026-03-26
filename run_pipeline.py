import asyncio
import sys
from datetime import datetime

from src.script_writer import ScriptWriter
from src.audio_engine import generate_audio_from_text

# If rss_builder exists, import it 
try:
    from src.rss_builder import update_feed
except ImportError:
    update_feed = None

async def main():
    print("=== Starting Weekly Tech Podcast Pipeline ===")
    
    # 1. Generate full 60-min script in 5 chunks
    writer = ScriptWriter()
    print("[1/3] Generating script...")
    full_script = await writer.generate_full_episode_script()
    
    # 2. Synthesize audio
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = "public"
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_filename = os.path.join(output_dir, f"episode_{date_str}.mp3")
    print(f"[2/3] Synthesizing audio to {output_filename}...")
    success = await generate_audio_from_text(full_script, output_filename)
    
    if not success:
        print("Audio synthesis failed.")
        sys.exit(1)
        
    # 3. Update RSS Feed
    print("[3/3] Updating RSS Feed...")
    if update_feed:
        base_url = os.environ.get("GITHUB_PAGES_URL", "https://kizarik.github.io/weekly-tech-podcast")
        update_feed(output_dir, base_url)
    else:
        print("RSS Builder not implemented yet, skipping feed update.")
        
    print("=== Pipeline Complete! ===")

if __name__ == "__main__":
    asyncio.run(main())
