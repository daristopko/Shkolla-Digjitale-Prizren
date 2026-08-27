function getTransactions() {
  return JSON.parse(localStorage.getItem("transactions")) || [];
}

function saveTransactions(transactions) {
  localStorage.setItem("transactions", JSON.stringify(transactions));
}

function getBudget() {
  return parseFloat(localStorage.getItem("budget")) || 0;
}

function saveBudget(amount) {
  localStorage.setItem("budget", amount);
}