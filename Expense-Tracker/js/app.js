document.addEventListener("DOMContentLoaded", function () {
  // Dashboard
  if (document.getElementById("balance")) {
    updateSummary();
    renderTransactions();
    renderCategoryChart();
    renderMonthlyChart();
    checkBudget();
    // Filters
    const searchInput = document.getElementById("search-input");
    const filterCategory = document.getElementById("filter-category");
    const filterType = document.getElementById("filter-type");

    if (searchInput) searchInput.addEventListener("input", renderTransactions);
    if (filterCategory) filterCategory.addEventListener("change", renderTransactions);
    if (filterType) filterType.addEventListener("change", renderTransactions);
    const saveEditBtn = document.getElementById("save-edit-btn");
    if (saveEditBtn) {
      saveEditBtn.addEventListener("click", function () {
        const id = document.getElementById("edit-id").value;
        const description = document.getElementById("edit-description").value.trim();
        const amount = parseFloat(document.getElementById("edit-amount").value);
        const type = document.getElementById("edit-type").value;
        const category = document.getElementById("edit-category").value;
        const date = document.getElementById("edit-date").value;

        const errorMsg = document.getElementById("edit-error");

        if (!description || !date || isNaN(amount) || amount <= 0) {
          errorMsg.style.display = "block";
          return;
        }

        errorMsg.style.display = "none";
        editTransaction(id, description, amount, type, category, date);

        bootstrap.Modal.getInstance(document.getElementById("editModal")).hide();
        renderTransactions();
        updateSummary();
        renderCategoryChart();
        renderMonthlyChart();
        checkBudget();
      });
    }

    // Save budget
    const saveBudgetBtn = document.getElementById("save-budget-btn");
    if (saveBudgetBtn) {
      saveBudgetBtn.addEventListener("click", function () {
        const amount = parseFloat(document.getElementById("budget-input").value);
        if (isNaN(amount) || amount < 0) return;
        saveBudget(amount);
        checkBudget();
      });
    }
  }

  // Add Transaction page
  const saveBtn = document.getElementById("save-btn");
  if (saveBtn) {
    saveBtn.addEventListener("click", function () {
      const description = document.getElementById("description").value.trim();
      const amount = parseFloat(document.getElementById("amount").value);
      const type = document.getElementById("type").value;
      const category = document.getElementById("category").value;
      const date = document.getElementById("date").value;

      const errorMsg = document.getElementById("error-msg");

      if (!description || !date || isNaN(amount) || amount <= 0) {
        errorMsg.style.display = "block";
        return;
      }

      errorMsg.style.display = "none";
      addTransaction(description, amount, type, category, date);
      window.location.href = "../index.html";
    });
  }
});