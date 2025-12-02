from langchain_openai import ChatOpenAI
from langchain_sambanova import ChatSambaNova
from config import settings

SAMBANOVA_MODELS = {
    "deepseek-r1": "DeepSeek-R1-0528",
    "deepseek-v3": "DeepSeek-V3-0324",
    "deepseek-v3.1": "DeepSeek-V3.1",
    "deepseek-r1-distill": "DeepSeek-R1-Distill-Llama-70B",
    "llama-3.3-70b": "Meta-Llama-3.3-70B-Instruct",
    "llama-3.1-8b": "Meta-Llama-3.1-8B-Instruct",
    "qwen3-32b": "Qwen3-32B",
}

def get_llm(model_name: str, openai_api_key: str = None, sambanova_api_key: str = None):
    # Determine which keys to use
    
    if model_name not in SAMBANOVA_MODELS:
        api_key = openai_api_key if (settings.allow_user_keys and openai_api_key) else None
        return ChatOpenAI(
            model=settings.default_model, 
            temperature=0, 
            streaming=True,
            api_key=api_key
        )
    
    is_reasoning = "r1" in model_name.lower()
    api_key = sambanova_api_key if (settings.allow_user_keys and sambanova_api_key) else None
    
    return ChatSambaNova(
        model=SAMBANOVA_MODELS[model_name],
        max_tokens=settings.sambanova_max_tokens,
        temperature=settings.sambanova_reasoning_temperature if is_reasoning else 0,
        top_p=settings.sambanova_reasoning_top_p if is_reasoning else settings.sambanova_standard_top_p,
        streaming=True,
        sambanova_api_key=api_key
    )
