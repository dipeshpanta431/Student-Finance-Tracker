// Automatically close flash messages after 3 seconds
setTimeout(function () {
    let alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        // Do not close the monthly budget alert
        if (alert.id === "budgetAlert") {
            return;
        }

        let bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
    });

}, 3000);