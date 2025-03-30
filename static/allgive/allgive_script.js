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

  // Функция для форматирования даты
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

  // Функция для расчета оставшегося времени
  function calculateRemainingTime(endDate) {
    const end = new Date(endDate);
    const now = new Date();
    const diff = end - now;

    if (diff <= 0) return "0д 00:00:00";

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    return `${days}д ${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  }

  // Функция для получения класса статуса
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

  // Функция для отправки POST запроса
  async function fetchRaffleData(status) {
    const user_id = tg?.initDataUnsafe?.user?.id;
    console.log(user_id, status);
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
        updateTabContent(status, data); // Функция для обновления содержимого вкладки
      } else {
        console.error("Ошибка при получении данных");
      }
    } catch (error) {
      console.error("Ошибка при отправке запроса:", error);
    }
  }

  // Функция для обновления содержимого вкладки
  function updateTabContent(status, data) {
    const tabContent = document.querySelector(
      `.tab-content[data-status="${status}"]`
    );

    // Очистить текущий контент
    tabContent.innerHTML = "";

    // Проверка, если данных нет
    if (data.length === 0) {
      const noGiveawaysMessage = document.createElement("p");
      noGiveawaysMessage.classList.add("no-giveaways");
      noGiveawaysMessage.textContent = `У вас нет созданных розыгрышей в статусе "${status}"`;
      tabContent.appendChild(noGiveawaysMessage);

      // Добавляем кнопку "Создать розыгрыш" в конце
      const createButton = document.createElement("a");
      createButton.classList.add("button");
      createButton.href = "/newgive";
      createButton.textContent = "Создать розыгрыш";
      tabContent.appendChild(createButton);
    } else {
      // Выводим каждый розыгрыш в новом дизайне
      data.forEach((raffle) => {
        const formattedStartDate = formatDate(raffle.start_date);
        const formattedEndDate = formatDate(raffle.end_date);
        const remainingTime = calculateRemainingTime(raffle.end_date);
        const statusClass = getStatusClass(raffle.status);

        const raffleItem = document.createElement("div");
        raffleItem.classList.add("raffle-item");

        raffleItem.innerHTML = `
            <div class="raffle-header">
              <div class="raffle-status ${statusClass}">
                <span class="status-dot"></span>
                ${raffle.status}
              </div>
              <div class="raffle-time">Осталось: ${remainingTime}</div>
            </div>
            
            <div class="raffle-title">
              <h3 class="raffle-name">${raffle.name}</h3>
            </div>
            
            <div class="raffle-dates">
              ${formattedStartDate} - ${formattedEndDate}
            </div>
            
            <button class="raffle-manage">Управлять</button>
          `;

        // Добавляем обработчик для кнопки "Управлять"
        const manageButton = raffleItem.querySelector(".raffle-manage");
        manageButton.addEventListener("click", function () {
          // Здесь можно добавить переход на страницу управления розыгрышем
          window.location.href = `/manage-raffle/${raffle.id}`;
        });

        tabContent.appendChild(raffleItem);
      });
    }
  }

  // Обновление оставшегося времени каждую секунду
  function updateRemainingTimes() {
    const timeElements = document.querySelectorAll(".raffle-time");
    timeElements.forEach((element) => {
      const raffleItem = element.closest(".raffle-item");
      const datesElement = raffleItem.querySelector(".raffle-dates");
      if (datesElement) {
        const dateText = datesElement.textContent;
        const endDateMatch = dateText.match(/- (.+)$/);
        if (endDateMatch && endDateMatch[1]) {
          const endDate = new Date(endDateMatch[1]);
          element.textContent = `Осталось: ${calculateRemainingTime(endDate)}`;
        }
      }
    });
  }

  // Запускаем обновление времени каждую секунду
  setInterval(updateRemainingTimes, 1000);

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

      // Запрашиваем данные для нужного статуса
      fetchRaffleData(status);
    });
  });

  // По умолчанию загружаем данные для вкладки "Активен"
  fetchRaffleData("active");
});