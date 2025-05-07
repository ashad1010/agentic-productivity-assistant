import datetime
import schedule
import time
import threading
import openai
import os
import json
from colorama import init, Fore, Style

init(autoreset=True)

# Set up OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

TASK_FILE = "tasks.json"
tasks = []

# ========== Persistence ==========
def save_tasks():
    with open(TASK_FILE, "w") as f:
        json.dump([{ "description": t["description"], "due_date": t["due_date"].isoformat() } for t in tasks], f)

def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r") as f:
            data = json.load(f)
            for item in data:
                tasks.append({
                    "description": item["description"],
                    "due_date": datetime.datetime.fromisoformat(item["due_date"])
                })

# ========== Task Functions ==========
def add_task(description, due_date):
    try:
        due_datetime = datetime.datetime.strptime(due_date, "%Y-%m-%d")
        due_datetime = due_datetime.replace(hour=23, minute=59, second=59)
        task = { "description": description, "due_date": due_datetime }
        tasks.append(task)
        save_tasks()
        print(Fore.GREEN + "Task added successfully.")
    except ValueError:
        print(Fore.RED + "Invalid date format. Use YYYY-MM-DD.")

def view_tasks():
    if not tasks:
        print(Fore.YELLOW + "No tasks available.")
        return
    print(Fore.CYAN + "Your tasks:")
    for idx, task in enumerate(tasks, 1):
        print(Fore.CYAN + f"{idx}. {task['description']} (Due: {task['due_date'].strftime('%Y-%m-%d')})")

def remove_task(index):
    try:
        if 0 <= index < len(tasks):
            removed_task = tasks.pop(index)
            save_tasks()
            print(Fore.GREEN + f"Removed task: {removed_task['description']}")
        else:
            print(Fore.RED + "Invalid task number.")
    except ValueError:
        print(Fore.RED + "Invalid input.")

def remove_task_by_name(name):
    global tasks
    tasks = [t for t in tasks if t['description'].lower() != name.lower()]
    save_tasks()
    print(Fore.GREEN + f"Removed task: {name}")

# ========== Reminders ==========
def check_reminders():
    now = datetime.datetime.now()
    for task in tasks:
        days_left = (task['due_date'].date() - now.date()).days
        if days_left < 0:
            print(Fore.RED + f"\n⚠️ OVERDUE: '{task['description']}' was due on {task['due_date'].strftime('%Y-%m-%d')}!")
        elif days_left == 0:
            print(Fore.YELLOW + f"\n🔔 REMINDER: '{task['description']}' is due TODAY!")
        elif days_left == 1:
            print(Fore.YELLOW + f"\n🔔 Reminder: '{task['description']}' is due TOMORROW ({task['due_date'].strftime('%Y-%m-%d')})!")

def run_scheduler():
    schedule.every(1).minutes.do(check_reminders)
    while True:
        schedule.run_pending()
        time.sleep(1)

# ========== LLM Processing ==========
def process_natural_input(user_input):
    prompt = f"""
    You are an AI assistant that helps manage tasks.
    Convert the user's input into a structured action:
    - "Remind me to submit my project on March 28th" → "add_task: submit my project, 2025-03-28"
    - "Show me all my tasks" → "view_tasks"
    - "Delete the meeting task" → "remove_task: meeting"

    User Input: {user_input}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-2024-08-06",
        messages=[{"role": "system", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

def motivational_quote():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": "Give me one short motivational quote"}]
        )
        return response["choices"][0]["message"]["content"].strip()
    except:
        return "You're doing better than you think."

# ========== Main Loop ==========
def main():
    load_tasks()
    print(Fore.MAGENTA + Style.BRIGHT + "\nWelcome back, Ashad. Here's your productivity assistant.")
    quote = motivational_quote()
    print(Fore.BLUE + f"\n🌟 Quote of the Day: {quote}\n")
    check_reminders()

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    while True:
        print(Style.BRIGHT + "\nType a command (e.g., 'Remind me to submit my project on March 28')")
        print("Or use menu: 1. Add Task | 2. View Tasks | 3. Remove Task | 4. Exit")
        user_input = input("\nYour input: ").strip()

        if user_input in ['1', '2', '3', '4']:
            if user_input == '1':
                description = input("Task description: ").strip()
                due_date = input("Due date (YYYY-MM-DD): ").strip()
                add_task(description, due_date)
            elif user_input == '2':
                view_tasks()
            elif user_input == '3':
                view_tasks()
                try:
                    index = int(input("Enter task number to remove: ")) - 1
                    remove_task(index)
                except:
                    print(Fore.RED + "Invalid number.")
            elif user_input == '4':
                print(Fore.CYAN + "Goodbye. Stay productive!")
                break
        else:
            try:
                structured_command = process_natural_input(user_input)
                print(Fore.MAGENTA + f"\nAI Parsed: {structured_command}")

                if "add_task:" in structured_command:
                    _, task_details = structured_command.split(":")
                    task_name, due_date = task_details.split(", ")
                    add_task(task_name.strip(), due_date.strip())
                elif structured_command == "view_tasks":
                    view_tasks()
                elif "remove_task:" in structured_command:
                    _, task_name = structured_command.split(":")
                    remove_task_by_name(task_name.strip())
                else:
                    print(Fore.RED + "Could not interpret your input.")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")

if __name__ == "__main__":
    main()