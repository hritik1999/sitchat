from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from application.ai.llm import director_llm
class ScriptStep(BaseModel):
    role: str = Field(..., description="Character name or 'Narration'")
    instruction: Optional[str] = Field(None, description="Instruction guidance for characters")
    content: Optional[str] = Field(None, description="Scene setting for narration if applicable")

class TurnOutput(BaseModel):
    planning: str = Field(..., description="Planning for the next turn.")
    scripts: List[ScriptStep] = Field(..., description="List of script elements with role and instruction or content")

class Achievement(BaseModel):
    title: str = Field(..., description="Achievement title.")
    reason: str = Field(..., description="Justification for the achievement and score.")
    score: int = Field(..., description="Score from 1 to 5.")

class AchievementsOutput(BaseModel):
    achievements: List[Achievement] = Field(..., description="List of detected achievements.")

class ObjectiveCheckOutput(BaseModel):
    completed: bool = Field(..., description="Boolean indicating if objective achieved.")
    reason: str = Field(..., description="Explanation of why or why not.")

class OutlineOutput(BaseModel):
    previous_outline: str = Field(..., description="A comprehensive analysis of the narrative so far, including key events, character development, player choices, and their consequences.")
    new_outline: str = Field(..., description="A detailed outline for the next scene that advances the story while providing meaningful player agency.")

class Director:

    def __init__(self,llm,show,description,background,actors,player,relations):

        self.show = show
        self.description = description
        self.background = background
        self.actors = actors
        self.player = player
        self.relations = relations
        self.llm = llm

         # Parsers using PydanticOutputParser
        self.outline_parser = JsonOutputParser(pydantic_object=OutlineOutput)
        self.turn_parser = JsonOutputParser(pydantic_object=TurnOutput)
        self.check_parser = JsonOutputParser(pydantic_object=ObjectiveCheckOutput)
        self.achievement_parser =JsonOutputParser(pydantic_object=AchievementsOutput)

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
        fmt = self.outline_parser.get_format_instructions()
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
            - A concise paragraph describing a flexible scene framework for the director's script—structured enough to advance the plot toward the objective and achieve it, yet purposefully open-ended so that once the player provides input, the script seamlessly adapts to their choices and propels the narrative dynamically.
            - a natural progression from established events
            - Maintain consistency with character motivations and personalities
            - Integrate consequences of previous player choices
            - Advance meaningfully toward the plot objective and achieve it
            - Include potential decision points for player agency
            3. Constraints for Scene Development
            - Focus on narrative description rather than dialogue scripting
            - Maintain established tone, world rules, and character voices
            - Avoid forced plot developments or artificial twists
            - Ensure continuity with previous events
            - Ensure continuity with all prior events, while allowing the outline to adapt if minor details change.  
            - Create meaningful stakes that connect to the plot objective
            - Offer organic entry points for new player choices, without asking the player to invent essential narrative facts.

            # Context
            ##Chat History:
            {chat_history}
            ##Plot Objective:
            {plot_objective}

            # Output Format
            Please output ONLY valid JSON that conforms to the format instructions below:
            {fmt}
                """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=outline_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | self.llm | self.outline_parser
        outline = chain.invoke({})
        return outline
    
    def generate_turn_instructions(self,chat_history,outline,plot_failure_reason='None',plot_objective='',num_lines=5):
        fmt = self.turn_parser.get_format_instructions()
        dialogue_turn_prompt = f"""
                    # Planning Step
                    ## Before generating any script elements, evaluate:
                    # 1. Is the plot objective already satisfied in chat_history? If yes, return [] immediately.
                    # 2. Does chat_history contain an unresolved player message? If yes, mark it as "unattended".
                    ## Once planning is complete, proceed only if objective not met.

                    # Instruction for Script Creation
                    ## Core Task
                    Transform the provided outline into an actionable script that advances the narrative while prioritizing player engagement and narrative coherence.

                    ## Script Parameters
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

                    ### 1. Plot Objective Check
                        - If the plot objective has been met in chat_history, return an empty list and skip all other steps.

                    ### 2. Player Engagement (CRITICAL)
                        - Do NOT include the player as a scripted character.
                        -(**MOST IMPORTANT**) If there is any player message in chat_history that has not been answered by any character then the FIRST script instruction/element must address the player message immediately.(**MOST IMPORTANT**)
                        - Do not rely on the player to supply key plot details; present clear choices when decision points arise.
                        - Create meaningful interaction opportunities that respect player agency.

                    ### 3. Narrative Coherence
                        - Follow logical progression from chat_history and outline.
                        - Maintain established character personalities and dynamics.
                        - Address subtle reasons for past plot failures through character behavior.
                        - Skip any outline elements already covered in chat_history.

                    ### 4. Script Structure Priorities
                    - Perform the planning step first (see above).
                    - Address unattended player input immediately, if present.
                    - Progress narrative according to outline and scene order.
                    - Introduce choices rather than requiring player-supplied details.
                    - Conclude naturally if outline completes before reaching the line limit.

                    ## Content Constraints
                    - NEVER repeat scenes or dialogue from chat_history.
                    - NEVER narrate the player’s internal states.
                    - NEVER ignore player contributions or agency.
                    - NEVER include explicit dialogue—use intent-based instructions instead.
                    - NEVER include player in the script.
                    - NEVER include player in narration.
                    - AVOID using narration whenever possible i.e use character instructions instead as much as possible.

                    # Context Resources

                        ## Outline: 
                            {outline}
                        ## Chat History: 
                            {chat_history}
                        ## Plot Objective:
                            {plot_objective}
                        ## Plot Failure Reason: 
                            {plot_failure_reason}

                    # Output Format
                    Please output ONLY valid JSON that conforms to the format instructions below:
                    {fmt}
                    """

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=dialogue_turn_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | self.llm | self.turn_parser
        script = chain.invoke({})
        return script
    
    def check_objective(self,chat_history,plot_objective):
        fmt = self.check_parser.get_format_instructions()
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
                # Output Format
                Please output ONLY valid JSON that conforms to the format instructions below:
                {fmt}
                """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=check_objective_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | self.llm | self.check_parser
        objective_status = chain.invoke({})
        return objective_status

    def detect_achievements(self, chat_history, player_name, achievements):
        fmt = self.achievement_parser.get_format_instructions()
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

            # Output Format
            Please output ONLY valid JSON that conforms to the format instructions below:
            {fmt}

            # Final instructions
            Think step by step when analyzing the chat history. Identify moments of active player participation first, then evaluate their significance based on the scoring guidelines. Carefully compare potential achievements against past ones to ensure diversity. Return only a valid JSON array without any markdown or additional formatting.
            """

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=achievement_prompt)
        ]
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | self.llm | self.achievement_parser
        new_achievements = chain.invoke({})
        return new_achievements