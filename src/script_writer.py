import os
from src.research_agent import ResearchAgent
from src.llm_backend import get_model

class ScriptWriter:
    """
    Generates a podcast transcript (monologue format) by chaining Vertex AI calls 
    for the 5 distinct segments of the weekly tech podcast.
    """
    def __init__(self):
        # gemini-2.5-flash 또는 원하는 모델 지정
        self.model = get_model("gemini-2.5-flash")
        self.researcher = ResearchAgent()
        
        self.segments = [
            "Part 1: Foundation Models & Open Source",
            "Part 2: Papers (RAG & Agents)",
            "Part 3: Industry Insights",
            "Part 4: Engineering Ecosystem",
            "Part 5: Actionable Insights"
        ]

    async def _generate_segment_script(self, segment_title: str, context: str) -> str:
        prompt = (
            f"You are a professional tech podcast solo host. "
            f"Write a charismatic, deep-dive radio transcript (about 5-10 minutes spoken) "
            f"for the segment '{segment_title}'. Use the provided context.\n\n"
            f"Context: {context}\n\n"
            f"Do not output markdown, just the raw spoken words."
        )
        
        if not self.model:
            # Fallback for missing package
            return f"Welcome to {segment_title}. Today we discuss: {context}. That concludes this segment.\n\n"

        try:
            # Vertex AI async generation
            response = await self.model.generate_content_async(prompt)
            return response.text + "\n\n"
        except Exception as e:
            print(f"Error generating script for {segment_title}: {e}")
            return f"[Error generating {segment_title}]\n\n"

    async def generate_full_episode_script(self) -> str:
        """
        Generates the script for all 5 parts sequentially to avoid context overflow,
        then merges them into one giant text block for the Audio Engine.
        """
        full_script = "Welcome to the Weekly Tech Podcast!\n\n"
        
        for segment in self.segments:
            print(f"Researching: {segment}")
            context = self.researcher.gather_context_for_segment(segment)
            
            print(f"Writing script for: {segment}")
            script = await self._generate_segment_script(segment, context)
            full_script += script
            
        full_script += "Thank you for listening. See you next week!"
        return full_script
