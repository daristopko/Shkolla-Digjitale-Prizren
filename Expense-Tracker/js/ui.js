function updateSummary() {
  const totals = getTotals();

  document.getElementById("balance").textContent = "€" + totals.balance.toFixed(2);
  document.getElementById("total-income").textContent = "€" + totals.income.toFixed(2);
  document.getElementById("total-expenses").textContent = "€" + totals.expenses.toFixed(2);
}

function renderTransactions() {
  const search = document.getElementById("search-input")?.value.toLowerCase() || "";
  const categoryFilter = document.getElementById("filter-category")?.value || "all";
  const typeFilter = document.getElementById("filter-type")?.value || "all";

  let transactions = getTransactions();

  if (search) {
    transactions = transactions.filter(t => t.description.toLowerCase().includes(search));
  }

  if (categoryFilter !== "all") {
    transactions = transactions.filter(t => t.category === categoryFilter);
  }

  if (typeFilter !== "all") {
    transactions = transactions.filter(t => t.type === typeFilter);
  }

  const tbody = document.getElementById("transaction-list");
  if (!tbody) return;

  tbody.innerHTML = "";

  transactions.forEach(t => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${t.date}</td>
      <td>${t.description}</td>
      <td>${t.category}</td>
      <td class="text-${t.type === "income" ? "success" : "danger"}">
        ${t.type === "income" ? "+" : "-"}€${t.amount.toFixed(2)}
      </td>
      <td>
        <button class="btn btn-warning btn-sm me-1" onclick="handleEdit('${t.id}')">Edit</button>
        <button class="btn btn-danger btn-sm" onclick="handleDelete('${t.id}')">Delete</button>
      </td>
    `;
    tbody.appendChild(row);
  });
}

function handleDelete(id) {
  deleteTransaction(id);
  renderTransactions();
  updateSummary();
}

function handleEdit(id) {
  const transaction = getTransactions().find(t => t.id === id);
  if (!transaction) return;

  document.getElementById("edit-id").value = transaction.id;
  document.getElementById("edit-description").value = transaction.description;
  document.getElementById("edit-amount").value = transaction.amount;
  document.getElementById("edit-type").value = transaction.type;
  document.getElementById("edit-category").value = transaction.category;
  document.getElementById("edit-date").value = transaction.date;

  const modal = new bootstrap.Modal(document.getElementById("editModal"));
  modal.show();
}