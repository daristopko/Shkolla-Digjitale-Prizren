function addTransaction(description, amount, type, category, date) {
  const transactions = getTransactions();

  const transaction = {
    id: crypto.randomUUID(),
    description: description,
    amount: parseFloat(amount),
    type: type,
    category: category,
    date: date,
    createdAt: new Date().toISOString()
  };

  transactions.push(transaction);
  saveTransactions(transactions);
}

function deleteTransaction(id) {
  const transactions = getTransactions().filter(t => t.id !== id);
  saveTransactions(transactions);
}

function getTotals() {
  const transactions = getTransactions();

  const income = transactions
    .filter(t => t.type === "income")
    .reduce((sum, t) => sum + t.amount, 0);

  const expenses = transactions
    .filter(t => t.type === "expense")
    .reduce((sum, t) => sum + t.amount, 0);

  return {
    income: income,
    expenses: expenses,
    balance: income - expenses
  };
}

function editTransaction(id, description, amount, type, category, date) {
  const transactions = getTransactions().map(t => {
    if (t.id === id) {
      return {
        ...t,
        description: description,
        amount: parseFloat(amount),
        type: type,
        category: category,
        date: date
      };
    }
    return t;
  });
  saveTransactions(transactions);
}