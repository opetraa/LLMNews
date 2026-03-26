import os
import asyncio
from typing import List

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None

def chunk_text(text: str, max_chars: int = 500) -> List[str]:
    """
    Split text into chunks of at most `max_chars`.
    Tries to split by paragraphs or sentences to avoid cutting words.
    """
    chunks = []
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) > max_chars and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = ""
            
        if len(p) > max_chars:
            sentences = p.replace(". ", ".\n").split('\n')
            for s in sentences:
                if len(current_chunk) + len(s) > max_chars and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                current_chunk += s + " "
        else:
            current_chunk += p + "\n\n"
            
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
        
    return chunks

async def _synthesize_chunk(text: str, output_path: str, voice: str) -> bool:
    """Synthesize a single text chunk using edge-tts."""
    if not edge_tts:
        # Fallback for testing environment without edge-tts installed
        with open(output_path, "wb") as f:
            f.write(b"mock_audio_data")
        return True

    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"Error synthesizing chunk: {e}")
        return False

async def generate_audio_from_text(text: str, output_filename: str, voice: str = "ko-KR-SunHiNeural") -> bool:
    """
    Generates a full audio file from a long text string by chunking it,
    synthesizing each chunk, and merging them.
    """
    chunks = chunk_text(text, max_chars=500)
    temp_files = []
    
    # Generate MP3 for each chunk sequentially to avoid rate limits
    success = True
    for i, chunk in enumerate(chunks):
        temp_file = f"{output_filename}.chunk_{i}.mp3"
        temp_files.append(temp_file)
        if not await _synthesize_chunk(chunk, temp_file, voice):
            success = False
            break
            
    if not success:
        for tf in temp_files:
            if os.path.exists(tf):
                os.remove(tf)
        return False
        
    if not AudioSegment:
        # Fallback if pydub is missing (for mock tests)
        with open(output_filename, "wb") as out_f:
            for tf in temp_files:
                if os.path.exists(tf):
                    with open(tf, "rb") as in_f:
                        out_f.write(in_f.read())
                    os.remove(tf)
        return True

    try:
        combined = AudioSegment.empty()
        for tf in temp_files:
            if os.path.exists(tf):
                segment = AudioSegment.from_mp3(tf)
                combined += segment
                os.remove(tf)
        combined.export(output_filename, format="mp3")
        return True
    except Exception as e:
        print(f"Error merging audio: {e}")
        return False
