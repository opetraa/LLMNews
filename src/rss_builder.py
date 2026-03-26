import os
import glob
from datetime import datetime
import pytz
from feedgen.feed import FeedGenerator

def update_feed(public_dir: str, base_url: str):
    if not os.path.exists(public_dir):
        os.makedirs(public_dir)

    # 1. Enforce Rolling Retention (Keep latest 4 MP3s)
    search_pattern = os.path.join(public_dir, "episode_*.mp3")
    mp3_files = glob.glob(search_pattern)
    
    # Sort files by modification time (oldest first)
    mp3_files.sort(key=os.path.getmtime)
    
    # If more than 4, delete oldest
    while len(mp3_files) > 4:
        oldest_file = mp3_files.pop(0)
        try:
            os.remove(oldest_file)
            print(f"Rolling Retention: Deleted old episode -> {oldest_file}")
        except Exception as e:
            print(f"Failed to delete {oldest_file}: {e}")

    # Reload list and sort newest first for RSS
    final_mp3s = glob.glob(search_pattern)
    final_mp3s.sort(key=os.path.getmtime, reverse=True)
    
    if not final_mp3s:
        print("No episodes found to build RSS.")
        return

    # 2. Build RSS Feed
    fg = FeedGenerator()
    fg.load_extension('podcast')
    
    fg.title('Weekly Tech Podcast')
    fg.description('Zero-Cost AI generated weekly tech catch-up radio.')
    fg.link(href=base_url, rel='alternate')
    fg.language('ko')
    
    tz = pytz.UTC
    
    for mp3_path in final_mp3s:
        filename = os.path.basename(mp3_path)
        file_url = f"{base_url.rstrip('/')}/{filename}"
        file_size = os.path.getsize(mp3_path)
        
        date_str = filename.replace("episode_", "").replace(".mp3", "")
        try:
            pub_date = datetime.strptime(date_str, "%Y-%m-%d")
            pub_date = tz.localize(pub_date)
        except ValueError:
            pub_date = datetime.now(tz)
        
        fe = fg.add_entry()
        fe.id(file_url)
        fe.title(f"Tech Briefing: {date_str}")
        fe.published(pub_date)
        fe.description(f"Weekly tech podcast episode generated on {date_str}.")
        fe.enclosure(file_url, str(file_size), 'audio/mpeg')
        
    xml_output = os.path.join(public_dir, "feed.xml")
    fg.rss_file(xml_output)
    print(f"Successfully generated podcast RSS feed at {xml_output} with {len(final_mp3s)} episodes.")
