document.addEventListener("DOMContentLoaded", function () {
    const tg = window.Telegram?.WebApp;

    const userId = tg?.initDataUnsafe?.user?.id || null;
    if (!userId) {
        console.error("Ошибка: Не удалось получить ID пользователя.");
        return;
    }

    async function sendPostRequest(url) {
        try {
            const response = await fetch(url+'/mobile', {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId })
            });
            const result = await response.json();

            const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
            console.log(`Ссылка: https://t.me/RandomRace_bot?start=${result.new}`);
            if (isMobile) {
                window.location.href = `https://t.me/RandomRace_bot?start=${result.new}`;
                console.log('отработал')
            } else {
                const response = await fetch(url, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: userId })
                });
                console.log('отработал 2')
                const result = await response.json();
            }

            tg.close();
        } catch (error) {
            console.error("Ошибка запроса:", error);
        }
    }


    function setupButtonListeners(selector, url) {
        const buttons = document.querySelectorAll(selector);
        if (buttons.length === 0) {
            console.error(`Кнопки ${selector} не найдены!`);
            return;
        }

        buttons.forEach(button => {
            button.addEventListener("click", function () {
                console.log(`Клик по ${selector}`);
                sendPostRequest(url);
            });
        });
    }

    // Добавляем обработчики на все кнопки
    setupButtonListeners("#add-newpost", "/api/new_post");
    setupButtonListeners("#add-newchannel", "/api/new_channel");
});
