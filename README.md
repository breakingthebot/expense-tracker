<!--
README.md
Documents setup, usage, architecture, and learning notes for the expense tracker CLI.
Connects to: src/expense_tracker/main.py, .env.example, requirements.txt
Created: 2026-06-06
-->

# Core Python Expense Tracker CLI

A command-line expense tracker that records categorized expenses, stores them in JSON, and summarizes monthly spending.

## Stack

- Python 3.12
- Standard library only
- Local JSON file storage
- `unittest` for automated tests

## Setup

1. Create the virtual environment:

   ```powershell
   python -m venv venv
   ```

2. Activate it:

   ```powershell
   venv\Scripts\activate
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

   This project currently uses only the Python standard library, so there are no third-party packages to install.

## Environment Variables

See `.env.example`.

- `EXPENSE_TRACKER_DATA_FILE`: Optional path for the JSON data file. If omitted, the app uses `data/expenses.json`.

## Running Locally

Open the guided menu:

```powershell
python -m src.expense_tracker.main interactive
```

Add an expense directly:

```powershell
python -m src.expense_tracker.main add --amount 12.50 --category Food --description "Lunch"
```

View the current month summary:

```powershell
python -m src.expense_tracker.main summary
```

View a specific month:

```powershell
python -m src.expense_tracker.main summary --month 2026-06
```

The root launcher also starts the app:

```powershell
python expense_tracker.py
```

Run tests:

```powershell
python -m unittest discover
```

## Deployed

Not deployed. This is a local CLI portfolio project.

## Architecture Notes

I built this as a clean, maintainable version of the original single-file expense tracker. The launcher starts the app, the command layer handles terminal commands, the interactive menu handles guided prompts, validators clean user input, the model defines one expense, storage reads and writes JSON, and the summary service calculates monthly totals. That separation makes each piece easier to understand, test, and improve without turning the app into one large script.

The app supports both an interactive menu and direct command-line commands. That matters for a portfolio piece because it shows the program can support guided user workflows and predictable automation. Expenses are saved as JSON so the data format stays easy to inspect, and the code uses `Decimal` for money instead of floats to avoid rounding surprises.

## Notes

- The JSON data file is ignored by Git because personal spending data should not be committed.
- Categories are centralized in `src/expense_tracker/utils/validators.py`.
- Storage writes through a temporary file before replacing the JSON file, reducing the chance of corrupting saved data.
- The next strong portfolio improvements would be edit/delete commands, date selection, CSV export, and richer reporting.
