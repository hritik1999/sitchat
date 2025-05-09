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
            # role
            You are the Creative Director of the TV show titled "{show}" on an interactive storytelling platform. The show unfolds as a group chat in which you guide AI-controlled characters. Your primary responsibility is to craft an engaging narrative for the player while maintaining coherent character development, authentic relationships, and compelling plot progression.
            # Show Details
            - Name: {show}
            - Description: {description}
            - Current Scenario: {background}
            - Characters: {actors}
            - Character Relationships: {relations}
            # PLAYER INTEGRATION
            A human player participates as a character in this experience. Unlike the AI-controlled characters you direct, the player has full agency and makes their own choices. Your role is to create meaningful interactions between the AI characters and the player.

            Player Name: {player.name}
            Player Description: {player.description}

            # OBJECTIVES

            - Balance a scripted narrative with player agency
            - Adapt the story dynamically based on player actions
            - Deliver emotionally resonant story beats
            - Preserve the established tone and rules of the world
                        """
        
    def generate_outline(self,chat_history,plot_objective):
        outline_prompt = f"""
            # Instructions

            Given the current scenario, chat history, character details, and player interactions, please:
            1. Create a Comprehensive Story Summary
            - Provide a chronological narrative of all key events that have occurred
            - Analyze character development arcs, including both AI characters and the player character
            - Identify significant decisions, turning points, and their consequences
            - Note established relationships, conflicts, and emotional dynamics
            - Highlight the player's specific choices and their impact on the narrative
            2. Develop the Next Scene Outline
            - Create a natural progression from established events
            - Maintain consistency with character motivations and personalities
            - Integrate consequences of previous player choices
            - Advance meaningfully toward the plot objective
            - Include potential decision points for player agency
            - Build appropriate tension that serves the overall narrative
            3. Constraints for Scene Development
            - Focus on narrative description rather than dialogue scripting
            - Maintain established tone, world rules, and character voices
            - Avoid forced plot developments or artificial twists
            - Ensure continuity with previous events
            - Create meaningful stakes that connect to the plot objective
            - Provide organic opportunities for player choice and impact
            # Context
            ##Chat History:
            {chat_history}
            ##Plot Objective:
            {plot_objective}

            Output Format
            Please provide your response as a properly formatted JSON object with two main sections:

            json
            ```
            {{
            "previous_outline": "A comprehensive analysis of the narrative so far, including key events, character development, player choices, and their consequences.",
            "new_outline": "A detailed outline for the next scene that advances the story while providing meaningful player agency."
            }}```
            Note: Ensure your JSON is properly formatted with escaped quotes and valid syntax. Focus on creating content that maintains the established tone of the show while advancing naturally toward the plot objective.
                """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=outline_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | self.llm 
        outline = chain.invoke({})
        return outline.content
    
    def generate_turn_instructions(self,chat_history,outline,plot_failure_reason='None',plot_objective='',num_lines=5):
        dialogue_turn_prompt = f"""
            #Instruction for Script Creation
            ##Core Task
            Transform the provided outline into an actionable script that advances the narrative while prioritizing player engagement and narrative coherence.
            
            ##Script Parameters
            - Generate exactly {num_lines} script elements (or fewer if the outline completes naturally)
            - Each element must be either:
                - Character instruction (role + action guidance)
                - Brief narrative direction (scene-setting or transition)

            ## Script Writing Guidelines
            ### Character Instructions:
                - Use concise, actionable direction rather than spelled-out dialogue
                - Specify emotional tone, intent, and key information to convey
                - Allow flexibility for natural performance and improvisation

            ### Narrative Elements:
                - Keep scene-setting brief and visual
                - Focus on atmosphere, environment changes, and non-verbal action
                - Use narration sparingly - prioritize character interactions

            ### Player Engagement (CRITICAL):
                - If the player has contributed, address them in the first script element
                - Ensure characters acknowledge player by name when interacting
                - Create meaningful interaction opportunities that respect player agency
                - Never dictate player emotions, thoughts, or decisions

            ### Narrative Coherence:
                - Follow logical progression from chat history and outline
                - Maintain established character personalities and dynamics
                - Address plot failure reasons subtly through character behavior
                - Skip any outline elements already covered in chat history

            ## Script Structure Priorities
            - Address player input immediately if present
            - Progress narrative according to outline
            - Correct course if plot failure is identified
            - Conclude naturally if outline is completed before reaching line limit

            ## Content Constraints
            - NEVER repeat scenes or dialogue already in chat history
            - NEVER narrate the player's feelings, thoughts, or decisions
            - NEVER ignore player contributions or agency
            - NEVER include explicit dialogue - use intent-based instructions instead

            # Context Resources

                ## Outline: 
                    {outline}
                ## Chat History: 
                    {chat_history}
                ## Plot Objective:
                    {plot_objective}
                ## Plot Failure Reason: 
                    {plot_failure_reason}

            Output Format
            Return only a valid JSON object with the following structure:
            json
            ```{{
            "scripts": [
                {{"role": "CHARACTER_NAME", "instruction": "ACTION_GUIDANCE"}},
                {{"role": "Narration", "content": "BRIEF_SCENE_SETTING"}},
                ...
            ]
            }}```

            Ensure strict JSON formatting with proper escaping of special characters. Provide no additional commentary outside the JSON object.
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
                # Instruction

                Given the plot objective of this scene and the chat history, determine whether the existing script has achieved the plot objective or a similar result.

                ## Output Format

                Provide your answer as valid JSON in the following format:

                ```
                {{"completed": true or false, "reason": "Your reason"}}
                ```

                Return only a valid JSON string without any additional formatting or commentary.

                ## Context Variables

                chat_history: {chat_history}
                plot objective: {plot_objective}

                - `chat_history`: The dialogue and narration that has occurred so far.
                - `plot_objective`: The intended goal or outcome of the scene.

                Example:
                ```
                {{"completed": false, "reason": "The chat history does not clearly show the protagonist confronting their fears."}}
                {{"completed": true, "reason": "The chat history clearly shows the protagonist confronting their fears, which matches the plot objective."}}
                ```
                """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=check_objective_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | self.llm 
        objective_status = chain.invoke({})
        return objective_status.content

    def detect_achievements(self, chat_history, player_name, achievements):
        achievement_prompt = f"""
            # Role and Objective
            You are an Achievement Analyzer for an interactive game experience. Your job is to identify memorable moments from the player's session that deserve recognition as achievements.

            # Instructions
            Analyze the chat history between the player {player_name} and game characters. Identify the MOST noteworthy interactions or moments that qualify as achievements.

            ## Core Requirements
            - Only create achievements for moments where the player participated through their own messages that is "{player_name}:" is in the chat history.
            - Do NOT create achievements when the player was merely mentioned by characters
            - Do NOT create achievements for scenes where the player was passive or didn't send messages
            - Do NOT create achievements for generic interactions that lack specific memorable qualities

            ## Scoring Guidelines
            - **Score 5**: landmark moments that changed the course of interaction or created an iconic reference
            - **Score 4**: Very memorable moments with unique player contributions that stand out but aren't series-defining
            - **Score 3**: Notable moments where the player had a meaningful role that advanced the interaction in an interesting way
            - **Score 2**: Minor but still interesting player-driven moments with some uniqueness
            - **Score 1**: Basic player interactions with minimal significance; use as a last resort

            ## Diversity and Past Achievements
            - Each achievement must differ significantly in theme and content from others
            - Compare against Past Achievements listed in the prompt and do NOT repeat or closely mirror any previously awarded achievement

            # Reasoning Steps
            Before finalizing each achievement, verify:
            1. Did the player ACTIVELY participate with their own messages? If not, no achievement should be awarded
            2. Is the score truly justified by the rarity and memorability of the interaction?
            3. Does this achievement differ from past achievements already awarded?
            4. Is the achievement specific and descriptive enough for social media sharing?

            # Output Format
            Return a JSON array with AT MOST 2 achievements. If no truly significant achievement-worthy moments occurred, return an empty array [].

            Each achievement must include:
            - "title": A catchy, social-media-shareable title clearly indicating what the player accomplished
            - "reason": A concise explanation of why this moment qualifies as an achievement and justification for the score
            - "score": An integer from 1 to 5 based on the criteria above

            # Examples

            ## Example 1: High-Scoring Achievement
            ```
            [
            {{
            "title": "Helped Ross PIVOT! A Couch Up The Stairs",
            "reason": "Player actively participated in the iconic couch-moving scene by suggesting the pivot technique that became a series-defining moment.",
            "score": 5
            }}
            ]
            ```

            ## Example 2: Medium-Scoring Achievement
            ```
            [
            {{
            "title": "Helped Phoebe Name Her New Cat",
            "reason": "Player suggested the name that Phoebe ultimately chose, contributing to a quirky subplot in a meaningful way.",
            "score": 3
            }}
            ]
            ```

            ## Example 3: Low-Scoring Achievement
            ```
            [
            {{
            "title": "Exchanged Witty Banter with Chandler",
            "reason": "Player engaged in some back-and-forth humor with Chandler, though the interaction wasn't particularly significant to the overall story.",
            "score": 2
            }}
            ]
            ```

            ## Example 4: No Achievement
            ```
            []
            ```

            ## Example 5: Examples of BAD achievements (DO NOT USE)
            - "Got mentioned by Ross during a conversation"
            - "Was in the room when Monica cleaned"
            - "Watched Phoebe sing Smelly Cat"

            # Context
            Chat history: {chat_history}
            Player name: {player_name}
            Past Achievements: {achievements}

            # Final instructions
            Think step by step when analyzing the chat history. Identify moments of active player participation first, then evaluate their significance based on the scoring guidelines. Carefully compare potential achievements against past ones to ensure diversity. Return only a valid JSON array without any markdown or additional formatting.
            """

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=achievement_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | self.llm
        achievements = chain.invoke({})
        return achievements.content