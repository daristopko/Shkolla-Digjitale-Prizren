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
      <td data-label="Date">${t.date}</td>
      <td data-label="Description">${t.description}</td>
      <td data-label="Category">${t.category}</td>
      <td data-label="Amount" class="text-${t.type === "income" ? "success" : "danger"}">
        ${t.type === "income" ? "+" : "-"}€${t.amount.toFixed(2)}
      </td>
      <td data-label="Action">
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
  renderCategoryChart();
  renderMonthlyChart();
  checkBudget();
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

let categoryChartInstance = null;
let monthlyChartInstance = null;

function renderCategoryChart() {
  const canvas = document.getElementById("category-chart");
  if (!canvas) return;

  const transactions = getTransactions().filter(t => t.type === "expense");
  const totals = {};

  transactions.forEach(t => {
    totals[t.category] = (totals[t.category] || 0) + t.amount;
  });

  const labels = Object.keys(totals);
  const data = Object.values(totals);

  if (categoryChartInstance) categoryChartInstance.destroy();

  categoryChartInstance = new Chart(canvas, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: ["#dc3545", "#0d6efd", "#ffc107", "#198754", "#6f42c1", "#6c757d"]
      }]
    }
  });
}

function renderMonthlyChart() {
  const canvas = document.getElementById("monthly-chart");
  if (!canvas) return;

  const transactions = getTransactions().filter(t => t.type === "expense");
  const now = new Date();
  const months = [];

  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    months.push({ label: d.toLocaleString("default", { month: "short", year: "2-digit" }), key: `${d.getFullYear()}-${d.getMonth()}`, total: 0 });
  }

  transactions.forEach(t => {
    const d = new Date(t.date);
    const key = `${d.getFullYear()}-${d.getMonth()}`;
    const month = months.find(m => m.key === key);
    if (month) month.total += t.amount;
  });

  if (monthlyChartInstance) monthlyChartInstance.destroy();

  monthlyChartInstance = new Chart(canvas, {
    type: "bar",
    data: {
      labels: months.map(m => m.label),
      datasets: [{
        label: "Expenses (€)",
        data: months.map(m => m.total),
        backgroundColor: "#dc3545"
      }]
    }
  });
}

function checkBudget() {
  const budget = getBudget();
  const budgetInput = document.getElementById("budget-input");
  const warning = document.getElementById("budget-warning");

  if (budgetInput) budgetInput.value = budget || "";
  if (!warning) return;

  if (budget <= 0) {
    warning.style.display = "none";
    return;
  }

  const now = new Date();
  const currentMonthExpenses = getTransactions()
    .filter(t => t.type === "expense")
    .filter(t => {
      const d = new Date(t.date);
      return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
    })
    .reduce((sum, t) => sum + t.amount, 0);

  if (currentMonthExpenses > budget) {
    warning.textContent = `Warning: this month's expenses (€${currentMonthExpenses.toFixed(2)}) exceed your budget (€${budget.toFixed(2)}).`;
    warning.style.display = "block";
  } else {
    warning.style.display = "none";
  }
}