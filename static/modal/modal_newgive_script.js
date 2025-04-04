document.addEventListener("click", function (event) {
    // Открытие модального окна выбора поста
    if (event.target.closest("#selectPostBtn")) {
        const postModalOverlay = document.getElementById("modalOverlay");
        postModalOverlay.classList.add("show");
        postModalOverlay.style.display = "flex";
        const modalContainer =
            postModalOverlay.querySelector(".modal-container");
        modalContainer.classList.add("show");

        // Загрузка постов при открытии модального окна
        openPostsModal();
    }

    // Закрытие модального окна выбора поста
    if (event.target.closest("#closeModalBtn")) {
        const postModalOverlay = document.getElementById("modalOverlay");
        postModalOverlay.classList.remove("show");
        const modalContainer =
            postModalOverlay.querySelector(".modal-container");
        modalContainer.classList.remove("show");
        setTimeout(() => {
            postModalOverlay.style.display = "none";
        }, 300);
    }

    // Открытие модального окна для добавления каналов
    if (event.target.closest("#open-channel-modal-btn")) {
        const channelModalOverlay = document.getElementById(
            "modalOverlayChannel"
        );
        channelModalOverlay.classList.add("show");
        channelModalOverlay.style.display = "flex";
        const modalContainer =
            channelModalOverlay.querySelector(".modal-container");
        modalContainer.classList.add("show");
    }

    // Закрытие модального окна для добавления каналов
    if (event.target.closest("#closeChannelModalBtn")) {
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
    }
});

function openPostsModal() {
    loadPostsToModal().then(() => {
        const postModalOverlay = document.getElementById("modalOverlay");
        postModalOverlay.classList.add("animate-fade-in");
        postModalOverlay
            .querySelector(".modal-container")
            .classList.add("animate-slide-up");
    });
}

async function loadPostsToModal() {
    const tg = window.Telegram?.WebApp;
    const userId = tg?.initDataUnsafe?.user?.id;

    try {
        const response = await fetch("/api/get_posts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId }),
        });

        const posts = await response.json();
        const postsList = document.getElementById("modalPostsList");
        const noPostsMessage = document.getElementById("noPostsMessage");
        const postsListContainer =
            document.getElementById("postsListContainer");

        postsList.innerHTML = "";

        if (posts.length > 0) {
            postsListContainer.classList.remove("hidden");
            noPostsMessage.classList.add("hidden");

            const modalContent = document.querySelector(".modal-content");
            if (modalContent) {
                modalContent.style.flexGrow = "0";
            }

            const addButtonContainer = document.querySelector(
                ".add-button-container"
            );
            if (addButtonContainer) {
                addButtonContainer.style.display = "block";
            }

            posts.forEach((post) => {
                const postElement = createPostElement(post);
                postsList.appendChild(postElement);
            });
        } else {
            postsListContainer.classList.add("hidden");
            noPostsMessage.classList.remove("hidden");
        }
    } catch (error) {
        console.error("Ошибка загрузки постов:", error);
    }
}

function createPostElement(post) {
    const postElement = document.createElement("div");
    postElement.className = "post-item";
    postElement.innerHTML = `
      <div class="post-content" id="${post.id}">
        <div class="post-details">
          <h3 class="post-title">${post.title}</h3>
        </div>
        <div class="post-actions">
          <button class="action-button view-button" title="Выбрать">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 13l4 4L19 7" />
            </svg>
          </button>
        </div>
      </div>
    `;

    // Добавление обработчика события на кнопку "Выбрать"
    postElement.querySelector(".view-button").addEventListener("click", () => {
        // Находим элемент, куда нужно записать выбранный пост
        const selectPostBtn = document.getElementById("selectPostBtn");
        // Обновляем содержимое элемента #selectPostBtn
        selectPostBtn.innerHTML = `
          <div class="field-with-icon">
            <span id="${post.id}">${post.title}</span>
            <i data-lucide="chevron-right"></i>
          </div>
        `;

        // Закрытие модального окна после выбора
        const postModalOverlay = document.getElementById("modalOverlay");
        postModalOverlay.classList.remove("show");
        const modalContainer =
            postModalOverlay.querySelector(".modal-container");
        modalContainer.classList.remove("show");
        setTimeout(() => {
            postModalOverlay.style.display = "none";
        }, 300);
    });

    // Убедитесь, что элементы поста добавляются в DOM
    const postsList = document.getElementById("modalPostsList");
    if (postsList) {
        postsList.appendChild(postElement);
    } else {
        console.error("Элемент с id modalPostsList не найден.");
    }

    return postElement;
}
