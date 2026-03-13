# 🤖 Business Idea Validator Agent

An AI-powered business idea validator that analyzes your startup ideas through intelligent conversation. Built as Mini Agent 1 of the AI Agent Founder's Playbook.

## 🎯 What It Does

- Asks smart follow-up questions one at a time
- Remembers your entire conversation
- Gives structured analysis with honest scoring
- Saves all conversations to SQLite database

## 🛠️ Technologies Used

- Python 3
- OpenAI API (GPT-4o-mini)
- SQLite3
- python-dotenv

## ⚙️ How To Run

1. Clone the repository
   git clone https://github.com/vishnuanilp/mini-agent-1.git

2. Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies
   pip install openai python-dotenv

4. Create .env file and add your API key
   OPENAI_API_KEY=your-key-here

5. Run the agent
   python3 idea_validator.py

## 💬 Example Output

Agent: Tell me your business idea and I will analyze it.
You: AI tool for tier 2 shop owners

Agent: ANALYSIS:
- Verdict: Viable
- Market Size: Medium
- Score: 7/10
- Action: Conduct a survey this week

## 🧠 Lessons Applied

- Lesson 2: Prompt Engineering
- Lesson 3: System Prompts + SQLite
- Lesson 4: JSON Output Formatting
- Lesson 5: Conversation Loop + Memory

## 👨‍💻 Author

Vishnu Anil — AI Agent Founder's Journey
GitHub: https://github.com/vishnuanilp