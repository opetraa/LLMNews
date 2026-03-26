import os
import asyncio
from src.research_agent import ResearchAgent
from src.llm_backend import get_model

class ScriptWriter:
    """
    Generates a podcast transcript (monologue format) by chaining Vertex AI calls 
    for 20 distinct micro-segments of the weekly tech podcast.
    """
    def __init__(self):
        # Use gemini-1.5-flash for reliability and speed
        self.model = get_model("gemini-1.5-flash")
        self.researcher = ResearchAgent()
        
        self.segments = [
            "Part 1: Key Tech News Headlines of the Week",
            "Part 2: Proprietary AI Models (GPT, Claude) Updates",
            "Part 3: Open Source AI Models (Llama, Mistral) Updates",
            "Part 4: Local AI and Small Language Models (SLMs)",
            "Part 5: Hardware & Chips (Nvidia, AMD, Apple Silicon)",
            "Part 6: RAG (Retrieval-Augmented Generation) Innovations",
            "Part 7: Vector Databases and Search Technology",
            "Part 8: Agentic AI and Autonomous Frameworks",
            "Part 9: AI in Healthcare and Biotech",
            "Part 10: AI in Finance and FinTech",
            "Part 11: Developer Tooling (Cursor, Copilot, LangChain)",
            "Part 12: Cybersecurity and AI Red Teaming",
            "Part 13: Big Tech Rumors and Corporate Moves",
            "Part 14: Legal, Copyright, and AI Regulations",
            "Part 15: Interesting Github Repositories to Watch",
            "Part 16: Noteworthy Arxiv Papers of the Week",
            "Part 17: Machine Learning Optimization Techniques",
            "Part 18: UX/UI Trends in AI Products",
            "Part 19: AI Ethics and Social Impact",
            "Part 20: Actionable Insight of the Week (Wrap-up)"
        ]

    async def _generate_segment_script(self, segment_title: str, context: str) -> str:
        prompt = (
            f"You are a professional tech podcast solo host. "
            f"Write a charismatic, fast-paced radio transcript (about 2-3 minutes spoken, around 300 words) "
            f"for the specific segment: '{segment_title}'.\n"
            f"Use the following real-time research context strictly as your source material:\n"
            f"Context: {context}\n\n"
            f"Do not output markdown or meta-text like 'Host:', just the raw spoken words."
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
            return f"We experienced a slight technical hiccup gathering full info for {segment_title}, but we are moving right along.\n\n"

    async def generate_full_episode_script(self) -> str:
        """
        Generates the script for all 20 parts sequentially to avoid context overflow
        and rate limits, then merges them into one giant text block.
        """
        full_script = "Welcome to the Weekly Tech Podcast! I'm your AI host, and we have a massive 20-part deep dive into this week's tech news.\n\n"
        
        for i, segment in enumerate(self.segments):
            print(f"Researching [{i+1}/20]: {segment}")
            context = self.researcher.gather_context_for_segment(segment)
            
            print(f"Writing script for [{i+1}/20]: {segment}")
            script = await self._generate_segment_script(segment, context)
            full_script += script
            
            # Rate limiting mitigation for GCP quotas
            await asyncio.sleep(2)
            
        full_script += "Wow, what an incredible week in tech. Thank you for listening to this full hour deep dive. See you next week!"
        return full_script
