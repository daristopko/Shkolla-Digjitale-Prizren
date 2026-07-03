App Overview {
    This app tracks your expenses, its for anyone wanting to track their expenses that they make, it solves the problem of trying to remember what you bought days or months ago, or to know exactly how much money they spent on particular stuff etc.
}


User Stories {
    "As a student, I want to add my daily expenses, so that I can track where my money is going."
    "As a young worker, I want to view my expense history, so that I can understand my spending habits over time."
    "As a roommate, I want to filter expenses by category, so that I can quickly see how much I spend on food, transport, or bills."
    "As a casual user, I want to see my total expenses, so that I know how much money I have spent overall."
    "As a user, I want to delete an expense entry, so that I can correct mistakes or remove incorrect records."
    "As a user, I want my data to be saved automatically, so that I don't lose my expense records when I close the app."
    "As a freelancer, I want to add expenses with categories, so that I can organize business and personal spending separately."
    "As a budget-conscious user, I want to view expenses by category over time, so that I can identify where I am overspending."
}

Feature List {
    MVP {
        Add expense (amount, description, category, date)
        View expense list (chronological)
        Display total expenses (overall sum)
        Delete expense entry
        Basic form validation (no empty/invalid inputs)
        Persist data locally (e.g. LocalStorage)
        Simple category assignment (e.g. Food, Transport, Bills)
        Filter expenses by category
        Responsive UI (works on mobile + desktop)
    }

    Nice-to-have {
        Edit existing expense entries
        Search expenses by text (description)
        Monthly breakdown view
        Charts / graphs (spending visualization)
        Dark mode
        Multiple currency support
        Export data (CSV/PDF)
        Authentication (login system)
        Cloud sync (multi-device support)
        Budget limits per category (alerts when exceeded)
        Recurring expenses (subscriptions, rent)
        Sorting options (by amount, date, category)
    }
}

Data Model {
    "id": "string — e.g. crypto.randomUUID() → 'a1b2c3d4-e5f6-...'",
    "amount": "number — e.g. 4.50",
    "description": "string — e.g. 'Bus ticket'",
    "category": "string (enum) — one of: 'Food' | 'Transport' | 'Bills' | 'Health' | 'Entertainment' | 'Other'",
    "date": "string (ISO 8601) — e.g. '2025-04-21'",
    "createdAt": "string (ISO 8601 timestamp) — e.g. '2025-04-21T14:30:00Z'"
}

App Pages / Views {
    Dashboard {
        Purpose: Main overview of all spending.

        Features {
            Shows list of all expenses (chronological)
            Displays total amount spent
            Allows deleting expenses
            Shows category labels per entry
            Basic navigation to other actions
        }
    }

    Add Expense {
        Purpose: Create a new expense entry.

        Features {
            Input amount
            Input description
            Select category (Food, Transport, etc.)
            Select date
            Save expense
            Form validation (prevents empty/invalid data)
        }
    }

    Category Filter View {
        Purpose: View spending by category.

        Features {
            Filter expenses by category
            Show only matching expenses
            Display total for selected category
        }
    }
}

System Behaviour {
    Data Persistence {
        Purpose: Keep data saved between sessions.

        Features {
            Save expenses to local storage
            Load saved expenses on app startup
        }
    }
}

Tech Stack {
    Core (Vanilla) {
        HTML - structure of pages (layout, forms, sections)
        CSS - styling (layout, spacing, responsiveness, UI design)
        JavaScript (Vanilla JS) - all logic {
            adding/deleting expenses
            filtering
            calculating totals
            updating UI dynamically
            handling LocalStorage
        }
    }

    External Dependencies {
        Fonts {

        }

        Icons {

        }

        Charts {
            
        }
    }
}