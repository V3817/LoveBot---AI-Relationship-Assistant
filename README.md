```markdown
# LoveBot - AI Relationship Assistant

💝 AI-powered relationship coach with multi-modal interaction capabilities.

## Features
- **Chat Mode**: Context-aware conversations about relationships
- **Personality Quiz**: Love language & conflict style assessment
- **Story Mode**: AI-generated story continuations
- **Knowledge Base**: Document upload & contextual recall

## Installation
```bash
git clone [repo_url]
cd LoveBot
pip install -r requirements.txt
```

## Configuration
1. Obtain API keys from [Groq](https://console.groq.com/) and [Anthropic](https://console.anthropic.com/)
2. Create `.env` file:
```env
GROQ_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

## Usage
```bash
streamlit run app.py
```
- **Sidebar**: Enter API keys & navigate modes
- **Modes**:
  - 💬 Chat: Real-time relationship advice
  - 📖 Story: Collaborative story writing
  - 💭 Quiz: Personality assessment
  - 📚 Knowledge: Document management

## Project Structure
```
LoveBot/
├── app.py
├── utils/
│   ├── chat.py        # Conversation logic
│   ├── content_filter.py  # Safety checks
│   ├── quiz.py        # Personality assessment
│   ├── knowledge_base.py  # Document management
│   └── story.py       # Narrative generation
├── styles/
│   └── chat.css       # Interface styling
└── requirements.txt   # Dependencies
