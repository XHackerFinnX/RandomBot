document.addEventListener("DOMContentLoaded", function () {
    const newGiveawayBtn = document.getElementById("new-giveaway-btn");
    const allGiveawayBtn = document.getElementById("view-all-giveaways-btn");

    newGiveawayBtn.addEventListener("click", function () {
        window.location.href = "/newgive";
    });

    allGiveawayBtn.addEventListener("click", function () {
        window.location.href = "/allgive";
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const tg = window.Telegram?.WebApp;
    tg.BackButton.hide();

    if (tg) {
        tg.expand();
    }

    const userData = {
        name: "Пользователь",
    };

    init();

    function init() {
        setTimeout(() => {
            document.getElementById("loading").classList.add("hidden");
            document.getElementById("main-content").classList.remove("hidden");
        }, 300);

        if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {
            userData.name = tg.initDataUnsafe.user.first_name;
        }

        updateUsername(userData.name);
    }

    function updateUsername(name) {
        const usernameElement = document.getElementById("user_name");
        if (usernameElement) {
            usernameElement.textContent = name;
        }
    }
});

document.addEventListener("DOMContentLoaded", async function () {
    const tg = window.Telegram?.WebApp;

    const channelsList = document.getElementById("channels-list");
    const noChannelsContainer = document.getElementById(
        "no-channels-container"
    );

    const postsList = document.getElementById("posts-list");
    const noPostsContainer = document.getElementById("no-posts-container");

    async function fetchData() {
        const userId = tg?.initDataUnsafe?.user?.id;
        if (!userId) {
            console.error("Не удалось получить ID пользователя.");
            return;
        }

        try {
            const response = await fetch("/api/get_data", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId }),
            });

            if (!response.ok) {
                console.error("Ошибка ответа от сервера:", response.statusText);
                return;
            }

            const data = await response.json();
            updateChannels(data.channels);
            updatePosts(data.posts);
        } catch (error) {
            console.error("Ошибка загрузки данных:", error);
        }
    }

    function updateChannels(channels) {
        if (!channels || channels.length === 0) {
            noChannelsContainer.style.display = "block";
            channelsList.style.display = "none";
            return;
        }

        noChannelsContainer.style.display = "none";
        channelsList.style.display = "block";

        channelsList.innerHTML = "";

        const displayCount = Math.min(channels.length, 2);

        for (let i = 0; i < displayCount; i++) {
            const channel = channels[i];
            const channelElement = createChannelElement(channel);
            channelsList.appendChild(channelElement);
        }
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

    function getRandomColor() {
        const letters = "0123456789ABCDEF";
        let color = "#";
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    function createChannelElement(channel) {
        const channelDiv = document.createElement("div");
        channelDiv.className = "item-card";

        channelDiv.innerHTML = `
      <div class="item-card">
        <div class="item">
          <div class="item-avatar">
            ${
                channel.photo_url
                    ? `<img src="${channel.photo_url}" alt="${channel.name}" class="avatar-img" />`
                    : generateAvatarLetter(channel.name)
            }
          </div>
          <div class="item-details">
            <div class="item-title">${channel.name}</div>
            <div class="item-subtitle">Подписчиков: ${
                channel.subscribers || 0
            }</div>
          </div>
        </div>
      </div>
      `;

        channelDiv.addEventListener("click", () => {
            console.log("Channel clicked:", channel);
        });

        return channelDiv;
    }

    function updatePosts(posts) {
        if (!posts || posts.length === 0) {
            noPostsContainer.style.display = "block";
            postsList.style.display = "none";
            return;
        }

        noPostsContainer.style.display = "none";
        postsList.style.display = "block";

        postsList.innerHTML = "";

        const displayCount = Math.min(posts.length, 2);

        for (let i = 0; i < displayCount; i++) {
            const post = posts[i];
            const postElement = createPostElement(post);
            postsList.appendChild(postElement);
        }
    }

    function createPostElement(post) {
        const postDiv = document.createElement("div");
        postDiv.className = "item-card";

        const formattedDate = formatDate(post.date);

        postDiv.innerHTML = `
      <div class="item-card">
        <div class="item">
          <div class="item-avatar post-icon">
            <span>📄</span>
          </div>
          <div class="item-details" id="${post.id}">
            <div class="item-title">${post.title}</div>
            <div class="item-subtitle">${formattedDate}</div>
          </div>
        </div>
      </div>
    `;

        postDiv.addEventListener("click", () => {
            console.log("Post clicked:", post);
        });

        return postDiv;
    }

    function formatDate(dateString) {
        const date = new Date(dateString);

        if (isNaN(date.getTime())) {
            return dateString;
        }

        const day = date.getDate().toString().padStart(2, "0");
        const month = (date.getMonth() + 1).toString().padStart(2, "0");
        const year = date.getFullYear();
        const hours = date.getHours().toString().padStart(2, "0");
        const minutes = date.getMinutes().toString().padStart(2, "0");

        return `${day}.${month}.${year}, ${hours}:${minutes}`;
    }

    await fetchData();
});
