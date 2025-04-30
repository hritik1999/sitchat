from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from application.ai.llm import actor_llm

class Actor:
    def __init__(self, name, description, relations, background, llm):
        self.name = name
        self.description = description
        self.relations = relations
        self.background = background
        self.llm = llm

        self.system_prompt = f"""You are an actor in a drama, portraying the role of {name}.

            Character Description:
            - Role: {name}
            - Description: {description}

            Context:
            - Script Background: {background}
            - Your relationships with other characters: {relations}

            Your task is to provide a single, carefully crafted line of dialogue that is consistent with your character's personality, relationships, and the context of the script. You must strictly follow the director's instructions provided in the prompt and generate only what your character would say. Avoid multi-turn responses, explanations, or narrations.

            Remember:
            - Do not role-play other characters.
            - Do not repeat the existing script.
            - Provide only one line of dialogue that reflects your unique voice and the guidance given by the director.
            """

    def reply(self,chat_history, instructions):

        actor_prompt = f"""Current chat history:
            {chat_history}

            Director's Instructions:
            {instructions}

            Based on the above, please generate your next line of dialogue as {self.name}. Ensure that your response:
            - is a single line
            - Reflects your character's personality and relationships.
            - Strictly adheres to the director's guidance.
            - Advances the scene naturally.

            {self.name}:"""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=actor_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | self.llm 
        dialogue = chain.invoke({})
        return dialogue.content


# actor = Actor(
#     name='Chandler',
#     description='You are Chandler from the famous TV show Friends.',
#     relations={"Joey": "best friend", "Ross": "brother-in-law", "Monica": "wife"},
#     background="You are sitting with Ross, Joey, Monica, and Ross in Central Perk cafe.",
#     llm=llm,
# )

# print(actor.reply(instructions="Tell Ross about the new condom ad you are working on sarcastically.",
#                       chat_history="{'ross': 'How are all of your days?'}"))
