from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model_name="llama3.2:3b-instruct-fp16",
    base_url="http://localhost:11434/v1",
    temperature=0
)