document.addEventListener("DOMContentLoaded", function () {

    const editBudgetBtn =
        document.getElementById("editBudgetBtn");

    const editBudgetForm =
        document.getElementById("editBudgetForm");

    if (!editBudgetBtn || !editBudgetForm) {
        return;
    }

    editBudgetBtn.addEventListener("click", function () {

        const isHidden =
            editBudgetForm.style.display === "" ||
            editBudgetForm.style.display === "none";

        if (isHidden) {

            editBudgetForm.style.display = "block";

            editBudgetBtn.innerHTML =
                "❌ Cancel";

        } else {

            editBudgetForm.style.display = "none";

            editBudgetBtn.innerHTML =
                "✏️ Edit Budget";

        }

    });

});