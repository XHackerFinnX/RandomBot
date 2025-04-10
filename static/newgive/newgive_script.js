let activeDateField = null;
let savedRaffleData = null;
let currentStep = 0;

class SimpleAlert {
    constructor() {
        this.alertElement = document.getElementById("custom-alert");
        this.messageElement = document.getElementById("alert-message");
        this.closeButton = document.getElementById("alert-close");

        if (this.closeButton) {
            this.closeButton.addEventListener("click", () => this.hide());
        }
    }

    show(message, duration = 3000) {
        if (!this.alertElement || !this.messageElement) return;

        this.messageElement.textContent = message;
        this.alertElement.style.display = "block";

        setTimeout(() => {
            this.hide();
        }, duration);
    }

    hide() {
        if (this.alertElement) {
            this.alertElement.style.display = "none";
        }
    }
}

const alertify = new SimpleAlert();

function safeQuerySelector(selector) {
    return document.querySelector(selector) || null;
}

document.addEventListener("DOMContentLoaded", async () => {
    const tg = window.Telegram?.WebApp;
    window.Telegram.WebApp.ready();
    let currentYear, currentMonth; // Сохраняем состояние между открытиями модального окна для даты

    // Обработчики переключения месяцев
    function handlePrevMonth() {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        renderCalendar(currentYear, currentMonth);
    }

    function handleNextMonth() {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        renderCalendar(currentYear, currentMonth);
    }

    // Инициализация календаря
    function initCalendar() {
        const calendarDays = document.getElementById("calendar-days");
        const prevMonthButton = document.getElementById("prev-month");
        const nextMonthButton = document.getElementById("next-month");

        // Инициализация дат только при первом вызове
        if (currentYear === undefined || currentMonth === undefined) {
            const currentDate = new Date();
            currentYear = currentDate.getFullYear();
            currentMonth = currentDate.getMonth();
        }

        // Удаляем старые обработчики и добавляем новые
        prevMonthButton?.removeEventListener("click", handlePrevMonth);
        nextMonthButton?.removeEventListener("click", handleNextMonth);
        prevMonthButton?.addEventListener("click", handlePrevMonth);
        nextMonthButton?.addEventListener("click", handleNextMonth);

        renderCalendar(currentYear, currentMonth);
    }

    function renderCalendar(year, month) {
        const calendarDays = document.getElementById("calendar-days");
        const currentMonthDisplay = document.getElementById("current-month");

        calendarDays.innerHTML = "";
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        let startingDay = firstDay.getDay();
        startingDay = startingDay === 0 ? 6 : startingDay - 1;

        currentMonthDisplay.textContent = new Intl.DateTimeFormat("ru-RU", {
            month: "long",
            year: "numeric",
        }).format(firstDay);

        // Добавление пустых дней для выравнивания
        for (let i = 0; i < startingDay; i++) {
            const emptyDay = document.createElement("div");
            emptyDay.classList.add("calendar-day", "outside-month");
            calendarDays.appendChild(emptyDay);
        }

        // Добавление дней месяца
        for (let i = 1; i <= daysInMonth; i++) {
            const day = document.createElement("div");
            day.classList.add("calendar-day");
            day.textContent = i;

            const currentDate = new Date(year, month, i);
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            if (currentDate < today) {
                day.classList.add("disabled");
            } else {
                day.addEventListener("click", () => {
                    document
                        .querySelectorAll(".calendar-day.selected")
                        .forEach((d) => d.classList.remove("selected"));
                    day.classList.add("selected");
                });
            }
            calendarDays.appendChild(day);
        }
    }

    tg.BackButton.show();
    tg.BackButton.onClick(() => {
        const userId = tg?.initDataUnsafe?.user?.id;
        fetch("/api/delete-save-raffle", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_id: userId,
            }),
        })
            .then((response) => {
                if (response.ok) {
                    console.log("Розыгрыш успешно удален");
                    window.location.href = "/";
                } else {
                    console.error("Ошибка при удалении розыгрыша");
                }
            })
            .catch((error) => {
                console.error("Ошибка при отправке запроса:", error);
            });
    });

    const stepContent = document.getElementById("step-content");
    const backButton = document.getElementById("back-button");
    const nextButton = document.getElementById("next-button");
    const templates = {
        basics: document.getElementById("template-basics")?.content,
        channels: document.getElementById("template-channels")?.content,
        announcement: document.getElementById("template-announcement")?.content,
        results: document.getElementById("template-results")?.content,
        dates: document.getElementById("template-dates")?.content,
        winners: document.getElementById("template-winners")?.content,
        review: document.getElementById("template-review")?.content,
    };
    const steps = Object.keys(templates);

    // Функция для обновления индикатора прогресса
    function updateProgressIndicator() {
        const progressIndicator = safeQuerySelector(".progress-indicator");
        if (!progressIndicator) return;

        progressIndicator.innerHTML = "";
        steps.forEach((step, index) => {
            const dot = document.createElement("div");
            dot.classList.add("progress-dot");
            if (index === currentStep) dot.classList.add("active");
            progressIndicator.appendChild(dot);
        });
    }

    function parseDate(dateString) {
        const parts = dateString.split(/[\s\.:-]+/);
        return new Date(
            parts[2],
            parts[1] - 1,
            parts[0],
            parts[3] || 0,
            parts[4] || 0
        );
    }

    function isCurrentStepValid() {
        const currentStepName = steps[currentStep];
        switch (currentStepName) {
            case "basics":
                return (
                    giveawayData.name.trim() !== "" &&
                    giveawayData.selectedPost !== "Выбрать пост" &&
                    giveawayData.buttonText.trim() !== ""
                );
            case "channels":
                return giveawayData.selectedSubscriptionChannels.length > 0;
            case "announcement":
                return giveawayData.selectedAnnouncementChannels.length > 0;
            case "results":
                return giveawayData.selectedResultChannels.length > 0;
            case "dates":
                let isValidDates = false;
                if (giveawayData.startImmediately) {
                    isValidDates = giveawayData.endDate !== "";
                    giveawayData.startDate = "";
                } else {
                    isValidDates =
                        giveawayData.endDate !== "" &&
                        giveawayData.startDate !== "" &&
                        parseDate(giveawayData.startDate) <
                            parseDate(giveawayData.endDate);
                }
                return isValidDates;
            case "winners":
                return (
                    giveawayData.winnersCount >= 1 &&
                    giveawayData.winnersCount <= 30
                );
            case "review":
                return true;
            default:
                return false;
        }
    }

    function updateNextButtonState() {
        const isValid = isCurrentStepValid();
        document.querySelector(".button-primary").style.opacity = isValid
            ? "1"
            : "0.5";
        if (nextButton) {
            nextButton.disabled = !isValid;
            nextButton.classList.toggle("button-disabled", !isValid);
        }
    }

    // Загрузка шага
    function loadStep(step) {
        stepContent.innerHTML = "";
        stepContent.appendChild(
            document.importNode(templates[steps[step]], true)
        );
        updateNavigationButtons();
        updateProgressIndicator();
        initStepSpecificLogic(step);
        restoreCheckboxStates();
        updateNextButtonState();
    }

    // Обновление кнопок навигации
    function updateNavigationButtons() {
        backButton.style.display = currentStep === 0 ? "none" : "block";
        nextButton.textContent =
            currentStep === steps.length - 1 ? "Создать" : "Вперед";
    }

    // Обработчик кнопки "Назад"
    backButton.addEventListener("click", () => {
        saveCurrentStepData();
        if (currentStep > 0) {
            currentStep--;
            postGiveawayData(currentStep);
            loadStep(currentStep);
        }
    });

    // Обработчик кнопки "Вперед"
    nextButton.addEventListener("click", () => {
        saveCurrentStepData();
        if (currentStep < steps.length - 1) {
            currentStep++;
            postGiveawayData(currentStep);
            loadStep(currentStep);
        } else {
            createRaffle();
        }
    });

    function postGiveawayData(stepCount) {
        const tg = window.Telegram?.WebApp;
        const userId = tg?.initDataUnsafe?.user?.id;

        const dateString = new Date()
            .toLocaleString("ru-RU", {
                timeZone: "Europe/Moscow",
                year: "numeric",
                month: "2-digit",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
            })
            .replace(",", "");

        const raffleData = {
            user_id: userId,
            name: giveawayData.name,
            post_id: giveawayData.postId,
            post_text: giveawayData.selectedPost,
            post_button: giveawayData.buttonText,
            sub_channel_id:
                giveawayData.selectedSubscriptionChannels.map(Number),
            announcet_channel_id:
                giveawayData.selectedAnnouncementChannels.map(Number),
            results_channel_id: giveawayData.selectedResultChannels.map(Number),
            start_date: giveawayData.startImmediately
                ? dateString
                : giveawayData.startDate,
            end_date: giveawayData.endDate,
            user_win: giveawayData.winnersCount,
        };

        fetch("/api/save-giveaway", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                giveawayData: raffleData,
                step: stepCount,
            }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Ошибка при отправке данных");
                }
                return response.json();
            })
            .then((data) => {
                console.log("Данные успешно отправлены:", data);
            })
            .catch((error) => {
                console.error("Ошибка POST-запроса:", error);
            });
    }

    async function createRaffle() {
        const tg = window.Telegram?.WebApp;
        const userId = tg?.initDataUnsafe?.user?.id;

        if (!userId) {
            console.error("Не удалось получить ID пользователя.");
            return;
        }

        const dateString = new Date()
            .toLocaleString("ru-RU", {
                timeZone: "Europe/Moscow",
                year: "numeric",
                month: "2-digit",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
            })
            .replace(",", "");

        const raffleData = {
            user_id: userId,
            name: giveawayData.name,
            post_id: giveawayData.postId,
            post_text: giveawayData.selectedPost,
            post_button: giveawayData.buttonText,
            sub_channel_id:
                giveawayData.selectedSubscriptionChannels.map(Number),
            announcet_channel_id:
                giveawayData.selectedAnnouncementChannels.map(Number),
            results_channel_id: giveawayData.selectedResultChannels.map(Number),
            start_date: giveawayData.startImmediately
                ? dateString
                : giveawayData.startDate,
            end_date: giveawayData.endDate,
            user_win: giveawayData.winnersCount,
        };

        document.getElementById("main-container").style.display = "none";
        document.getElementById("loading-container").style.display = "block";
        try {
            const response = await fetch("/api/create_raffle", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(raffleData),
            });

            if (!response.ok) {
                throw new Error("Ошибка при создании розыгрыша");
            }

            const result = await response.json();
            window.location.href = "/loading";
            console.log("Розыгрыш успешно создан:", result);
        } catch (error) {
            console.error("Ошибка при создании розыгрыша:", error);
            document.getElementById("main-container").style.display = "block";
            document.getElementById("loading-container").style.display = "none";
            alertify.show(
                "Произошла ошибка при создании розыгрыша. Пожалуйста, попробуйте еще раз.",
                2000
            );
        }
    }

    // Сохранение данных текущего шага
    function saveCurrentStepData() {
        const currentStepName = steps[currentStep];
        switch (currentStepName) {
            case "basics":
                const nameInput = document.getElementById("giveaway-name");
                const selectPostBtn = document.getElementById("selectPostBtn");
                const namePost = selectPostBtn.querySelector("span");
                const postid = namePost.id;
                const buttonTextInput = document.getElementById("button-text");

                if (nameInput) giveawayData.name = nameInput.value;
                if (namePost) giveawayData.selectedPost = namePost.textContent;
                if (postid) giveawayData.postId = postid;
                if (buttonTextInput)
                    giveawayData.buttonText = buttonTextInput.value;
                break;

            case "channels":
                giveawayData.selectedSubscriptionChannels = getCheckedChannels(
                    "#subscription-channels-list .channel-checkbox"
                );
                break;
            case "announcement":
                giveawayData.selectedAnnouncementChannels = getCheckedChannels(
                    "#announcement-channels-list .channel-checkbox"
                );
                break;
            case "results":
                giveawayData.selectedResultChannels = getCheckedChannels(
                    "#result-channels-list .channel-checkbox"
                );
                break;

            case "dates":
                const startImmediatelyToggle =
                    document.getElementById("start-immediately");
                const startDateDisplay =
                    document.getElementById("start-date-display");
                const endDateDisplay =
                    document.getElementById("end-date-display");

                if (startImmediatelyToggle)
                    giveawayData.startImmediately =
                        startImmediatelyToggle.checked;
                if (
                    startDateDisplay &&
                    startDateDisplay.textContent !== "выбрать"
                ) {
                    giveawayData.startDate = startDateDisplay.textContent;
                }
                if (
                    endDateDisplay &&
                    endDateDisplay.textContent !== "выбрать"
                ) {
                    giveawayData.endDate = endDateDisplay.textContent;
                }
                break;

            case "winners":
                const winnersCountInput =
                    document.getElementById("winners-count");
                if (winnersCountInput)
                    giveawayData.winnersCount =
                        Number.parseInt(winnersCountInput.value) || 1;
                break;

            case "review":
                // На странице проверки нет новых данных для сохранения
                break;
        }

        updateNextButtonState();
    }

    function getCheckedChannels(selector) {
        const checkboxes = document.querySelectorAll(selector);

        if (!checkboxes || checkboxes.length === 0) {
            return [];
        }

        return Array.from(checkboxes)
            .filter((checkbox) => checkbox.checked)
            .map((checkbox) => checkbox.getAttribute("data-id"));
    }

    // Инициализация логики для конкретного шага
    function initStepSpecificLogic(step) {
        const currentStepName = steps[step];
        // Общая логика для всех шагов
        if (currentStepName === "review") {
            populateReviewPage();
        }

        switch (currentStepName) {
            case "basics":
                initBasicsStep();
                break;

            case "channels":
                initChannelsStep("subscription");
                break;

            case "announcement":
                initChannelsStep("announcement");
                break;

            case "results":
                initChannelsStep("result");
                break;

            case "dates":
                initDatesStep();
                break;

            case "winners":
                initWinnersStep();
                break;

            case "review":
                initReviewStep();
                break;
        }

        const currentStepName2 = steps[step];
        switch (currentStepName2) {
            case "basics":
                const nameInput = document.getElementById("giveaway-name");
                const buttonTextInput = document.getElementById("button-text");
                const selectPostBtn = document.getElementById("selectPostBtn");
                const namePost = selectPostBtn.querySelector("span");
                const postid = namePost ? namePost.id : null;

                if (nameInput)
                    nameInput.addEventListener("input", updateNextButtonState);
                if (buttonTextInput)
                    buttonTextInput.addEventListener(
                        "input",
                        updateNextButtonState
                    );
                if (selectPostBtn)
                    selectPostBtn.addEventListener(
                        "click",
                        updateNextButtonState
                    );

                if (postid) {
                    giveawayData.postId = postid;
                }

                break;
            case "channels":
            case "announcement":
            case "results":
                const checkboxes =
                    document.querySelectorAll(`.channel-checkbox`);
                checkboxes.forEach((checkbox) => {
                    checkbox.addEventListener("change", updateNextButtonState);
                });
                break;
            case "dates":
                const startImmediatelyToggle =
                    document.getElementById("start-immediately");
                const startDateDisplay =
                    document.getElementById("start-date-display");
                const endDateDisplay =
                    document.getElementById("end-date-display");

                if (startImmediatelyToggle) {
                    startImmediatelyToggle.addEventListener(
                        "change",
                        updateNextButtonState
                    );
                }

                function observeDateChanges(targetNode) {
                    if (!targetNode) return; // Если элемента нет, выходим

                    const observer = new MutationObserver(
                        updateNextButtonState
                    );
                    observer.observe(targetNode, {
                        childList: true,
                        subtree: true,
                        characterData: true,
                    });
                }

                observeDateChanges(startDateDisplay);
                observeDateChanges(endDateDisplay);
                break;

            case "winners":
                const winnersCountInput =
                    document.getElementById("winners-count");
                if (winnersCountInput)
                    winnersCountInput.addEventListener(
                        "input",
                        updateNextButtonState
                    );
                break;
        }

        updateNextButtonState();

        if (window.lucide) {
            window.lucide.createIcons();
        }

        const datePickerDialog = document.getElementById("date-picker-dialog");
        const startDateField = document.getElementById("start-date-field");
        const endDateField = document.getElementById("end-date-field");
        const applyDateButton = document.getElementById("apply-date");
        const cancelDateButton = document.getElementById("cancel-date");
        const timePicker = document.getElementById("time-picker");

        if (startDateField) {
            startDateField.addEventListener("click", () => {
                activeDateField = "start"; // Указываем, что активно поле начала
                datePickerDialog.style.display = "flex";
            });
        }

        if (endDateField) {
            endDateField.addEventListener("click", () => {
                activeDateField = "end"; // Указываем, что активно поле окончания
                datePickerDialog.style.display = "flex";
            });
        }

        if (cancelDateButton) {
            cancelDateButton.addEventListener("click", () => {
                datePickerDialog.style.display = "none";
            });
        }

        if (applyDateButton) {
            applyDateButton.addEventListener("click", () => {
                const selectedDate = document.querySelector(
                    ".calendar-day.selected"
                );
                const timePicker = document.getElementById("time-picker");

                if (selectedDate && timePicker) {
                    let dateDisplay;

                    // Определяем, в какое поле записывать дату
                    if (activeDateField === "start") {
                        dateDisplay =
                            document.getElementById("start-date-display");
                    } else if (activeDateField === "end") {
                        dateDisplay =
                            document.getElementById("end-date-display");
                    }

                    if (dateDisplay) {
                        const day = selectedDate.textContent;
                        const month = currentMonth + 1;
                        const year = currentYear;
                        const time = timePicker.value;

                        // Форматируем дату
                        const formattedDate = `${day
                            .toString()
                            .padStart(2, "0")}.${month
                            .toString()
                            .padStart(2, "0")}.${year} ${time}`;
                        dateDisplay.textContent = formattedDate;

                        if (activeDateField === "start") {
                            giveawayData.startDate = formattedDate;
                        } else if (activeDateField === "end") {
                            giveawayData.endDate = formattedDate;
                        }

                        updateNextButtonState();
                    }
                }
                datePickerDialog.style.display = "none";
            });
        }
        const buttonTextField = document.getElementById("button-text");
        const sampleButtons = document.querySelectorAll(".sample-button");

        const savedButtonText = sessionStorage.getItem("selectedButtonText");
        if (savedButtonText && buttonTextField) {
            buttonTextField.value = savedButtonText;
        }

        sampleButtons.forEach((button) => {
            button.addEventListener("click", () => {
                const buttonText = button.textContent;

                if (buttonTextField) {
                    buttonTextField.value = buttonText;
                }

                sessionStorage.setItem("selectedButtonText", buttonText);

                sampleButtons.forEach((btn) =>
                    btn.classList.remove("sample-button-active")
                );

                button.classList.add("sample-button-active");
            });
        });
    }

    // Инициализация шага основных настроек
    function initBasicsStep() {
        const nameInput = document.getElementById("giveaway-name");
        const selectPostBtn = document.getElementById("selectPostBtn");
        const namePost = selectPostBtn.querySelector("span");
        const postid = namePost ? namePost.id : null;
        const buttonTextInput = document.getElementById("button-text");
        const sampleButtons = document.querySelectorAll(".sample-button");
        // Восстановление данных
        if (nameInput) {
            nameInput.value = giveawayData.name;
            nameInput.addEventListener("input", () => {
                giveawayData.name = nameInput.value;
                updateNextButtonState();
            });
        }
        if (namePost) {
            namePost.textContent = giveawayData.selectedPost;
        }
        if (postid) {
            const postElement = document.getElementById(postid);

            if (postElement) {
                postElement.id = giveawayData.postId;
            }
        }
        if (buttonTextInput) {
            buttonTextInput.value = giveawayData.buttonText;
            buttonTextInput.addEventListener("input", () => {
                giveawayData.buttonText = buttonTextInput.value;
                updateNextButtonState();
            });
        }

        // Обработчик для кнопки выбора поста
        if (selectPostBtn) {
            selectPostBtn.addEventListener("click", () => {
                giveawayData.selectedPost = "Выбранный пост";
                if (namePost) namePost.textContent = giveawayData.selectedPost;
                updateNextButtonState();
            });
        }

        sampleButtons.forEach((button) => {
            button.addEventListener("click", () => {
                const buttonText = button.textContent;
                if (buttonTextInput) {
                    buttonTextInput.value = buttonText;
                    giveawayData.buttonText = buttonText;
                }
                sampleButtons.forEach((btn) =>
                    btn.classList.remove("sample-button-active")
                );
                button.classList.add("sample-button-active");
                updateNextButtonState();
            });
        });

        updateNextButtonState();
    }

    // Инициализация шага каналов
    async function initChannelsStep(type) {
        const channelsListId = `${type}-channels-list`;
        const channelsList = document.getElementById(channelsListId);

        if (!channelsList) {
            console.error(`Элемент с ID ${channelsListId} не найден.`);
            return;
        }

        channelsList.innerHTML = "";

        try {
            const tg = window.Telegram?.WebApp;
            const userId = tg?.initDataUnsafe?.user?.id;

            if (!userId) {
                console.error("Не удалось получить ID пользователя.");
                return;
            }

            const response = await fetch("/api/get_channel", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId, type }),
            });

            if (!response.ok) {
                console.error("Ошибка ответа от сервера:", response.statusText);
                return;
            }

            const channels = await response.json();
            document.getElementById("channels-loader").style.display = "none";
            let selectedChannels;
            switch (type) {
                case "subscription":
                    giveawayData.subscriptionChannels = channels;
                    selectedChannels =
                        giveawayData.selectedSubscriptionChannels;
                    break;
                case "announcement":
                    giveawayData.announcementChannels = channels;
                    selectedChannels =
                        giveawayData.selectedAnnouncementChannels;
                    break;
                case "result":
                    giveawayData.resultChannels = channels;
                    selectedChannels = giveawayData.selectedResultChannels;
                    break;
            }

            // Отображение загруженных каналов
            if (channels.length > 0) {
                channels.forEach((channel) => {
                    const channelElement = createChannelElementSub(
                        channel,
                        channelsListId
                    );
                    channelsList.appendChild(channelElement);

                    const checkbox =
                        channelElement.querySelector(".channel-checkbox");
                    if (
                        checkbox &&
                        selectedChannels.includes(channel.id.toString())
                    ) {
                        checkbox.checked = true;
                    }
                });
            } else {
                channelsList.innerHTML = "<p>Нет каналов для отображения.</p>";
            }

            // Отображение предупреждения для каналов подписки
            if (type === "subscription") {
                const warningElement = document.getElementById(
                    "no-channels-warning"
                );
                if (warningElement) {
                    warningElement.style.display =
                        channels.length > 0 ? "none" : "block";
                }
            }
        } catch (error) {
            console.error("Ошибка загрузки каналов:", error);
        }
    }

    // Обработчик для кнопки добавления канала (делегирование событий)
    document.addEventListener("click", async (event) => {
        if (event.target && event.target.id === "add-button") {
            const channelInput = document.getElementById("channel-name-input");
            const channelsListSubscrip = document.getElementById(
                "subscription-channels-list"
            );

            if (!channelInput) {
                console.error("Поле ввода канала не найдено!");
                return;
            }

            const channelName = channelInput.value.trim();
            if (!channelName) {
                alertify.show("Введите название канала!", 2000);
                return;
            }

            try {
                const response = await fetch("/api/add_channel_sub", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name: channelName }),
                });

                if (!response.ok) {
                    throw new Error("Ошибка при добавлении канала");
                }

                const channel = await response.json();

                const newChannelElement = createChannelElementSub(
                    channel,
                    "subscription-channels-list"
                );

                if (channelsListSubscrip) {
                    channelsListSubscrip.appendChild(newChannelElement);

                    const checkbox =
                        newChannelElement.querySelector(".channel-checkbox");
                    if (checkbox) {
                        checkbox.checked = true;
                        addSelectedChannel(
                            channel.id.toString(),
                            "subscription"
                        );
                    }

                    giveawayData.subscriptionChannels.push(channel);
                }

                channelInput.value = "";
                const channelModalOverlay = document.getElementById(
                    "modalOverlayChannel"
                );
                channelModalOverlay.classList.remove("show");
                const modalContainer =
                    channelModalOverlay.querySelector(".modal-container");
                modalContainer.classList.remove("show");
                setTimeout(() => {
                    channelModalOverlay.style.display = "none";
                }, 300);

                saveCurrentStepData();
            } catch (error) {
                alertify.show("Произошла ошибка. Попробуйте позже.", 2000);
            }
        }
    });

    function generateAvatarLetter(name) {
        const letter = name.charAt(0).toUpperCase();
        const color = getRandomColor();
        return `
          <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
            <circle cx="20" cy="20" r="20" fill="${color}" /> <!-- Делаем круглый фон -->
            <text x="40%" y="60%" fontSize="20" textAnchor="middle" dominantBaseline="central" fill="white">${letter}</text>
          </svg>
        `;
    }

    function getRandomColor() {
        const letters = "0123456789ABCDEF";
        let color = "#";
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    function createChannelElementSub(channel, type) {
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
      <div class="channel-actions">
        <label class="checkbox-container">
          <input type="checkbox" class="channel-checkbox" data-id="${
              channel.id
          }" data-type="${type}">
          <span class="checkmark"></span>
        </label>
      </div>
    `;

        // Добавляем обработчик событий для чекбокса
        const checkbox = channelElement.querySelector(".channel-checkbox");
        if (checkbox) {
            checkbox.addEventListener("change", (event) => {
                const isChecked = event.target.checked;
                const channelId = event.target.getAttribute("data-id");
                const channelType = event.target.getAttribute("data-type");

                const actualType = channelType.split("-")[0];

                if (isChecked) {
                    addSelectedChannel(channelId, actualType);
                } else {
                    removeSelectedChannel(channelId, actualType);
                }

                saveCurrentStepData();
            });
        }

        return channelElement;
    }

    function addSelectedChannel(channelId, type) {
        switch (type) {
            case "subscription":
                if (
                    !giveawayData.selectedSubscriptionChannels.includes(
                        channelId
                    )
                ) {
                    giveawayData.selectedSubscriptionChannels.push(channelId);
                }
                break;
            case "announcement":
                if (
                    !giveawayData.selectedAnnouncementChannels.includes(
                        channelId
                    )
                ) {
                    giveawayData.selectedAnnouncementChannels.push(channelId);
                }
                break;
            case "result":
                if (!giveawayData.selectedResultChannels.includes(channelId)) {
                    giveawayData.selectedResultChannels.push(channelId);
                }
                break;
        }
    }

    function removeSelectedChannel(channelId, type) {
        switch (type) {
            case "subscription":
                giveawayData.selectedSubscriptionChannels =
                    giveawayData.selectedSubscriptionChannels.filter(
                        (id) => id !== channelId
                    );
                break;
            case "announcement":
                giveawayData.selectedAnnouncementChannels =
                    giveawayData.selectedAnnouncementChannels.filter(
                        (id) => id !== channelId
                    );
                break;
            case "result":
                giveawayData.selectedResultChannels =
                    giveawayData.selectedResultChannels.filter(
                        (id) => id !== channelId
                    );
                break;
        }
    }

    // Инициализация шага дат
    function initDatesStep() {
        const startImmediatelyToggle =
            document.getElementById("start-immediately");
        const startDateField = document.getElementById("start-date-field");
        const endDateField = document.getElementById("end-date-field");
        const startDateDisplay = document.getElementById("start-date-display");
        const endDateDisplay = document.getElementById("end-date-display");

        // Восстановление данных
        if (startImmediatelyToggle) {
            startImmediatelyToggle.checked = giveawayData.startImmediately;

            startImmediatelyToggle.addEventListener("change", function () {
                giveawayData.startImmediately = this.checked;
                if (startDateField) {
                    startDateField.style.opacity = this.checked ? "0.5" : "1";
                    startDateField.style.pointerEvents = this.checked
                        ? "none"
                        : "auto";
                }
                updateNextButtonState();
            });

            startImmediatelyToggle.dispatchEvent(new Event("change"));
        }

        if (startDateDisplay && giveawayData.startDate) {
            startDateDisplay.textContent = giveawayData.startDate;
        }

        if (endDateDisplay && giveawayData.endDate) {
            endDateDisplay.textContent = giveawayData.endDate;
        }

        // Обработчики для полей выбора даты
        if (startDateField) {
            startDateField.addEventListener("click", () => {
                if (!giveawayData.startImmediately) {
                    activeDateField = "start";
                    openDatePicker();
                }
            });
        }

        if (endDateField) {
            endDateField.addEventListener("click", () => {
                activeDateField = "end";
                openDatePicker();
            });
        }

        function observeDateChanges(targetNode) {
            if (!targetNode) return; // Если элемента нет, ничего не делаем

            const observer = new MutationObserver(updateNextButtonState);

            observer.observe(targetNode, {
                characterData: true,
                childList: true,
                subtree: true,
            });
        }

        observeDateChanges(document.getElementById("start-date-display"));
        observeDateChanges(document.getElementById("end-date-display"));

        updateNextButtonState();
    }

    // Инициализация шага победителей
    function initWinnersStep() {
        const winnersCountInput = document.getElementById("winners-count");

        if (winnersCountInput) {
            winnersCountInput.value = giveawayData.winnersCount;

            winnersCountInput.addEventListener("change", function () {
                const value = Number.parseInt(this.value) || 1;
                giveawayData.winnersCount = Math.min(Math.max(value, 1), 30);
                this.value = giveawayData.winnersCount;
            });
        }
    }

    // Инициализация шага проверки
    function initReviewStep() {
        const editButtons = document.querySelectorAll(".button-edit-button");
        editButtons.forEach((button) => {
            button.addEventListener("click", () => {
                const step = Number.parseInt(button.getAttribute("data-step"));
                if (!isNaN(step) && step >= 0 && step < steps.length) {
                    currentStep = step;
                    loadStep(currentStep);
                }
            });
        });
    }

    // Заполнение страницы проверки
    function populateReviewPage() {
        // Каналы подписки
        const subscriptionChannelsElement = document.getElementById(
            "review-subscription-channels"
        );
        const selectedSubscriptionChannels =
            giveawayData.subscriptionChannels.filter((channel) =>
                giveawayData.selectedSubscriptionChannels.includes(
                    channel.id.toString()
                )
            );
        populateChannelsList(
            subscriptionChannelsElement,
            selectedSubscriptionChannels
        );

        // Каналы анонса
        const announcementChannelsElement = document.getElementById(
            "review-announcement-channels"
        );
        const selectedAnnouncementChannels =
            giveawayData.announcementChannels.filter((channel) =>
                giveawayData.selectedAnnouncementChannels.includes(
                    channel.id.toString()
                )
            );
        populateChannelsList(
            announcementChannelsElement,
            selectedAnnouncementChannels
        );

        // Каналы итогов
        const resultChannelsElement = document.getElementById(
            "review-result-channels"
        );
        const selectedResultChannels = giveawayData.resultChannels.filter(
            (channel) =>
                giveawayData.selectedResultChannels.includes(
                    channel.id.toString()
                )
        );
        populateChannelsList(resultChannelsElement, selectedResultChannels);

        // Основные настройки
        const reviewName = document.getElementById("review-name");
        if (reviewName)
            reviewName.textContent = giveawayData.name || "Не указано";

        const reviewPost = document.getElementById("review-post");
        if (reviewPost)
            reviewPost.textContent = giveawayData.selectedPost || "Не выбран";

        const reviewButtonText = document.getElementById("review-button-text");
        if (reviewButtonText)
            reviewButtonText.textContent = giveawayData.buttonText;

        // Даты
        const reviewStartDate = document.getElementById("review-start-date");
        if (reviewStartDate) {
            reviewStartDate.textContent = giveawayData.startImmediately
                ? "начнется сразу"
                : giveawayData.startDate || "не указана";
        }

        const reviewEndDate = document.getElementById("review-end-date");
        if (reviewEndDate) {
            reviewEndDate.textContent = giveawayData.endDate || "не указана";
        }

        // Победители
        const reviewWinnersCount = document.getElementById(
            "review-winners-count"
        );
        if (reviewWinnersCount) {
            reviewWinnersCount.textContent = giveawayData.winnersCount;
        }
    }

    function populateChannelsList(element, channels) {
        if (!element) return;

        element.innerHTML = "";

        if (channels.length === 0) {
            const emptyMessage = document.createElement("div");
            emptyMessage.className = "review-empty-message";
            emptyMessage.textContent = "Каналы не выбраны";
            element.appendChild(emptyMessage);
        } else {
            channels.forEach((channel) => {
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
                element.appendChild(channelElement);
            });
        }
    }

    // Открытие модального окна выбора даты
    function openDatePicker() {
        const datePickerDialog = document.getElementById("date-picker-dialog");
        initCalendar(); // Инициализируем календарь с сохраненными датами
        datePickerDialog.style.display = "flex";

        const applyDateButton = document.getElementById("apply-date");
        const cancelDateButton = document.getElementById("cancel-date");

        cancelDateButton.addEventListener("click", () => {
            datePickerDialog.style.display = "none";
        });

        applyDateButton.addEventListener("click", () => {
            const selectedDate = document.querySelector(
                ".calendar-day.selected"
            );
            const timePicker = document.getElementById("time-picker");

            if (selectedDate && timePicker) {
                const day = selectedDate.textContent.padStart(2, "0");
                const month = (currentMonth + 1).toString().padStart(2, "0");
                const year = currentYear;
                const time = timePicker.value;

                const formattedDate = `${day}.${month}.${year} ${time}`;
                const dateDisplay =
                    activeDateField === "start"
                        ? document.getElementById("start-date-display")
                        : document.getElementById("end-date-display");

                if (dateDisplay) {
                    dateDisplay.textContent = formattedDate;
                    if (activeDateField === "start") {
                        giveawayData.startDate = formattedDate;
                    } else {
                        giveawayData.endDate = formattedDate;
                    }
                    updateNextButtonState();
                }
            }
            datePickerDialog.style.display = "none";
        });
    }

    // Добавляем новую функцию для восстановления состояния чекбоксов
    function restoreCheckboxStates() {
        const currentStepName = steps[currentStep];
        let checkboxes;
        let selectedChannels;

        switch (currentStepName) {
            case "channels":
                checkboxes = document.querySelectorAll(
                    "#subscription-channels-list .channel-checkbox"
                );
                selectedChannels = giveawayData.selectedSubscriptionChannels;
                break;
            case "announcement":
                checkboxes = document.querySelectorAll(
                    "#announcement-channels-list .channel-checkbox"
                );
                selectedChannels = giveawayData.selectedAnnouncementChannels;
                break;
            case "results":
                checkboxes = document.querySelectorAll(
                    "#result-channels-list .channel-checkbox"
                );
                selectedChannels = giveawayData.selectedResultChannels;
                break;
            default:
                return;
        }

        checkboxes.forEach((checkbox) => {
            const channelId = checkbox.getAttribute("data-id");
            checkbox.checked = selectedChannels.includes(channelId);
        });
    }

    try {
        // Загружаем сохраненные данные
        savedRaffleData = await getSavedRaffle();
        console.log("Saved raffle data:", savedRaffleData);

        if (savedRaffleData && savedRaffleData.giveawayData) {
            // Обновляем giveawayData сохраненными значениями
            Object.assign(giveawayData, savedRaffleData.giveawayData);

            // Восстанавливаем шаг
            currentStep = savedRaffleData.step + 1 || 0;
            console.log("Restored step:", currentStep);

            // Восстанавливаем специфичные данные
            if (savedRaffleData.giveawayData.post_text) {
                giveawayData.selectedPost =
                    savedRaffleData.giveawayData.post_text;
            }
            if (savedRaffleData.giveawayData.post_id) {
                giveawayData.postId = savedRaffleData.giveawayData.post_id;
            }
            console.log(savedRaffleData.giveawayData.user_winners);
            if (savedRaffleData.giveawayData.user_winners) {
                giveawayData.winnersCount =
                    savedRaffleData.giveawayData.user_winners;
            }
        }
    } catch (e) {
        console.error("Error loading saved data:", e);
        currentStep = 0;
    }

    loadStep(currentStep);
});

async function getSavedRaffle() {
    const tg = window.Telegram?.WebApp;
    const userId = tg?.initDataUnsafe?.user?.id;
    const type = "channel";
    try {
        const response = await fetch("/api/get-save-raffle", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ user_id: userId }),
        });

        if (!response.ok) {
            throw new Error("Ошибка при получении сохраненного розыгрыша");
        }

        const data = await response.json();

        const response_channel = await fetch("/api/get_channel", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId, type }),
        });

        if (!response_channel.ok) {
            throw new Error(
                "Ошибка ответа от сервера:",
                response_channel.statusText
            );
        }

        const channels = await response_channel.json();

        return {
            step: data.step + 1 || 0,
            giveawayData: {
                name: data.name || "",
                selectedPost: data.post_text || "Выбрать пост",
                postId: data.post_id || "",
                buttonText: data.post_button || "Участвовать",
                selectedSubscriptionChannels:
                    data.sub_channel_id?.map(String) || [],
                selectedAnnouncementChannels:
                    data.announcet_channel_id?.map(String) || [],
                selectedResultChannels:
                    data.results_channel_id?.map(String) || [],
                startImmediately: data.start_date === "immediately",
                startDate: data.start_date || "",
                endDate: data.end_date || "",
                winnersCount: data.user_winners || 1,
                subscriptionChannels: channels || [],
                announcementChannels: channels || [],
                resultChannels: channels || [],
            },
        };
    } catch (error) {
        console.error("Ошибка запроса:", error);
        return null;
    }
}

// Инициализация состояния приложения
const giveawayData = {
    name: "",
    selectedPost: "Выбрать пост",
    postId: "",
    buttonText: "Участвовать",
    subscriptionChannels: [],
    announcementChannels: [],
    resultChannels: [],
    selectedSubscriptionChannels: [],
    selectedAnnouncementChannels: [],
    selectedResultChannels: [],
    addResultsToAnnouncement: false,
    startImmediately: true,
    startDate: "",
    endDate: "",
    winnersCount: 1,
};
