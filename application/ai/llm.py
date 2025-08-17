from langchain_openai import ChatOpenAI
import os

actor_llm = ChatOpenAI(
    model_name="gpt-4.1-mini-2025-04-14",
    temperature=0.5,
    api_key=os.getenv('OPENAI_API_KEY')
)

director_llm = ChatOpenAI(
    model_name="gpt-4.1-2025-04-14",
    temperature=0.3,
    api_key=os.getenv('OPENAI_API_KEY')
)
