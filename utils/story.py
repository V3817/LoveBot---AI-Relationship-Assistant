from typing import Dict, List, Optional
import random

class StoryManager:
    def __init__(self):
        self.scenarios = [
            {
                "id": "communication",
                "title": "Communication Challenge",
                "prompt": "You're trying to express your feelings about an important issue, but your partner seems distracted. What do you do?",
                "options": [
                    "Wait for a better time to talk",
                    "Express your frustration directly",
                    "Try a different approach to get their attention",
                    "Write down your thoughts first"
                ]
            }
        ]
    
    def build_context(self, user_story: str, chat_history: List[Dict], 
                     personality_data: Optional[Dict], knowledge_base_manager) -> str:
        """Build context from available data sources"""
        context_parts = []
        
        # Add the user's story
        context_parts.append(f"User's Story:\n{user_story}\n")
        
        # Add personality insights
        if personality_data:
            context_parts.append(f"""
Personal Profile:
- Love Language: {personality_data.get('love_language', 'Unknown')}
- Conflict Style: {personality_data.get('conflict_style', 'Unknown')}
- Social Style: {personality_data.get('social_style', 'Unknown')}
""")
        
        # Add relevant chat history
        if chat_history:
            recent_chats = chat_history[-5:]  # Get last 5 interactions
            chat_context = "\nRecent Interactions:\n"
            for msg in recent_chats:
                chat_context += f"- {msg['role']}: {msg['content'][:100]}...\n"
            context_parts.append(chat_context)
        
        # Get relevant knowledge base information
        if knowledge_base_manager:
            try:
                search_terms = [
                    "relationship dynamics",
                    "emotional connection",
                    "communication patterns",
                    user_story[:100]  # Use start of story for context
                ]
                kb_contexts = []
                for term in search_terms:
                    context = knowledge_base_manager.get_relevant_context(term)
                    if context:
                        kb_contexts.append(context)
                if kb_contexts:
                    context_parts.append("\nRelevant Knowledge:\n" + "\n".join(kb_contexts))
            except Exception as e:
                print(f"Error getting knowledge base context: {e}")
        
        return "\n".join(context_parts)
    
    def continue_user_story(self, user_story: str, chat_history: List[Dict], 
                          personality_data: Optional[Dict] = None, 
                          knowledge_base_manager=None) -> str:
        """Generate personalized story continuation"""
        context = self.build_context(user_story, chat_history, personality_data, knowledge_base_manager)
        try:
            from groq import Groq
            import os
            client = Groq(api_key=os.environ["GROQ_API_KEY"])
            system_prompt = """You are a skilled storyteller and relationship advisor. 
Using the provided context about the user's personality, relationship history, and knowledge base,
continue their story in a way that:
1. Maintains consistency with their personality traits and communication style
2. Incorporates relevant relationship insights
3. Provides meaningful character development
4. Offers subtle guidance while staying engaging
Keep the continuation natural and personal, weaving in elements from their profile and history."""
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nPlease continue this story..."}
            ]
            response = client.chat.completions.create(
                messages=messages,
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I apologize, but I encountered an error generating the story continuation: {str(e)}"
    
    def get_story_prompts(self, personality_data: Optional[Dict] = None) -> List[str]:
        """Generate personalized story prompts"""
        base_prompts = [
            "Tell me about a time when you had to make a difficult decision in a relationship...",
            "Share a story about a moment of connection or disconnect with someone important to you...",
            "Write about a situation where you wished you had communicated differently..."
        ]
        if personality_data:
            love_language = personality_data.get('love_language', '').lower()
            if "words of affirmation" in love_language:
                base_prompts.append("Share a story about expressing your feelings to someone special...")
            elif "quality time" in love_language:
                base_prompts.append("Tell me about a meaningful moment you shared with someone...")
        return base_prompts
    
    def get_random_scenario(self) -> Dict:
        """Return a random scenario"""
        return random.choice(self.scenarios)
    
    def get_scenario_by_id(self, scenario_id: str) -> Optional[Dict]:
        """Get a specific scenario by ID"""
        for scenario in self.scenarios:
            if scenario["id"] == scenario_id:
                return scenario
        return None
    
    def get_reflection_prompts(self, scenario_id: str, choice: str, 
                             personality_data: Optional[Dict] = None) -> List[str]:
        """Generate reflection prompts"""
        base_prompts = [
            "How did this choice align with your usual approach to similar situations?",
            "What did you learn about yourself from this scenario?",
            "How might this experience influence your future interactions?"
        ]
        scenario_specific_prompts = {
            "communication": [
                "How comfortable are you expressing your needs in relationships?",
                "What role does timing play in your communication style?"
            ],
            "boundaries": [
                "How do you typically handle boundary violations in relationships?",
                "What makes it easy or difficult for you to set boundaries?"
            ],
            "conflict": [
                "What is your usual approach to handling disagreements?",
                "How do you balance your needs with those of your partner?"
            ]
        }
        personal_prompts = []
        if personality_data:
            love_language = personality_data.get('love_language', '').lower()
            if "words of affirmation" in love_language:
                personal_prompts.append("How does your preference for verbal expression influence your decisions?")
            elif "quality time" in love_language:
                personal_prompts.append("How does your value of quality time affect your approach to relationships?")
        return base_prompts + scenario_specific_prompts.get(scenario_id, []) + personal_prompts
