function getTransactions() {
  return JSON.parse(localStorage.getItem("transactions")) || [];
}

function saveTransactions(transactions) {
  localStorage.setItem("transactions", JSON.stringify(transactions));
}