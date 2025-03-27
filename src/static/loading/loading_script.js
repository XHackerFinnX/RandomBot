document.addEventListener('DOMContentLoaded', function () {
    const successCloseButton = document.getElementById('success-close-button');
    const tg = window.Telegram?.WebApp;
    tg.BackButton.show()

    tg.BackButton.onClick(() => {
        window.location.href = "/"
    })

    // Прослушиватель событий для кнопки закрытия
    if (successCloseButton) {
        successCloseButton.addEventListener('click', () => {
            console.log(tg);
            if (tg) {
                tg.close(); // Закрытие Telegram Web App только если tg существует
            } else {
                console.error("Telegram Web App API не доступен.");
            }
        });
    }
});
