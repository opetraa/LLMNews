import os
import logging

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
except ImportError:
    vertexai = None
    GenerativeModel = None

logger = logging.getLogger(__name__)

_initialized = False

def init_vertex() -> None:
    global _initialized
    if _initialized:
        return
        
    if not vertexai:
        logger.warning("google-cloud-aiplatform is not installed. Using mock LLM.")
        return

    project = os.environ.get("GCP_PROJECT", "")
    location = os.environ.get("GCP_LOCATION", "us-central1")
    
    if not project:
        raise RuntimeError("GCP_PROJECT 환경변수가 설정되어 있어야 합니다.")
    
    vertexai.init(project=project, location=location)
    logger.info("Vertex AI Initialized (project=%s, location=%s)", project, location)
    _initialized = True

def get_model(model_name: str = "gemini-2.5-flash") -> "GenerativeModel":
    """주어진 이름의 Vertex AI GenerativeModel 인스턴스를 반환합니다."""
    init_vertex()
    if not GenerativeModel:
        return None
    return GenerativeModel(model_name)
