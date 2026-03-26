import os
import pytest
from src.audio_engine import generate_audio_from_text, chunk_text

@pytest.mark.asyncio
async def test_generate_audio_single_chunk(tmp_path):
    text = "Hello, this is a test for the weekly tech podcast audio engine."
    output_file = str(tmp_path / "test_output.mp3")
    
    # Run the generator
    success = await generate_audio_from_text(text, output_file, voice="en-US-AriaNeural")
    
    assert success is True
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 1000  # Should not be empty

def test_chunk_text():
    # Test that a long text is properly chunked by paragraphs or sentences
    long_text = "This is sentence one.\n\nThis is sentence two. " * 50
    chunks = chunk_text(long_text, max_chars=100)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 100
