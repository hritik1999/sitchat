from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from application.ai.llm import llm

class Actor:
    def __init__(self, name, description, relations, background, llm):
        self.name = name
        self.description = description
        self.relations = relations
        self.background = background
        self.llm = llm

        self.system_prompt = f"""You are an actor in a drama. Your role is {name}.

        Character description for role {name}: {description}

        Background of the script: {background}

        Your relationships with the other characters: {relations}

        Based on the information above, I will tell you the script that has unfolded so far in the play. Please role-play as {name} and respond with an appropriate line of dialogue.

        Do not role-play other characters; generate only what your character would say. Avoid multi-turn responses; generate only the next line. Do not repeat the existing script. You can output only one line of text.

        A director will guide you on how to better embody your role. Consider the context, director's guidance, your character's description, and the existing script. Use this information to generate the most fitting line of dialogue as an actor.
        """

    def reply(self,chat_history, instructions):

        actor_prompt = f"""The script so far is as follows: {chat_history}

                            Director's instructions: {instructions}

                            {self.name}:
                        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=actor_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | llm 
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
