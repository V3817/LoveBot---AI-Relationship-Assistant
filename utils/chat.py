from groq import Groq

class ChatManager:
    def __init__(self):
        self.client = None
        self.model = "mixtral-8x7b-32768"
    
    def set_api_key(self, api_key):
        self.client = Groq(api_key=api_key)
    
    def get_response(self, prompt, message_history, knowledge_context=""):
        if not self.client:
            raise Exception("API key not set")
        
        # Prepare messages
        messages = [
            {"role": "system", "content": self._get_system_prompt(knowledge_context)}
        ]
        
        # Add message history
        for msg in message_history[-5:]:  # Only use last 5 messages for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to get response from Groq: {str(e)}")
    
    def _get_system_prompt(self, knowledge_context=""):
        """Generate system prompt including personality insights and knowledge context"""
        base_prompt = "You are LoveBot, an AI relationship assistant. You provide empathetic, helpful advice while maintaining appropriate boundaries. You are knowledgeable about relationship psychology and communication strategies."
        context_parts = [base_prompt]
        
        try:
            # Get personality insights from session state if available
            import streamlit as st
            if "quiz_insights" in st.session_state:
                insights = st.session_state.quiz_insights
                context_parts.append(f"""
The user has completed a personality quiz with the following insights:
- Love Language: {insights['love_language']}
- Conflict Style: {insights['conflict_style']}
- Social Style: {insights['social_style']}
Please consider these personality traits when providing advice.""")
        except:
            pass
        
        # Add knowledge base context if available
        if knowledge_context:
            context_parts.append(f"""
Relevant information from my knowledge base:
{knowledge_context}
Use this information to provide more detailed and accurate advice.""")
        
        return "\n\n".join(context_parts)
