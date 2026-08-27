import streamlit as st
import uuid
import os
from utils.chat import ChatManager
from utils.content_filter import ContentFilter
from utils.session import SessionManager
from utils.quiz import QuizManager
from utils.knowledge_base import KnowledgeBaseManager
from utils.story import StoryManager
import time

# Page configuration
st.set_page_config(
    page_title="LoveBot - AI Relationship Assistant",
    page_icon="💝",
    layout="wide"
)

# Custom CSS
def load_css():
    with open("styles/chat.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize managers
@st.cache_resource
def init_managers():
    chat_manager = ChatManager()
    return (
        chat_manager,
        ContentFilter(),
        SessionManager(),
        QuizManager(),
        KnowledgeBaseManager(),
        StoryManager()
    )

def display_quiz():
    """Display personality quiz interface"""
    st.header("💭 Personality Quiz")
    st.markdown("Take this quiz to help LoveBot understand you better!")

    quiz_manager = st.session_state.quiz_manager

    if "quiz_responses" not in st.session_state:
        st.session_state.quiz_responses = {}

    if "quiz_completed" not in st.session_state:
        st.session_state.quiz_completed = False

    if not st.session_state.quiz_completed:
        for question in quiz_manager.get_questions():
            response = st.radio(
                question["text"],
                options=question["options"],
                key=f"quiz_{question['id']}"
            )
            if response:
                st.session_state.quiz_responses[question["id"]] = \
                    question["options"].index(response)

        if st.button("Complete Quiz"):
            if len(st.session_state.quiz_responses) == len(quiz_manager.get_questions()):
                insights = quiz_manager.analyze_results(st.session_state.quiz_responses)
                st.session_state.quiz_insights = insights
                st.session_state.quiz_completed = True
                st.rerun()
            else:
                st.warning("Please answer all questions before completing the quiz.")
    else:
        insights = st.session_state.quiz_insights
        st.success("Quiz completed! Here are your results:")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Love Language", insights["love_language"])
        with col2:
            st.metric("Conflict Style", insights["conflict_style"])
        with col3:
            st.metric("Social Style", insights["social_style"])

        st.markdown("### Your Personality Analysis")
        st.markdown(insights["summary"])

        if st.button("Retake Quiz"):
            st.session_state.quiz_completed = False
            st.session_state.quiz_responses = {}
            st.rerun()

def display_knowledge_base():
    """Display knowledge base management interface"""
    st.header("📚 Knowledge Base Management")

    kb_manager = st.session_state.kb_manager

    # File upload
    uploaded_file = st.file_uploader(
        "Upload documents to the knowledge base",
        type=['txt', 'md', 'pdf'],
        help="Supported formats: TXT, MD, PDF"
    )

    if uploaded_file:
        try:
            with st.spinner('Processing document...'):
                doc_id = kb_manager.add_document(file=uploaded_file)
                st.success(f"Document added successfully! ID: {doc_id}")
        except Exception as e:
            st.error(f"Error adding document: {str(e)}")

    # Knowledge base search demo
    st.subheader("Test Knowledge Base")
    search_query = st.text_input("Enter a query to test the knowledge base:")
    if search_query:
        with st.spinner('Searching...'):
            results = kb_manager.search_similar(search_query)
            for idx, result in enumerate(results, 1):
                with st.expander(f"Result {idx}"):
                    st.write(result['content'])
                    st.write("Metadata:", result['metadata'])

def display_story_mode():
    """Display story mode interface"""
    st.header("📖 Story Mode")
    st.markdown("Share your story and get personalized continuations based on your experiences.")

    story_manager = st.session_state.story_manager
    kb_manager = st.session_state.kb_manager

    # User story input
    user_story = st.text_area(
        "Share your story",
        height=200,
        help="Write about a relationship experience, challenge, or situation you'd like to explore.",
        placeholder="Start writing your story here..."
    )

    # Personality insights reminder
    if "quiz_insights" not in st.session_state:
        st.info("💡 Take the personality quiz first to get more personalized story continuations!")

    # Story prompts for inspiration
    with st.expander("Need inspiration? Here are some prompts..."):
        personality_data = st.session_state.get("quiz_insights", None)
        prompts = story_manager.get_story_prompts(personality_data)
        for prompt in prompts:
            st.markdown(f"• {prompt}")

    # Generate continuation button
    if user_story and st.button("Continue my story"):
        with st.spinner("Generating story continuation..."):
            try:
                # Get all context for story continuation
                chat_history = st.session_state.get("messages", [])
                personality_data = st.session_state.get("quiz_insights", None)

                # Generate continuation
                continuation = story_manager.continue_user_story(
                    user_story,
                    chat_history,
                    personality_data,
                    kb_manager
                )

                # Display continuation
                st.markdown("### Story Continuation")
                st.write(continuation)

                # Add to chat history for context
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"Story: {user_story}"
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": continuation
                })

            except Exception as e:
                st.error(f"Error generating story continuation: {str(e)}")

def main():
    # Load CSS
    load_css()

    # Initialize managers
    chat_manager, content_filter, session_manager, quiz_manager, kb_manager, story_manager = init_managers()
    st.session_state.quiz_manager = quiz_manager
    st.session_state.kb_manager = kb_manager
    st.session_state.story_manager = story_manager

    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Sidebar navigation
    with st.sidebar:
        st.title("📍 Navigation")
        
        # API Keys Section
        st.markdown("### 🔑 API Keys")
        groq_key = st.text_input("Groq API Key:", type="password")
        anthropic_key = st.text_input("Anthropic API Key:", type="password")
        
        if groq_key:
            os.environ['GROQ_API_KEY'] = groq_key
            chat_manager.set_api_key(groq_key)
        
        if anthropic_key:
            os.environ['ANTHROPIC_API_KEY'] = anthropic_key
            
        st.markdown("---")
        app_mode = st.radio("Choose a mode:", ["Chat", "Story Mode", "Personality Quiz", "Knowledge Base"])

    if app_mode == "Chat":
        # Main chat interface
        st.title("💝 LoveBot")
        st.markdown("Your AI-powered relationship assistant")

        # Display quiz insights if available
        if "quiz_insights" in st.session_state:
            with st.expander("Your Personality Profile"):
                insights = st.session_state.quiz_insights
                st.markdown(f"**Love Language:** {insights['love_language']}")
                st.markdown(f"**Conflict Style:** {insights['conflict_style']}")
                st.markdown(f"**Social Style:** {insights['social_style']}")

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # Content filtering
            if content_filter.is_safe(prompt):
                # Show assistant response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("🤔 Thinking...")

                    try:
                        # Get relevant context from knowledge base
                        context = kb_manager.get_relevant_context(prompt)

                        # Add context to the chat
                        response = chat_manager.get_response(prompt, st.session_state.messages, context)
                        message_placeholder.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        message_placeholder.markdown(f"❌ Error: {str(e)}")
            else:
                with st.chat_message("assistant"):
                    st.error("I cannot process that type of content. Please keep our conversation appropriate.")
    elif app_mode == "Story Mode":
        display_story_mode()
    elif app_mode == "Personality Quiz":
        display_quiz()
    else:
        display_knowledge_base()

if __name__ == "__main__":
    main()
