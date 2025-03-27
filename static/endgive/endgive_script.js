document.addEventListener('DOMContentLoaded', async function () {
    // Get Telegram WebApp instance
    const tg = window.Telegram?.WebApp;
    const userId = tg?.initDataUnsafe?.user?.id;

    // Get DOM elements
    const loadingScreen = document.getElementById('loading-screen');
    const mainScreen = document.getElementById('main-screen');
    const successScreen = document.getElementById('success-screen');
    const successScreenTrue = document.getElementById('success-screen-true');
    const aboutDialog = document.getElementById('about-dialog');
    const timeLeftElement = document.getElementById('time-left');
    const channelsContainer = document.getElementById('channels-container');
    const raffleId = new URLSearchParams(window.location.search).get('raffle_id');

    // Button elements
    const aboutButton = document.getElementById('about-button');
    const dialogOkButton = document.getElementById('dialog-ok-button');
    const dialogOverlay = document.getElementById('dialog-overlay');
    const checkSubscriptionButton = document.getElementById('check-subscription-button');
    const closeButton = document.getElementById('close-button');
    const successCloseButton = document.getElementById('success-close-button');

    // Mock data
    let mockChannels = [];
    let subUserAll = false;

    try {
        const response = await fetch('/api/channels-raffle-sub', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ hashid: raffleId, userid: userId })
        });

        if (!response.ok) {
            throw new Error(`Ошибка запроса: ${response.status}`);
        }

        const result = await response.json();
        mockChannels = result.data_channel;
        endDate = result.end_date;
        subUserAll = result.all_sub;

        startCountdownTimer(endDate)

    } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
    }

    showScreen(loadingScreen);

    setTimeout(() => {

        if (subUserAll) {
            showScreen(successScreenTrue);
        } else {
            populateChannels(mockChannels);
            showScreen(mainScreen);
        }
    }, 2000);

    // Event listeners
    aboutButton.addEventListener('click', () => {
        aboutDialog.classList.remove('hidden');
    });

    dialogOkButton.addEventListener('click', () => {
        aboutDialog.classList.add('hidden');
    });

    dialogOverlay.addEventListener('click', () => {
        aboutDialog.classList.add('hidden');
    });

    checkSubscriptionButton.addEventListener('click', () => {
        showScreen(loadingScreen);
        checkSubscription();
    });

    async function checkSubscription() {
        try {
            const response = await fetch('/api/check-subscription-user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify({ userId, raffleId, mockChannels })
            });

            const result = await response.json();

            if (result.ok) {
                // Показать успешное сообщение
                showScreen(successScreenTrue);
            } else {
                // Показать сообщение об ошибке
                showScreen(successScreen);
            }
        } catch (error) {
            console.error('Ошибка при проверке подписки:', error);
            showScreen(successScreen);
        }
    }

    closeButton.addEventListener('click', () => {
        if (tg && tg.close) {
            tg.close();
        } else {
            console.log('Close button clicked');
        }
    });

    successCloseButton.addEventListener('click', () => {
        showScreen(mainScreen);
    });

    // Helper Functions
    function showScreen(screenToShow) {
        // Hide all screens
        loadingScreen.classList.add('hidden');
        successScreenTrue.classList.add('hidden');
        mainScreen.classList.add('hidden');
        successScreen.classList.add('hidden');

        // Show the requested screen
        screenToShow.classList.remove('hidden');
    }

    function getMoscowTime() {
        const now = new Date().toLocaleString("en-US", {
            timeZone: "Europe/Moscow",
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: false
        });

        const [datePart, timePart] = now.split(', ');
        const [month, day, year] = datePart.split('/');

        return `${year}-${month}-${day} ${timePart}`;
    }

    function startCountdownTimer(endDate) {
        const countdownInterval = setInterval(() => {
            const now = new Date(getMoscowTime()).getTime();
            const endTime = new Date(endDate).getTime();
            const timeDifference = endTime - now;

            if (timeDifference <= 0) {
                clearInterval(countdownInterval);
                timeLeftElement.textContent = '⏳ Время истекло';
                return;
            }

            const days = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeDifference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeDifference % (1000 * 60)) / 1000);

            timeLeftElement.textContent = formatTimeLeft(days, hours, minutes, seconds);
        }, 1000);
    }

    function formatTimeLeft(days, hours, minutes, seconds) {
        return `${days}д ${hours < 10 ? '0' + hours : hours}:${minutes < 10 ? '0' + minutes : minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
    }

    function populateChannels(channels) {
        // Clear previous channels
        channelsContainer.innerHTML = '';

        // Add each channel to the container
        channels.forEach(channel => {
            const channelElement = document.createElement('div');
            channelElement.className = 'channel-item scale-transition';

            // Условие для отображения статуса подписки
            const subscriptionText = channel.status_sub
                ? 'Вы подписаны'
                : 'Подписаться';

            const isSubscribed = channel.status_sub ? 'subscribe-button button-sub' : 'subscribe-button button-primary';

            const maxLength = 12;
            channelElement.innerHTML = `
            <div class="flex items-center justify-between w-full">
                <div class="flex items-center">
                <div class="w-10 h-10 rounded-full overflow-hidden mr-3 flex-shrink-0">
                    ${channel.photo_url
                                ? `<img src="${channel.photo_url}" alt="${channel.name}" class="w-full h-full object-cover" loading="eager">`
                                : `<div class="w-full h-full flex items-center justify-center bg-primary text-white">${generateAvatarLetter(channel.name)}</div>`
                            }
                </div>
                <div class="flex flex-col">
                    <h3 class="font-medium text-sm text-foreground">${channel.name.length > maxLength ? channel.name.slice(0, maxLength) + '...' : channel.name}</h3>
                </div>
                </div>
                <button 
                class="${isSubscribed} text-xs px-4 py-1.5 transition-all"
                data-channel-id="${channel.id}"
                ${channel.status_sub ? 'disabled' : ''}
                >
                ${subscriptionText}
                </button>
            </div>
            `;

            channelsContainer.appendChild(channelElement);

            // Add event listener to the subscribe button
            const subscribeButton = channelElement.querySelector('.subscribe-button');
            subscribeButton.addEventListener('click', () => {
                handleSubscribe(`${channel.id}-${channel.channel_tg}`);
            });
        });
    }

    function handleSubscribe(channelId) {
        // Проверим, что channelId — это строка
        console.log(channelId)
        if (typeof channelId !== 'string') {
            console.error('channelId должен быть строкой');
            return;  // Прерываем выполнение, если channelId не строка
        }

        // Разделяем строку на id и username (если они присутствуют)
        const [idPart, usernamePart] = channelId.split('-@');  // Разделяем на ID и username

        let channelUrl;

        // Если есть публичное имя канала (username)
        if (usernamePart) {
            channelUrl = `https://t.me/${usernamePart}`;
        } else {
            // Если username отсутствует, используем ID (приватный канал)
            channelUrl = `https://t.me/c/${idPart.replace('-100', '')}`;
        }

        // Попробуем открыть канал
        try {
            window.open(channelUrl, '_blank');
        } catch (e) {
            console.error('Ошибка при открытии канала:', e);
        }
    }


    function generateAvatarLetter(name) {
        const letter = name.charAt(0).toUpperCase();
        const color = getRandomColor();
        return `
        <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
          <circle cx="20" cy="20" r="20" fill="${color}" />
          <text x="50%" y="50%" font-size="18" text-anchor="middle" dominant-baseline="central" fill="white" font-family="system-ui, sans-serif">${letter}</text>
        </svg>
      `;
    }

    function getRandomColor() {
        const colors = [
            "#3B82F6", // blue
            "#10B981", // green
            "#8B5CF6", // purple
            "#F97316", // orange
            "#EC4899", // pink
            "#6366F1", // indigo
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }
});
