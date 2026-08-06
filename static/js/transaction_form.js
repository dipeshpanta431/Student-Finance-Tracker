const incomeCategories = window.incomeCategories;
const expenseCategories = window.expenseCategories;
const initialCategory = window.initialCategory;

const transactionType = document.getElementById("transaction_type");
const category = document.getElementById("category");

const customCategoryGroup =
    document.getElementById("customCategoryGroup");

const customCategoryInput =
    document.getElementById("custom_category");

// Remember the previous category
let previousCategory = category.value;

// Used only on the first page load
let initialLoad = true;

function updateCategories() {

    // First load: preserve Flask's pre-filled value (used for Edit)
    // Later: preserve the user's current selection
   const selectedCategory = initialLoad
    ? initialCategory
    : category.value;

    const selectedType = transactionType.value;

    category.innerHTML = "";

    const categories =
        selectedType === "Income"
            ? incomeCategories
            : expenseCategories;

    categories.forEach(function(item) {

        const option = document.createElement("option");

        option.value = item;
        option.textContent = item;

        if (item === selectedCategory) {
            option.selected = true;
        }

        category.appendChild(option);

    });

    initialLoad = false;

}

function toggleCustomCategory() {

    if (category.value === "Other") {

        customCategoryGroup.style.display = "block";
        customCategoryInput.required = true;

    } else {

        customCategoryGroup.style.display = "none";
        customCategoryInput.required = false;

        if (previousCategory === "Other") {
            customCategoryInput.value = "";
        }

    }

    previousCategory = category.value;

}

transactionType.addEventListener("change", function () {

    updateCategories();
    toggleCustomCategory();

});

category.addEventListener("change", toggleCustomCategory);

updateCategories();
toggleCustomCategory();

