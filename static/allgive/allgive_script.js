document.addEventListener("DOMContentLoaded", function () {
  let tg = window.Telegram?.WebApp;
  if (tg) {
    tg.BackButton.show();
    tg.BackButton.onClick(function () {
      window.location.href = "/";
    });
  }

  const tabTriggers = document.querySelectorAll(".tab-trigger");
  const tabContents = document.querySelectorAll(".tab-content");

  function formatDate(dateString) {
    const date = new Date(dateString);
    return `${date
      .getDate()
      .toString()
      .padStart(
        2,
        "0"
      )}.${(date.getMonth() + 1).toString().padStart(2, "0")}.${date.getFullYear()}, ${date.getHours().toString().padStart(2, "0")}:${date.getMinutes().toString().padStart(2, "0")}`;
  }

  function calculateRemainingTime(endDate) {
    const end = new Date(endDate);
    const now = new Date();
    const diff = end - now;

    if (diff <= 0) return "";

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    return `${days}д ${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  }

  async function fetchRaffleData(status) {
    const user_id = tg?.initDataUnsafe?.user?.id;
    try {
      const response = await fetch(`/api/raffle-my?status=${status}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: user_id }),
      });

      if (response.ok) {
        const data = await response.json();
        updateTabContent(status, data);
      } else {
        console.error("Ошибка при получении данных");
      }
    } catch (error) {
      console.error("Ошибка при отправке запроса:", error);
    }
  }

  function updateTabContent(status, data) {
    const tabContent = document.querySelector(
      `.tab-content[data-status="${status}"]`
    );

    tabContent.innerHTML = "";

    if (data.length === 0) {
      const noGiveawaysMessage = document.createElement("p");
      noGiveawaysMessage.classList.add("no-giveaways");

      if (status === "active") {
        status = "Активен";
      }
      if (status === "pending") {
        status = "Ожидание";
      } 
      if (status === "completed") {
        status = "Завершен";
      }

      noGiveawaysMessage.textContent = `У вас нет созданных розыгрышей в статусе "${status}"`;
      tabContent.appendChild(noGiveawaysMessage);

      const createButton = document.createElement("a");
      createButton.classList.add("button");
      createButton.href = "/newgive";
      createButton.textContent = "Создать розыгрыш";
      tabContent.appendChild(createButton);
    } else {
      data.forEach((raffle) => {
        const formattedStartDate = formatDate(raffle.start_date);
        const formattedEndDate = formatDate(raffle.end_date);
        const statusClass = getStatusClass(raffle.status);

        const end = new Date(raffle.end_date);
        const now = new Date();
        const diff = end - now;

        let remainingTimeHTML = "";
        if (diff > 0) {
          const remainingTime = calculateRemainingTime(raffle.end_date);
          remainingTimeHTML = `<div class="raffle-time" id="raffle-time-${raffle.raffle_id}">Осталось: ${remainingTime}</div>`;
        }

        let buttonText = "Управлять";
        if (
          raffle.status.toLowerCase() === "завершен" ||
          raffle.status.toLowerCase() === "completed" ||
          raffle.status_user
        ) {
          buttonText = "Подробнее";
        }

        const raffleItem = document.createElement("div");
        raffleItem.classList.add("raffle-item");

        raffleItem.innerHTML = `
          <div class="raffle-header">
            <div class="raffle-status ${statusClass}">
              <span class="status-dot"></span>
              ${raffle.status}
            </div>
            ${remainingTimeHTML} <!-- Вставляем оставшееся время, если оно больше 0 -->
          </div>
          
          <div class="raffle-title">
            <h3 class="raffle-name">${raffle.name}</h3>
          </div>
          
          <div class="raffle-dates">
            ${formattedStartDate} - ${formattedEndDate}
          </div>
          
          <button class="raffle-manage">${buttonText}</button>
        `;

        const manageButton = raffleItem.querySelector(".raffle-manage");
        manageButton.addEventListener("click", function () {
          if (
            raffle.status.toLowerCase() === "завершен" ||
            raffle.status.toLowerCase() === "completed" ||
            raffle.status_user
          ) {
            window.location.href = `/raffle?raffle_id=${raffle.raffle_id}`;
          } else {
            window.location.href = `/manage-raffle?raffle_id=${raffle.raffle_id}`;
          }
        });

        tabContent.appendChild(raffleItem);

        if (diff > 0) {
          startCountdownTimer(raffle.end_date, raffle.raffle_id);
        }
      });
    }
  }

  function startCountdownTimer(endDate, raffleId) {
    const countdownInterval = setInterval(() => {
      const now = new Date();
      const endTime = new Date(endDate).getTime();
      const timeDifference = endTime - now;

      const timeLeftElement = document.getElementById(
        `raffle-time-${raffleId}`
      );

      if (timeDifference <= 0) {
        clearInterval(countdownInterval);
        timeLeftElement.textContent = "";
        return;
      }

      const days = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
      const hours = Math.floor(
        (timeDifference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
      );
      const minutes = Math.floor(
        (timeDifference % (1000 * 60 * 60)) / (1000 * 60)
      );
      const seconds = Math.floor((timeDifference % (1000 * 60)) / 1000);

      timeLeftElement.textContent = formatTimeLeft(
        days,
        hours,
        minutes,
        seconds
      );
    }, 1000);
  }

  function formatTimeLeft(days, hours, minutes, seconds) {
    return `Осталось: ${days}д ${hours < 10 ? "0" + hours : hours}:${minutes < 10 ? "0" + minutes : minutes}:${seconds < 10 ? "0" + seconds : seconds}`;
  }

  function getStatusClass(status) {
    switch (status.toLowerCase()) {
      case "активен":
      case "active":
        return "status-active";
      case "ожидание":
      case "pending":
        return "status-pending";
      case "завершен":
      case "completed":
        return "status-completed";
      default:
        return "status-active";
    }
  }

  fetchRaffleData("active");

  tabTriggers.forEach((trigger) => {
    trigger.addEventListener("click", function () {
      const status = this.getAttribute("data-status");

      tabTriggers.forEach((t) => t.classList.remove("active"));
      tabContents.forEach((c) => c.classList.remove("active"));

      this.classList.add("active");
      const currentTabContent = document.querySelector(
        `.tab-content[data-status="${status}"]`
      );
      currentTabContent.classList.add("active");

      fetchRaffleData(status);
    });
  });
});
