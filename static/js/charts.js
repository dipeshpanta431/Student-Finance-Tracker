const {
    income,
    expense,
    categoryLabels,
    categoryTotals,
    monthLabels,
    monthlyIncome,
    monthlyExpense,
    incomeCategoryLabels,
    incomeCategoryTotals
} = window.dashboardCharts;
const currentMonthName = window.dashboardCharts.currentMonthName;
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
    "Other": "#352f38"
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
const trendCtx = document.getElementById("dailyTrendChart");

if (trendCtx && dailyLabels.length > 0) {

    new Chart(trendCtx, {

        type: "line",

        data: {

            labels: dailyLabels,

            datasets: [

                {
                    label: "Income",

                    data: dailyIncome,

                    borderColor: "#22c55e",

                    backgroundColor: "rgba(34,197,94,0.15)",

                    tension: 0.35,

                    fill: false,

                    pointRadius: 4,

                    pointHoverRadius: 6
                },

                {
                    label: "Expense",

                    data: dailyExpense,

                    borderColor: "#ef4444",

                    backgroundColor: "rgba(239,68,68,0.15)",

                    tension: 0.35,

                    fill: false,

                    pointRadius: 4,

                    pointHoverRadius: 6
                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            interaction: {

                mode: "index",

                intersect: false

            },

            plugins: {

                tooltip: {

                    callbacks: {

                       title: function(context) {
                            return currentMonthName + " " + context[0].label;
                        },

                        label: function(context) {

                            return context.dataset.label +
                                   ": NPR " +
                                   Number(context.raw).toLocaleString();

                        }

                    }

                }

            },

            scales: {

                x: {

                    title: {

                        display: true,

                        text: "Day"

                    }

                },

                y: {

                    beginAtZero: true,

                    title: {

                        display: true,

                        text: "NPR"

                    },

                    ticks: {

                        callback: function(value) {

                            return Number(value).toLocaleString();

                        }

                    }

                }

            }

        }

    });

}

const totalIncome = incomeCategoryTotals.reduce(
    (sum, value) => sum + value,
    0
);

const incomePieCtx =
    document.getElementById("incomeCategoryChart");

const incomePieColors =
    incomeCategoryLabels.map(category =>
        categoryColors[category] || "#94a3b8"
    );

if (incomePieCtx && incomeCategoryTotals.length > 0) {

    new Chart(incomePieCtx, {

        type: "pie",

        data: {

            labels: incomeCategoryLabels,

            datasets: [{

                data: incomeCategoryTotals,

                borderWidth: 2,

                backgroundColor: incomePieColors,

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

                            const percentage = totalIncome
                                ? ((value / totalIncome) * 100).toFixed(1)
                                : 0;

                            return `${context.label}: ${percentage}% (NPR ${value.toLocaleString()})`;

                        }

                    }

                }

            }

        }

    });

}