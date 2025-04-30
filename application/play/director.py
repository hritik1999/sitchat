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
                As the director, analyze the current chat history and develop the next story phase to achieve the plot objective following these steps:

                1. CHAT HISTORY ANALYSIS
                Synthesize the key events, character decisions, and emotional beats from the chat history. Focus on:
                • Major character revelations
                • Relationship developments
                • Critical decisions and their consequences
                • Player character's actions and their impact
                • Emotional highs and lows
                • Put then in previous outline

                2. CHAT CONTINUATION
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

                Chat history: 
                {chat_history}

                Plot objective: 
                {plot_objective}

                Output your result in JSON format. Example:
                    ```
                    {{"previous_outline": "Summary of the existing script", "new_outline": "Continuation for the upcoming script"}}
                    ```

                Return only valid JSON with no additional formatting or commentary.

                remember -
                1. Your response should be in JSON format.
                2. Ensure the JSON is valid and contains the keys 'previous_outline' and 'new_outline'.
                3. The 'previous_outline' should be a detailed summary of the existing script and 'new_outline' should be the continuation for the upcoming script.
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
            • Prioritize player engagement - if player has spoken, address them first and be rude if required
            • Ask the character to use the player's name
            • Provide emotional context and motivation rather than verbatim dialogue
            • Instructions should suggest intent while allowing creative interpretation
            • Ensure each character remains true to their established personality

            3. NARRATIVE TECHNIQUES
            • Show, don't tell - minimize narration when character actions can convey the same information
            • Create opportunities for meaningful player response
            • Never narrate the player's feelings or decisions
            • If addressing plot failure reason, provide course correction and do not repeat outline in the chat history

            4. SCRIPT PROGRESSION
            • Each line should meaningfully advance the outline's objectives
            • Create natural transitions between speakers/actions
            • Skip any elements from the outline that have already occurred in the chat history
            • Focus exclusively on developing new narrative elements that haven't yet been covered
            • Continue the story from where the chat history ends without redundancy

            
            Outline: 
                {outline}

            Chat history: 
                {chat_history}
            
            Plot failure reason: 
                {plot_failure_reason}

            FORMAT YOUR RESPONSE AS:
            ```json
                        {{"scripts": [{{"role": "Alice", "instruction": "..." }}, {{"role": "Bob", "instruction": "..." }}, {{"role": "Narration", "content": "..." }}, ...]}}
            ```

            Return only valid JSON with no additional formatting or commentary.

            REMEMBER- 
            1. If there is Player message then respond to the player first
            2. If plot failure is given then address that in your script and correct the plot
            3. Never repeat whats already there in the chat history
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
        
        chat_history: {chat_history}
        plot objective: {plot_objective}
        
         {{"completed": true or false, "reason": "Your reason"}}

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
    