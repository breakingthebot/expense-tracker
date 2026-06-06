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
python -m src.expense_tracker.main
```

The guided menu asks questions for adding, listing, editing, deleting, reporting, and exporting expenses. You can also open it explicitly:

```powershell
python -m src.expense_tracker.main interactive
```

Add an expense directly:

```powershell
python -m src.expense_tracker.main add --amount 12.50 --category Food --description "Lunch" --date 2026-06-01
```

View the current month summary:

```powershell
python -m src.expense_tracker.main summary
```

List saved expenses:

```powershell
python -m src.expense_tracker.main list
```

List expenses for a specific month:

```powershell
python -m src.expense_tracker.main list --month 2026-06
```

Delete an expense by ID:

```powershell
python -m src.expense_tracker.main delete --id expense-id-from-list
```

Edit an expense by ID:

```powershell
python -m src.expense_tracker.main edit --id expense-id-from-list --amount 14.25 --category Food --description "Client lunch" --date 2026-06-02
```

Export expenses to CSV:

```powershell
python -m src.expense_tracker.main export --output exports/expenses.csv
```

Export a specific month to CSV:

```powershell
python -m src.expense_tracker.main export --output exports/june-2026.csv --month 2026-06
```

View a specific month:

```powershell
python -m src.expense_tracker.main summary --month 2026-06
```

View monthly spending insights:

```powershell
python -m src.expense_tracker.main report --month 2026-06
```

Set a monthly category budget:

```powershell
python -m src.expense_tracker.main budget set --month 2026-06 --category Food --amount 300.00
```

List monthly budgets:

```powershell
python -m src.expense_tracker.main budget list --month 2026-06
```

Create a recurring expense template:

```powershell
python -m src.expense_tracker.main recurring add --amount 1200.00 --category Housing --description "Rent" --day 1
```

Apply recurring templates to a month:

```powershell
python -m src.expense_tracker.main recurring apply --month 2026-06
```

Recurring template application skips matching expenses that already exist for the selected month.

The root launcher also starts the app:

```powershell
python expense_tracker.py
```

Run tests:

```powershell
python -m unittest discover
```

## Screenshots

Guided menu:

```text
Expense Tracker CLI
Answer the prompts to manage expenses without memorizing commands.

1. Add expense
2. List expenses
3. Edit expense
4. Delete expense
5. View monthly summary
6. View monthly report
7. Export CSV
8. Set budget
9. List budgets
10. Add recurring template
11. List recurring templates
12. Apply recurring templates
13. Exit
```

Monthly report with budget comparison:

```text
Report for 2026-06
Total spent: $1275.00
Transactions: 2
Average expense: $637.50
Top category: Housing
Category breakdown:
- Food: $75.00
- Housing: $1200.00
Budget comparison:
- Food: budget $300.00, spent $75.00, remaining $225.00
- Housing: budget $1200.00, spent $1200.00, remaining $0.00
```

Recurring template workflow:

```text
Recurring templates
template-id | day 1 | Housing | $1200.00 | Rent

Applied 1 recurring template(s) to 2026-06.
Applied 0 recurring template(s) to 2026-06.
```

CSV export:

```text
Exported 2 expense record(s) to exports/june-2026.csv.
```

## Deployed

Not deployed. This is a local CLI portfolio project.

## Architecture Notes

I built this as a clean, maintainable version of the original single-file expense tracker. The launcher starts the app, the command layer handles terminal commands, the interactive menu handles guided prompts, validators clean user input, the model defines one expense, storage reads and writes JSON, and the summary service calculates monthly totals. That separation makes each piece easier to understand, test, and improve without turning the app into one large script.

The app supports both a questionnaire-style menu and direct command-line commands. That matters for a portfolio piece because it shows the program can support guided user workflows and predictable automation. Expenses are saved as JSON so the data format stays easy to inspect, and the code uses `Decimal` for money instead of floats to avoid rounding surprises.

## Notes

- The JSON data file is ignored by Git because personal spending data should not be committed.
- The budget data file is ignored by Git because personal financial targets should not be committed.
- The recurring template data file is ignored by Git because personal bill patterns should not be committed.
- Categories are centralized in `src/expense_tracker/utils/validators.py`.
- Storage writes through a temporary file before replacing the JSON file, reducing the chance of corrupting saved data.
- The next strong portfolio improvement would be a lightweight changelog.
