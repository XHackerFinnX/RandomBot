document.addEventListener("DOMContentLoaded", fetchData);

document.addEventListener("DOMContentLoaded", function () {
    let tg = window.Telegram?.WebApp;
    const userId = tg?.initDataUnsafe?.user?.id;
    console.log(userId);
    if (userId) {
        tg.BackButton.show();
        tg.BackButton.onClick(function () {
            window.location.href = "/allgive";
        });
    } else {
        window.location.href = "/";
    }
});

async function fetchData() {
    try {
        const raffleId = getRaffleId();
        console.log(raffleId);
        const response = await fetch("/api/get_raffle_data_settings", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ raffle_id: raffleId }),
        });

        if (!response.ok) {
            throw new Error("Ошибка загрузки данных");
        }

        const data = await response.json();
        console.log(data);
        updateUI(data);
    } catch (error) {
        console.error("Ошибка получения данных:", error);
    }
}

function updateUI(data) {
    document.getElementById("giveaway-name").textContent = data.name;
    document.getElementById("selected-post").textContent =
        data.post_text || "Не указан";
    document.getElementById("button-text").textContent =
        data.button_text || "Не указан";
    document.getElementById("start-date-value").textContent =
        data.start_date || "Не указано";
    document.getElementById("end-date-value").textContent =
        data.end_date || "Не указано";
    document.getElementById("winners-count").textContent =
        data.winners_count || "Не указано";
    document.getElementById("participants-count").textContent =
        data.participants_count || "0";

    const statusText = document.getElementById("status-text");
    const statusIndicator = document.querySelector(".status-indicator");
    const actionButton = document.getElementById("end-early-button");

    statusText.textContent = data.status;

    if (data.status === "Ожидание") {
        statusIndicator.style.backgroundColor = "orange";
        actionButton.textContent = "Запустить сейчас";
        actionButton.style.display = "block";
        actionButton.onclick = () => showModal("start");
    } else if (data.status === "Активен") {
        statusIndicator.style.backgroundColor = "red";
        actionButton.textContent = "Завершить досрочно";
        actionButton.style.display = "block";
        actionButton.onclick = () => showModal("end");
    } else {
        statusIndicator.style.backgroundColor = "gray";
        actionButton.style.display = "none";
    }
    console.log(data.subscription_channels);
    console.log(data.announcement_channels);
    console.log(data.result_channels);
    updateChannels(".channels-list", data.subscription_channels);
    updateChannels(".announcement-list", data.announcement_channels);
    updateChannels(".result-list", data.result_channels);
}

function updateChannels(selector, channels) {
    const container = document.querySelector(selector);
    container.innerHTML = "";

    if (!channels || channels.length === 0) {
        container.innerHTML = "<p>Нет выбранных каналов</p>";
        return;
    }

    channels.forEach((channel) => {
        const channelElement = createChannelElementSub(channel);
        container.appendChild(channelElement);
    });
}

function getRandomColor() {
    const letters = "0123456789ABCDEF";
    let color = "#";
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function generateAvatarLetter(name) {
    const letter = name.charAt(0).toUpperCase();
    const color = getRandomColor();
    return `
  <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="20" r="20" fill="${color}" /> <!-- Делаем круглый фон -->
    <text x="50%" y="45%" font-size="20" text-anchor="middle" dominant-baseline="central" fill="white">${letter}</text>
  </svg>
`;
}

function createChannelElementSub(channel) {
    const channelElement = document.createElement("div");
    channelElement.className = "channel-item";

    channelElement.innerHTML = `
    <div class="channel-content">
      <div class="channel-avatar">
        ${
            channel.photo_url
                ? `<img src="${channel.photo_url}" alt="${channel.name}" class="channel-avatar-img">`
                : generateAvatarLetter(channel.name)
        }
      </div>
      <div class="channel-info">
        <div class="channel-name-container">
          <h3 class="channel-name">${channel.name}</h3>
        </div>
        <p class="channel-subscribers">Подписчиков: ${
            channel.subscribers || 0
        }</p>
      </div>
    </div>
  `;

    return channelElement;
}

function getRaffleId() {
    return document
        .querySelector(".header p")
        .textContent.split(" ")[1]
        .slice(1);
}

function showModal(actionType) {
    const modal = document.getElementById("confirmation-modal");
    const modalText = document.getElementById("modal-text");

    if (actionType === "start") {
        modalText.textContent = "Вы уверены, что хотите запустить розыгрыш?";
    } else if (actionType === "end") {
        modalText.textContent = "Вы уверены, что хотите завершить розыгрыш?";
    } else if (actionType === "cancel") {
        modalText.textContent = "Вы уверены, что хотите отменить розыгрыш?";
    }

    modal.setAttribute("data-action", actionType);
    modal.style.display = "flex";
}

function hideModal() {
    document.getElementById("confirmation-modal").style.display = "none";
}

async function confirmAction() {
    const modal = document.getElementById("confirmation-modal");
    const actionType = modal.getAttribute("data-action");

    try {
        const raffleId = getRaffleId();
        const response = await fetch("/api/perform_raffle_action", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                raffle_id: raffleId,
                action: actionType,
            }),
        });

        if (!response.ok) {
            throw new Error("Ошибка выполнения действия");
        }

        const data = await response.json();
        console.log("Ответ:", data);

        window.location.href = "/allgive";
    } catch (error) {
        console.error("Ошибка запроса:", error);
    }

    hideModal();
}

document
    .getElementById("end-cancel-button")
    .addEventListener("click", () => showModal("cancel"));
document
    .getElementById("modal-confirm")
    .addEventListener("click", confirmAction);
document.getElementById("modal-cancel").addEventListener("click", hideModal);
