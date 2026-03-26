import os
import logging
import traceback
from src.llm_backend import get_model

try:
    from vertexai.generative_models import Tool, grounding
except ImportError:
    Tool = None
    grounding = None

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    Research Agent that gathers daily/weekly context for the 5 segments using Vertex AI.
    It uses Gemini with Google Search Grounding for real-time web search capabilities.
    """
    def __init__(self, api_key: str = None):
        # API keys are no longer needed for Google Search Grounding (handled by Workload Identity)
        self.model = get_model("gemini-2.5-flash") # Using flash for faster research
        
        self.search_tool = None
        if Tool and grounding:
            # Enable Google Search Grounding
            self.search_tool = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())
        else:
            logger.warning("Vertex AI SDK missing Tool/grounding. Will run without Google Search Grounding.")
        
    def gather_context_for_segment(self, segment_title: str) -> str:
        """
        Gathers text content relevant to the segment using Vertex AI Search Grounding.
        Returns a rich text summary to be used as context for the script writer.
        """
        logger.info(f"Gathering Vertex AI Search Grounding context for: {segment_title}")
        
        prompt = (
            f"You are an expert tech podcast researcher. Please search the live internet for "
            f"the absolute latest news, breakthroughs, and discussions happening this week regarding: '{segment_title}'.\n"
            f"Provide a very detailed, actionable summary of the most important points. Include specific facts and recent events."
        )
        
        if not self.model:
            logger.warning("GenerativeModel is None. Cannot perform real-time research.")
            return f"Mock search context for: {segment_title}"
            
        try:
            kwargs = {}
            if self.search_tool:
                kwargs["tools"] = [self.search_tool]
                
            response = self.model.generate_content(prompt, **kwargs)
            return response.text
        except Exception as e:
            logger.error(f"Error gathering context for {segment_title}: {e}")
            logger.error(traceback.format_exc())
            return f"General tech trends for the week regarding {segment_title}: Focus on performance and generative capabilities."
