const {
    income,
    expense,
    categoryLabels,
    categoryTotals
} = window.dashboardCharts;


const ctx = document.getElementById("incomeExpenseChart");
if (ctx) {
    new Chart(ctx, {

        type: "bar",

        data: {

            labels: ["Income", "Expense"],

            datasets: [{

                data: [income, expense],

            backgroundColor: [
                    "#22c55e",
                    "#ef4444"
                ],

                borderRadius: 14,

                barPercentage: 0.5,

                categoryPercentage: 0.6,
                hoverBackgroundColor: [
                    "#16a34a",
                    "#dc2626"
                ]

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            animation: {

                duration: 1200,

                easing: "easeOutQuart"

            },

            plugins: {


                legend: {

                    display: false

                },

                tooltip: {

                    callbacks: {

                        label: function(context) {

                            return "NPR " + context.raw.toLocaleString();

                        }

                    }

                }

            },

            scales: {

                x: {

                    grid: {

                        display: false

                    }

                },

                y: {

                    beginAtZero: true,

                    title: {

                        display: true,

                        text: "NPR",

                        font: {

                            size: 14,

                            weight: "bold"

                        }

                    },

                    ticks: {

                        callback: function(value) {

                            return value.toLocaleString();

                        }

                    }

                }

            }

        }

    });
}


const totalExpense = categoryTotals.reduce((sum, value) => sum + value, 0);


const pieCtx = document.getElementById("expenseCategoryChart");

const categoryColors = {
    "Food": "#f97316",
    "Transportation": "#3b82f6",
    "Education": "#8b5cf6",
    "Shopping": "#ec4899",
    "Entertainment": "#facc15",
    "Medical": "#ef4444",
    "Rent": "#6b7280",
    "Salary": "#22c55e",
    "Allowance": "#14b8a6",
    "Other": "#94a3b8"
};

const pieColors = categoryLabels.map(category =>
    categoryColors[category] || "#94a3b8"
);

if (pieCtx) {
    new Chart(pieCtx, {

        type: "pie",

        data: {

            labels: categoryLabels,

            datasets: [{

                data: categoryTotals,

                borderWidth: 2,
                backgroundColor: pieColors,

                borderColor: "#ffffff"

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    position: "bottom"

                },

            tooltip: {

                    callbacks: {

                        label: function(context) {

                            const value = context.raw;

                            const percentage = totalExpense
                                ? ((value / totalExpense) * 100).toFixed(1)
                                : 0;

                            return `${context.label}: ${percentage}% (NPR ${value.toLocaleString()})`;

                        }

                    }

                }
            }

        }

    });
}