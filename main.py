import datetime
import schedule
import time
import threading
import openai
import os

tasks = []

def add_task(description, due_date):
    due_datetime = datetime.datetime.strptime(due_date, "%Y-%m-%d")
    due_datetime = due_datetime.replace(hour=23, minute=59, second=59)
    task = {
        "description": description,
        "due_date": due_datetime
    }
    tasks.append(task)
    print("Task added successfully.")

def view_tasks():
    if not tasks:
        print("No tasks available.")
        return

    print("Your tasks:")
    for idx, task in enumerate(tasks, 1):
        due_date_str = task['due_date'].strftime("%Y-%m-%d")
        print(f"{idx}. {task['description']} (Due: {due_date_str})")

def remove_task(index):
    if 0 <= index < len(tasks):
        removed_task = tasks.pop(index)
        print(f"Removed task: {removed_task['description']}")
    else:
        print("Invalid task number.")

def check_reminders():
    now = datetime.datetime.now()
    for task in tasks:
        days_left = (task['due_date'].date() - now.date()).days

        if days_left < 0:
            print(f"\n⚠️ OVERDUE: '{task['description']}' was due on {task['due_date'].strftime('%Y-%m-%d')}!")
        elif days_left == 0:
            print(f"\n🔔 REMINDER: '{task['description']}' is due TODAY!")
        elif days_left == 1:
            print(f"\n🔔 Reminder: '{task['description']}' is due TOMORROW ({task['due_date'].strftime('%Y-%m-%d')})!")

def run_scheduler():
    schedule.every(1).minutes.do(check_reminders)
    while True:
        schedule.run_pending()
        time.sleep(1)

def remove_task(index):
    if 0 <= index < len(tasks):
        removed_task = tasks.pop(index)
        print(f"Removed task: {removed_task['description']}")
    else:
        print("Invalid task number.")

def remove_task_by_name(task_name):
    global tasks
    tasks = [task for task in tasks if task['description'].lower() != task_name.lower()]
    print(f"Removed task: {task_name}")

# Load API key from environment variables (safer than hardcoding)
openai.api_key = os.getenv("OPENAI_API_KEY")  

def process_natural_input(user_input):
    """Uses OpenAI's GPT to interpret user input into structured commands."""
    prompt = f"""
    You are an AI assistant that helps manage tasks.
    Convert the user's input into a structured action:
    - "Remind me to submit my project on March 28th" → "add_task: submit my project, 2025-03-28"
    - "Show me all my tasks" → "view_tasks"
    - "Delete the meeting task" → "remove_task: meeting"
    
    User Input: {user_input}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can use "gpt-4" if available
        messages=[{"role": "system", "content": prompt}]
    )

    structured_output = response["choices"][0]["message"]["content"].strip()
    return structured_output


def main():
    # Start the reminder thread before user interaction
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    while True:
        print("\nPersonal Productivity Assistant")
        print("Type a command (e.g., 'Remind me to submit my project on March 28')")
        print("Or use menu: 1. Add Task | 2. View Tasks | 3. Remove Task | 4. Exit")
        
        user_input = input("Enter command or choice: ").strip()

        if user_input in ['1', '2', '3', '4']:
            if user_input == '1':
                description = input("Enter task description: ")
                due_date = input("Enter due date (YYYY-MM-DD): ")
                add_task(description, due_date)
            elif user_input == '2':
                view_tasks()
            elif user_input == '3':
                view_tasks()
                index = int(input("Enter task number to remove: ")) - 1
                remove_task(index)
            elif user_input == '4':
                print("Exiting Assistant. Stay productive!")
                break
        else:
            # Process natural language input
            structured_command = process_natural_input(user_input)
            print(f"AI Interpretation: {structured_command}")

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
                print("❌ I didn't understand that command. Try again.")

if __name__ == "__main__":
    main()