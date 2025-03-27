document.addEventListener('DOMContentLoaded', function () {

    let tg = window.Telegram?.WebApp;
    if (tg) {
        tg.BackButton.show();

        tg.BackButton.onClick(function () {
            window.location.href = '/';
        });
    }

    const tabTriggers = document.querySelectorAll('.tab-trigger');
    const tabContents = document.querySelectorAll('.tab-content');

    tabTriggers.forEach(trigger => {
        trigger.addEventListener('click', function () {
            const status = this.getAttribute('data-status');

            tabTriggers.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            this.classList.add('active');
            document.querySelector(`.tab-content[data-status="${status}"]`).classList.add('active');
        });
    });
});
