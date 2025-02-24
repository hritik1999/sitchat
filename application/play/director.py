from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from application.ai.llm import llm

class Director:

    def __init__(self,show,description,background,actors,player,relations):

        self.show = show
        self.description = description
        self.background = background
        self.actors = actors
        self.player = player
        self.relations = relations

        self.system_prompt = f"""You are the director of a drama. You are directing "{show}".

            Description of the show: {description}

            Background of the current play: {background}

            Characters and their descriptions: {actors}

            Relationships among the characters: {relations}

            Note: There is also a player in the show whom you cannot direct or give instructions to, but your goal is to keep them engaged and entertained by instructing the actors.
            Player description: {player}
            """
        
    def generate_outline(self,chat_history,plot_objective):
        outline_prompt = f"""
            Given the characters and the existing script for this scene, please first summarize what has happened in the plot so far.

            Then, based on the relationships and the chat history between characters, write a detailed continuation for the upcoming script. Ensure that the combined plot of the current scene and the continuation adheres strictly to the given plot objective, and that the content is consistent with the characters' images.

            The existing script may have partially achieved the plot objective. You must follow the requirements of the plot objective closely, continuing the existing script and gradually developing the plot. Do not disregard the existing script or introduce developments beyond the specified objective.

            Your output should describe what will happen next without using a dialogue script format. Do not include events that have already occurred, and avoid introducing premature plot twists. All characters mentioned must remain in the scene.

            Output your result in JSON format. Example:
            ```
            {{"previous_outline": "Summary of the existing script", "new_outline": "Continuation for the upcoming script"}}
            ```
            chat_history: {chat_history}
            plot_objective: {plot_objective}

            Return only a valid JSON string without any markdown or additional formatting.
            """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=outline_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | llm 
        outline = chain.invoke({})
        return outline.content
    
    def generate_turn_instructions(self,chat_history,outline,num_lines=10):
        dialogue_turn_prompt = f"""
        Given the characters and the outline of the upcoming plot for this scene, please translate the plot outline into a script format consisting of up to {num_lines} lines. Ensure that the new lines follow the storyline and seamlessly connect with the preceding script.

        Develop the script gradually and enrich the details based on the provided plot outline. If the outlined events are covered before reaching {num_lines} lines, you may stop early.

        Ensure your continuation smoothly integrates with the existing script. Prefer character dialogues over narration when possible.

        Output the script continuation in JSON format. Each line should be a dictionary with keys "role" and "instruction".In the instruction provide a brief synopsis of the upcoming line for the actor. However, do not directly provide a line.use keywords to instruct the actor on how to role-play the character in the next line, so that the actor can play out the dialogue that fits the script.
        The "role" can be "Narration" or one of the characters in the scene but not the player. If it is narration you can send content. 
        Example format:
        ```
        {{"scripts": [{{"role": "Alice", "instruction": "..." }}, {{"role": "Bob", "instruction": "..." }}, {{"role": "Narration", "content": "..." }}, ...]}}
        ```
        chat_history: {chat_history}
        outline of upcoming plot: {outline}

        Return only a valid JSON string without any markdown or additional formatting.
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=dialogue_turn_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | llm 
        script = chain.invoke({})
        return script.content
    
    def check_objective(self,chat_history,plot_objective):
        check_objective_prompt = f"""
        Given the characters and the plot objective of this scene, please determine whether the existing script has included the plot objective.

        You should output your answer in JSON format. Give your result in "completed", and explain your reason in "reason". Format example:
        ```
        {{"completed": true or false, "reason": "Your reason"}}
        ```
        chat_history: {chat_history}
        plot objective: {outline}

        Return only a valid JSON string without any markdown or additional formatting.
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=check_objective_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | llm 
        objective_status = chain.invoke({})
        return objective_status.content
    
# Test code using a Friends TV show example
# if __name__ == "__main__":
#     show = "Friends: The One with the Unscripted Scene"
#     description = "A classic sitcom that follows the humorous misadventures of a group of friends living in New York City."
#     background = "The scene takes place at Central Perk, the coffee shop where the friends gather to chat over coffee."
#     actors = {
#         "Chandler": "Sarcastic and witty, often self-deprecating, with a sharp sense of humor.",
#         "Joey": "Lovable and simple, known for his charm and occasional cluelessness.",
#         "Monica": "Organized, competitive, and caring, always in control.",
#         "Rachel": "Stylish and ambitious, transitioning from her carefree past to a more mature outlook."
#     }
#     relations = {
#         "Chandler": {"Joey": "best friend", "Monica": "husband"},
#         "Joey": {"Chandler": "best friend", "Rachel": "flirt"},
#         "Monica": {"Chandler": "wife", "Rachel": "close friend"},
#         "Rachel": {"Joey": "flirt", "Monica": "close friend"}
#     }
#     player = {"Gunther": "the quiet barista who secretly admires Rachel"}

#     chat_history = ("Chandler: Could I *be* any more sarcastic today? "
#                     "Joey: How you doin'? "
#                     "Monica: Guys, let's focus on the coffee. "
#                     "Rachel: I can't decide if this latte is too trendy or not.")
#     plot_objective = ("Reveal a surprising twist that connects Monica's organized nature to "
#                       "Chandler's hidden vulnerabilities, while highlighting Joey's endearing charm.")

#     # Instantiate the Director
#     director = Director(show, description, background, actors, player, relations)

#     # Generate the plot outline
#     outline = director.generate_outline(chat_history, plot_objective)
#     print("Generated Outline:")
#     print(outline)

#     # Generate the script turn instructions using the generated outline
#     script_turn = director.generate_turn_instructions(chat_history, outline, num_lines=6)
#     print("\nGenerated Script Turn:")
#     print(script_turn)