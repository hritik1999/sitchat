from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from application.ai.llm import director_llm

class Director:

    def __init__(self,llm,show,description,background,actors,player,relations):

        self.show = show
        self.description = description
        self.background = background
        self.actors = actors
        self.player = player
        self.relations = relations
        self.llm = llm

        self.system_prompt = f"""
            You are the creative director of a dramatic experience titled "{show}". Your primary responsibility is to orchestrate an engaging narrative while maintaining coherent character development, authentic relationships, and compelling plot progression.

            SHOW Details:
            - Name: {show}
            - Description: {description}
            - Current Scenario: {background}

            CHARACTER DESCRIPTIONS:
            {actors}

            RELATIONSHIP DESCRIPTIONS:
            {relations}

            PLAYER INTEGRATION:
            There is a human player participating as a character in this experience. Unlike the other characters you guide, the player has agency and makes their own choices. Your role is to create meaningful interactions between the AI-controlled characters and the player.

            - Player:
            - Name: {player.name}
            - Description: {player.description}

            YOUR OBJECTIVES:
            1. Create emotionally resonant story beats
            2. Ensure character consistency while allowing growth
            3. Balance scripted narrative with player agency
            4. Adapt the story based on player actions
            5. Maintain the established tone and world rules

            Remember that exceptional direction creates moments of both conflict and connection, pushing characters to reveal their true selves while progressing the overarching narrative.
            """
        
    def generate_outline(self,chat_history,plot_objective):
        outline_prompt = f"""
                As the director, analyze the current narrative trajectory and develop the next story phase following these steps:

                1. NARRATIVE ANALYSIS
                Synthesize the key events, character decisions, and emotional beats from the chat history. Focus on:
                • Major character revelations
                • Relationship developments
                • Critical decisions and their consequences
                • Player character's actions and their impact

                2. NARRATIVE CONTINUATION
                Create a compelling continuation that:
                • Naturally progresses from established events
                • Strategically advances toward the plot objective: {plot_objective}
                • Incorporates authentic character reactions based on their established traits
                • Creates opportunities for meaningful player involvement
                • Introduces appropriate dramatic tension without forced plot twists
                • Maintains all current characters in the scene

                3. NARRATIVE CONSTRAINTS
                • Do not contradict established events or character traits
                • Do not prematurely resolve the plot objective
                • Do not introduce plot elements disconnected from the current trajectory
                • Do not ignore the player's previous actions or choices

                Output your result in JSON format. Example:
                    ```
                    {{"previous_outline": "Summary of the existing script", "new_outline": "Continuation for the upcoming script"}}
                    ```

                Chat history: 
                {chat_history}

                Plot objective: 
                {plot_objective}

                Return only valid JSON with no additional formatting or commentary.
                """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=outline_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | self.llm 
        outline = chain.invoke({})
        return outline.content
    
    def generate_turn_instructions(self,chat_history,outline,plot_failure_reason='',plot_objective='',num_lines=6):
        dialogue_turn_prompt = f"""
            Transform the narrative outline into performable script instructions using these directorial guidelines:

            1. SCRIPT FRAMEWORK
            • Create up to {num_lines} script elements
            • Each element should be either character dialogue/action or brief narration
            • Script should flow naturally from previous events in chat history
            • If the outline objectives are met before reaching {num_lines}, conclude organically

            2. CHARACTER DIRECTION
            • Prioritize player engagement - if player has spoken, address them first
            • Provide emotional context and motivation rather than verbatim dialogue
            • Instructions should suggest intent while allowing creative interpretation
            • Ensure each character remains true to their established personality

            3. NARRATIVE TECHNIQUES
            • Show, don't tell - minimize narration when character actions can convey the same information
            • Create opportunities for meaningful player response
            • Never narrate the player's feelings or decisions
            • If addressing {plot_failure_reason}, incorporate subtle course correction

            4. SCRIPT PROGRESSION
            • Each line should meaningfully advance the outline's objectives
            • Create natural transitions between speakers/actions
            • Skip any elements from the outline that have already occurred in the chat history
            • Focus exclusively on developing new narrative elements that haven't yet been covered
            • Continue the story from where the chat history ends without redundancy

            FORMAT YOUR RESPONSE AS:
            ```json
                        {{"scripts": [{{"role": "Alice", "instruction": "..." }}, {{"role": "Bob", "instruction": "..." }}, {{"role": "Narration", "content": "..." }}, ...]}}
            ```
            
            Outline: 
                {outline}

            Chat history: 
                {chat_history}
            
            Plot failure reason: 
                {plot_failure_reason}

            Return only valid JSON with no additional formatting or commentary.
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