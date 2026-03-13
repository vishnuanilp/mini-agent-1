from dotenv import load_dotenv
import os
from openai import OpenAI
import sqlite3
import datetime
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Business Idea Validator Agent starting...")

# Database setup
conn = sqlite3.connect("idea_validator.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        role      TEXT,
        content   TEXT
    )
""")
conn.commit()

print("Database ready!")

# Agent persona — the personality of your agent
system_prompt = """
You are an expert Business Idea Validator with 15 years of experience 
analyzing startups and business ideas.

Your job is to:
1. Listen to the user's business idea carefully
2. Ask smart follow-up questions to understand it better
3. When you have enough information, provide a structured analysis

Your personality:
- Professional but friendly
- Ask ONE question at a time — never multiple questions
- Be honest and direct — do not flatter bad ideas
- Always end your analysis with one clear action step

When you are ready to analyze, structure your response like this:
ANALYSIS:
- Verdict: Viable / Not Viable
- Market Size: Large / Medium / Small
- Top Risk: (one sentence)
- Top Opportunity: (one sentence)  
- Score: X/10
- Action: (one specific action this week)
"""

print("Agent persona ready!")

# Save message to database
def save_message(role, content):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO conversations (timestamp, role, content)
        VALUES (?, ?, ?)
    """, (timestamp, role, content))
    conn.commit()

# Conversation history — AI memory
messages = [
    {"role": "system", "content": system_prompt}
]

print("Agent ready to chat!")
# Welcome message
print("\n" + "="*50)
print("Welcome to the Business Idea Validator Agent!")
print("Tell me your business idea and I will analyze it.")
print("Type 'quit' to exit.")
print("="*50 + "\n")

# Conversation loop
while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("Goodbye! Good luck with your business idea!")
        break

    # Add user message to history
    messages.append({"role": "user", "content": user_input})
    save_message("user", user_input)

    # Get AI response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply = response.choices[0].message.content

    # Add AI reply to history
    messages.append({"role": "assistant", "content": reply})
    save_message("assistant", reply)

    print(f"\nAgent: {reply}\n")