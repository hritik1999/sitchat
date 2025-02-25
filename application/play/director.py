from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from application.ai.llm import llm

class Director:

    def __init__(self,llm,show,description,background,actors,player,relations):

        self.show = show
        self.description = description
        self.background = background
        self.actors = actors
        self.player = player
        self.relations = relations
        self.llm = llm

        self.system_prompt = f"""You are the director of a drama titled "{show}". Your role is to guide the narrative while ensuring consistency in character development, relationships, and plot progression. 

            Description of the show: {description}

            Background of the current play: {background}

            Characters and their descriptions: {actors}

            Relationships among the characters: {relations}

            Note: There is also a player who is part of the show, but you must not direct or give instructions to the player.
            Player description: {player}
            """
        
    def generate_outline(self,chat_history,plot_objective,plot_failure_reason=''):
        outline_prompt = f"""
                Given the characters, their relationships, and the chat history for the events till now, please perform the following:

                1. **Summarize** the events that have unfolded so far in a concise yet detailed using background and chat history. Highlight key character interactions and turning points.
                2. **Outline** a detailed narrative continuation for the upcoming scene. Ensure that this outline:

                - Seamlessly continues from the existing script.
                - Gradually drives the plot toward the specified plot objective and achieves the plot objective while avoiding abrupt twists.
                -the content should consistent with the characters' images.
                - Your output should describe what will happen next without using a dialogue script format. 
                - All characters mentioned must remain in the scene.
                - Do not include events that have already occurred, and avoid introducing premature plot twists. 
                - Do not disregard the existing script or introduce developments beyond the specified objective.
                - Do not include the player in your outline but make the characters engage with him.

                Make sure that your continuation is coherent and maintains the overall mood and style of the show.

                Output your result in JSON format. Example:
                    ```
                    {{"previous_outline": "Summary of the existing script", "new_outline": "Continuation for the upcoming script"}}
                    ```

                    chat_history: {chat_history}
                    plot_objective to achieve: {plot_objective}
                    {plot_failure_reason}

                Return only a valid JSON string without any markdown or additional formatting.

                """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=outline_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | self.llm 
        outline = chain.invoke({})
        return outline.content
    
    def generate_turn_instructions(self,chat_history,outline,num_lines=10):
        dialogue_turn_prompt = f"""
            Given the established characters and the detailed narrative outline for the upcoming scene, please convert the outline into a script format with up to {num_lines} lines. Follow these guidelines:

            1. Ensure each line builds naturally on the previous events, maintaining narrative continuity.
            2. Use keywords and brief instructions rather than explicit dialogue, allowing actors creative freedom in their performance.
            3. Ensure that the transitions between lines are smooth and that the overall tone remains consistent with the show's style.
            4. Use character dialogues to replace Narration wherever possible.
            5. Do not include the player in your script but instruct the characters to engage the player if required.
            6. If the outlined events are covered before reaching {num_lines} lines, you may stop early.

            Your output should be a JSON object with a key "scripts" whose value is a list of dictionaries. Each dictionary should have:
            - "role": Either one of the characters in the scene or "Narration" (do not include the player).
            - "instruction" (or "content" if it is narration): A brief, keyword-driven guideline for how the line should be performed.

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
        chain = chat_prompt | self.llm 
        script = chain.invoke({})
        return script.content
    
    def check_objective(self,chat_history,plot_objective):
        check_objective_prompt = f"""
        Given the plot objective of this scene and chat history, please determine whether the existing script has achieved the plot objective or similar result as the plot objective.

        You should output your answer in JSON format. Give your result in "completed", and explain your reason in "reason". Format example:
        
        {{"completed": true or false, "reason": "Your reason"}}

        chat_history: {chat_history}
        plot objective: {plot_objective}

        Return only a valid JSON string without any markdown or additional formatting.
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=check_objective_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | self.llm 
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