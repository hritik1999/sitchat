from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0.5,
    api_key=os.getenv('OPENAI_API_KEY')
)