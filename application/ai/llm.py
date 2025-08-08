from langchain_openai import ChatOpenAI
import os

actor_llm = ChatOpenAI(
    model_name="gpt-5-mini",
    api_key=os.getenv('OPENAI_API_KEY')
)

director_llm = ChatOpenAI(
    model_name="gpt-5-nano",
    api_key=os.getenv('OPENAI_API_KEY')
)