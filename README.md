# AI-Powered CLI Task Manager

This is a command-line productivity assistant that supports both menu-driven interaction and natural language input. It allows users to add, view, and remove tasks using structured commands or free-form phrases. The assistant leverages GPT-4 to interpret user input and provide motivational quotes, while running periodic reminders in the background.

## Features

- Add tasks using structured input or natural language
- Parse dates and track due dates automatically
- Save and load tasks locally from `tasks.json`
- Background reminder checks for due/overdue tasks
- Color-coded output using `colorama`
- Periodic motivational quotes via GPT-4
- GPT-4-powered input parsing using OpenAI’s API

## Technologies Used

- Python 3.x
- `openai` for GPT-4 API
- `schedule` for timed checks
- `colorama` for terminal output styling
- `json` and `datetime` for persistence and logic
- Multithreading for background reminder checks

## How to Run

1. Install dependencies:
   ```bash
   pip install openai schedule colorama
   ```

2. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

   On Windows (PowerShell):
   ```powershell
   $env:OPENAI_API_KEY="your_api_key_here"
   ```

3. Run the program:
   ```bash
   python main.py
   ```

4. Choose from:
   - Structured input (e.g., option 1 → Add task)
   - Natural language (e.g., "Remind me to file taxes on April 30")

## Example Commands

- `Remind me to finish my report on 2025-04-10`
- `Show me all my tasks`
- `Delete the gym task`

## Notes

- Tasks are saved locally to `tasks.json` in the project directory.
- The GPT model used is `gpt-4o-2024-08-06`.
- For non-AI fallback or offline use, the menu interface still works.

## License

This project is intended for personal productivity and educational use. Not intended for commercial deployment.
