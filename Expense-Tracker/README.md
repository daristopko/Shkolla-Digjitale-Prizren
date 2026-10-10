# Expense Tracker

A personal finance web app for tracking income and expenses. Built with vanilla HTML, CSS, and JavaScript as part of Shkolla Digjitale Prizren.

## Features

- Add, edit, and delete transactions (income or expense)
- Predefined categories: Food, Transport, Bills, Health, Entertainment, Other
- Dashboard with balance, total income, and total expenses
- Search by description, filter by category and by type
- Charts (Chart.js): expenses by category (pie) and monthly expenses for the last 6 months (bar)
- Monthly budget saved in localStorage, with a red warning when monthly expenses exceed it
- "Analizë kursimi" button: calculates the 3-month average and suggests where to save
- Responsive layout for mobile
- All data persists in localStorage

## Tech Stack

- HTML, CSS, JavaScript (vanilla)
- Bootstrap 5.3.3 (CDN)
- Chart.js 4.4.4 (CDN)

## Project Structure

Expense-Tracker/
├── css/
│ ├── main.css
│ └── components.css
├── docs/
│ └── PRD.md
├── js/
│ ├── app.js
│ ├── storage.js
│ ├── transactions.js
│ └── ui.js
├── pages/
│ ├── add-transaction.html
│ └── filter.html
├── index.html
└── README.md


## How to Run

1. Clone or download the repository
2. Open the project folder in VS Code
3. Run `index.html` with the Live Server extension (or open it directly in a browser)

## Data Model

```json
{
  "id": "uuid",
  "description": "Bus ticket",
  "amount": 4.5,
  "type": "expense",
  "category": "Transport",
  "date": "2026-10-04",
  "createdAt": "2026-10-04T14:30:00.000Z"
}
```

## Author

Daris Topko