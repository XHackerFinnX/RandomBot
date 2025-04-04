document.addEventListener("DOMContentLoaded", function () {
    const tg = window.Telegram?.WebApp;

    if (tg) {
        tg.BackButton.show();
        tg.BackButton.onClick(function () {
            window.location.href = "/allgive";
        });
    }
    const winnersListElement = document.getElementById("winners-list");
    const hashid = new URLSearchParams(window.location.search).get("raffle_id");
    const data = { hashid };
    const url = "/api/list_winner";

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
        .then((response) => response.json())
        .then((winners) => {
            winners.forEach((winner) => {
                const winnerElement = document.createElement("div");
                winnerElement.className = "winner-item";

                const winnerText = document.createElement("p");
                winnerText.textContent = `${winner.id}. ${winner.name}`;

                winnerElement.appendChild(winnerText);
                winnersListElement.appendChild(winnerElement);
            });
        })
        .catch((error) => {
            console.error("Ошибка при запросе к серверу:", error);
        });

    const closeButton = document.getElementById("close-button");
    closeButton.addEventListener("click", function () {
        tg.close();
    });

    function showToast(title, description) {
        const toastContainer = document.getElementById("toast-container");

        const toast = document.createElement("div");
        toast.className = "toast";

        const toastTitle = document.createElement("div");
        toastTitle.className = "toast-title";
        toastTitle.textContent = title;

        const toastDescription = document.createElement("div");
        toastDescription.className = "toast-description";
        toastDescription.textContent = description;

        toast.appendChild(toastTitle);
        toast.appendChild(toastDescription);
        toastContainer.appendChild(toast);

        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                toast.classList.add("visible");
            });
        });

        setTimeout(() => {
            toast.classList.remove("visible");

            setTimeout(() => {
                if (toast.parentNode === toastContainer) {
                    toastContainer.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
});
