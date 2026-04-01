import os
import sqlite3
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def setup_database():
    conn = sqlite3.connect("prompt_lab.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            strategy TEXT,
            prompt_sent TEXT,
            response TEXT,
            tokens INTEGER,
            cost REAL,
            timestamp TEXT
        )
    """)
    
    conn.commit()
    return conn
def call_ai(prompt, system_prompt=None, temperature=0.7):
    messages = []
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature
    )
    
    answer = response.choices[0].message.content
    tokens = response.usage.total_tokens
    cost = tokens * 0.00000015
    
    return answer, tokens, cost
def zero_shot(task):
    prompt = task
    return prompt

def few_shot(task):
    prompt = f"""Here are some examples of completing tasks well:

Example 1:
Task: "Summarize what a car does"
Response: A car is a vehicle that transports people and goods using an engine. It runs on fuel or electricity and is the most common form of personal transportation.

Example 2:
Task: "Summarize what a phone does"
Response: A phone is a device for communication. Modern smartphones also browse the internet, take photos, and run applications.

Now complete this task with the same quality and format:
Task: "{task}"
Response:"""
    return prompt

def chain_of_thought(task):
    prompt = f"""{task}

Think about this step by step:
1. What is being asked?
2. What are the key parts to address?
3. What is the best way to explain this?

Then give your final answer."""
    return prompt

def role_based(task):
    prompt = task
    system = (
        "You are an expert professor with 20 years of experience. "
        "You explain things clearly with real-world examples. "
        "You are concise but thorough. "
        "Always give one practical example."
    )
    return prompt, system

def save_result(conn, task, strategy, prompt_sent, response, tokens, cost):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO experiments (task, strategy, prompt_sent, response, tokens, cost, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (task, strategy, prompt_sent, response, tokens, cost, datetime.now().isoformat()))
    conn.commit()

def run_experiment(conn, task):
    print(f"\nTask: {task}")
    print("=" * 60)
    print("Running 4 strategies... please wait.\n")
    
    results = []
    
    # Strategy 1: Zero Shot
    prompt = zero_shot(task)
    answer, tokens, cost = call_ai(prompt, temperature=0.7)
    save_result(conn, task, "Zero-Shot", prompt, answer, tokens, cost)
    results.append(("Zero-Shot", answer, tokens, cost))
    print("Zero-Shot done.")
    
    # Strategy 2: Few Shot
    prompt = few_shot(task)
    answer, tokens, cost = call_ai(prompt, temperature=0.7)
    save_result(conn, task, "Few-Shot", prompt, answer, tokens, cost)
    results.append(("Few-Shot", answer, tokens, cost))
    print("Few-Shot done.")
    
    # Strategy 3: Chain of Thought
    prompt = chain_of_thought(task)
    answer, tokens, cost = call_ai(prompt, temperature=0)
    save_result(conn, task, "Chain-of-Thought", prompt, answer, tokens, cost)
    results.append(("Chain-of-Thought", answer, tokens, cost))
    print("Chain-of-Thought done.")
    
    # Strategy 4: Role Based
    prompt, system = role_based(task)
    answer, tokens, cost = call_ai(prompt, system_prompt=system, temperature=0.7)
    save_result(conn, task, "Role-Based", prompt, answer, tokens, cost)
    results.append(("Role-Based", answer, tokens, cost))
    print("Role-Based done.")
    
    return results

def show_comparison(results):
    print("\n" + "=" * 60)
    print("COMPARISON TABLE")
    print("=" * 60)
    
    for strategy, answer, tokens, cost in results:
        print(f"\n--- {strategy} ---")
        print(f"Tokens: {tokens} | Cost: ${cost:.6f}")
        print(f"Response: {answer[:200]}")
        if len(answer) > 200:
            print("... (truncated)")
    
    # Find the cheapest and most expensive
    cheapest = min(results, key=lambda x: x[2])
    expensive = max(results, key=lambda x: x[2])
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Cheapest: {cheapest[0]} ({cheapest[2]} tokens)")
    print(f"Most expensive: {expensive[0]} ({expensive[2]} tokens)")
    
    total_tokens = sum(r[2] for r in results)
    total_cost = sum(r[3] for r in results)
    print(f"Total tokens: {total_tokens}")
    print(f"Total cost: ${total_cost:.6f}")

def main():
    conn = setup_database()
    
    print("=" * 60)
    print("  PROMPT ENGINEERING LAB BOT")
    print("  Mini Agent #1 — Week 1")
    print("=" * 60)
    print("\nGive me any task. I'll run it through 4 different")
    print("prompting strategies and compare the results.")
    
    while True:
        print("\nCommands:")
        print("  Type any task to test all 4 strategies")
        print("  'history' to see past experiments")
        print("  'quit' to exit")
        
        user_input = input("\nYour task: ").strip()
        
        if user_input.lower() == "quit":
            print("Goodbye! All experiments saved.")
            break
        
        if user_input.lower() == "history":
            show_history(conn)
            continue
        
        if not user_input:
            continue
        
        results = run_experiment(conn, user_input)
        show_comparison(results)
    
    conn.close()


def show_history(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT task, strategy, tokens, cost
        FROM experiments
        ORDER BY id
    """)
    
    rows = cursor.fetchall()
    if not rows:
        print("\nNo experiments yet!")
        return
    
    print("\n--- EXPERIMENT HISTORY ---")
    print(f"{'Task':<30} {'Strategy':<18} {'Tokens':<8} {'Cost':<10}")
    print("-" * 66)
    for row in rows:
        task_short = row[0][:28] if len(row[0]) > 28 else row[0]
        print(f"{task_short:<30} {row[1]:<18} {row[2]:<8} ${row[3]:.6f}")


if __name__ == "__main__":
    main()
