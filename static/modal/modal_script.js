const modalOverlay = document.getElementById('modalOverlay');
const openModalBtn = document.getElementById('openModalBtn');
const addPostBtn = document.getElementById('addPostBtn');
const closeModalBtn = document.getElementById('closeModalBtn');
const channelModalOverlay = document.getElementById('channelModalOverlay');
const openModalBtnChannel = document.getElementById('openModalBtnChannel');
const addChannelBtn = document.getElementById('addChannelBtn');
const closeChannelModalBtn = document.getElementById('closeChannelModalBtn');
const postsList = document.getElementById('posts-list');
const noPostsContainer = document.getElementById('no-posts-container');
const viewAllPosts = document.getElementById('view-all-posts');
const channelsList = document.getElementById('channels-list');
const noChannelsContainer = document.getElementById('no-channels-container');
const viewAllChannels = document.getElementById('view-all-channels');

function initUI() {
  if (postsList && postsList.children.length === 0) {
    noPostsContainer.classList.remove('hidden');
  } else {
    noPostsContainer.classList.add('hidden');
  }

  if (channelsList && channelsList.children.length === 0) {
    noChannelsContainer.classList.remove('hidden');
  } else {
    noChannelsContainer.classList.add('hidden');
  }
}

async function updateChannel(channelId, userId) {
  try {
    const response = await fetch(`/api/update-channel?user_id=${userId}&channelid=${channelId}`, {
      method: 'POST',
    });

    if (response.ok) {
      window.location.reload(); // Обновляем страницу
    } else {
      console.error('Ошибка обновления канала');
    }
  } catch (error) {
    console.error('Ошибка сети:', error);
  }
}

async function deleteChannel(channelId, userId) {
  try {
    const response = await fetch(`/api/delete-channel?user_id=${userId}&channelid=${channelId}`, {
      method: 'POST',
    });

    if (response.ok) {
      window.location.reload(); // Обновляем страницу
    } else {
      console.error('Ошибка удаления канала');
    }
  } catch (error) {
    console.error('Ошибка сети:', error);
  }
}

// Функция для удаления поста
async function deletePost(postId, userId) {
  try {
    const response = await fetch(`/api/delete-post?user_id=${userId}&postid=${postId}`, {
      method: 'POST',
    });

    if (response.ok) {
      window.location.reload(); // Обновляем страницу
    } else {
      console.error('Ошибка удаления поста');
    }
  } catch (error) {
    console.error('Ошибка сети:', error);
  }
}

// Функция для просмотра поста
async function viewPost(postId, userId) {
  try {
    const response = await fetch(`/api/view-post?user_id=${userId}&postid=${postId}`, {
      method: 'POST',
    });

    if (response.ok) {
      console.log('Пост просмотрен');
      window.location.reload();
    } else {
      console.error('Ошибка при просмотре поста');
    }
  } catch (error) {
    console.error('Ошибка сети:', error);
  }
}


function openPostsModal() {
  loadPostsToModal().then(() => {
    modalOverlay.classList.add('animate-fade-in');
    modalOverlay.querySelector('.modal-container').classList.add('animate-slide-up');
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
    })

    const posts = await response.json();

    const postsList = document.getElementById('modalPostsList');
    const noPostsMessage = document.getElementById('noPostsMessage');
    const postsListContainer = document.getElementById('postsListContainer');

    postsList.innerHTML = '';

    if (posts.length > 0) {
      postsListContainer.classList.remove('hidden');
      noPostsMessage.classList.add('hidden');

      const modalContent = document.querySelector('.modal-content');
      if (modalContent) {
        modalContent.style.flexGrow = '0';
      }

      const addButtonContainer = document.querySelector('.add-button-container');
      if (addButtonContainer) {
        addButtonContainer.style.display = 'block';
      }

      posts.forEach(post => {
        const postElement = createPostElement(post);
        postsList.appendChild(postElement);
      });
    } else {
      postsListContainer.classList.add('hidden');
      noPostsMessage.classList.remove('hidden');
    }
  } catch (error) {
    console.error('Ошибка загрузки постов:', error);
  }
}

function createPostElement(post) {
  const postElement = document.createElement('div');
  postElement.className = 'post-item';
  postElement.innerHTML = `
    <div class="post-content" id="${post.id}">
      <div class="post-details">
        <h3 class="post-title">${post.title}</h3>
      </div>
      <div class="post-actions">
        <button class="action-button view-button" title="Просмотреть">
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>
        </button>

        <button class="action-button delete-button" title="Удалить">
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            <line x1="10" y1="11" x2="10" y2="17"></line>
            <line x1="14" y1="11" x2="14" y2="17"></line>
          </svg>
        </button>
      </div>
    </div>
  `;

  // Добавьте обработчики событий для кнопок
  postElement.querySelector('.delete-button').addEventListener('click', () => deletePost(post.id, post.user_id));
  postElement.querySelector('.view-button').addEventListener('click', () => viewPost(post.id, post.user_id));

  return postElement;
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
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

function createChannelElement(channel) {
  const channelElement = document.createElement('div');
  channelElement.className = 'channel-item';
  console.log(channel)
  console.log(channel.verified)
  const statusIcon = channel.verified
    ? `<svg class="status-verified" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`
    : `<svg class="status-not-verified" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;

  channelElement.innerHTML = `
    <div class="channel-content">
      <div class="channel-avatar">
        ${channel.photo_url ? `<img src="${channel.photo_url}" alt="${channel.name}" class="channel-avatar-img">` : generateAvatarLetter(channel.name)}
      </div>
      <div class="channel-info">
        <div class="channel-name-container">
          <h3 class="channel-name">${channel.name}</h3>
          <div class="channel-status">
            ${statusIcon}
          </div>
        </div>
        <p class="channel-subscribers">Подписчиков: ${channel.subscribers || 0}</p>
      </div>
    </div>
    <div class="channel-actions">
      <button class="channel-button update-btn" data-id="${channel.id}" aria-label="Обновить">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path>
          <path d="M3 3v5h5"></path>
          <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"></path>
          <path d="M16 16h5v5"></path>
        </svg>
      </button>
      <button class="channel-button delete-btn" data-id="${channel.id}" aria-label="Удалить">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          <line x1="10" y1="11" x2="10" y2="17"></line>
          <line x1="14" y1="11" x2="14" y2="17"></line>
        </svg>
      </button>
    </div>
  `;

  // Add event listeners using the correct selectors
  const updateBtn = channelElement.querySelector('.update-btn');
  if (updateBtn) {
    updateBtn.addEventListener('click', () => updateChannel(channel.id, channel.user_id));
  }

  const deleteBtn = channelElement.querySelector('.delete-btn');
  if (deleteBtn) {
    deleteBtn.addEventListener('click', () => deleteChannel(channel.id, channel.user_id));
  }

  return channelElement;
}

async function loadChannelsToModal() {
  const tg = window.Telegram?.WebApp;
  const userId = tg?.initDataUnsafe?.user?.id;

  if (!userId) {
    console.error("Не удалось получить ID пользователя.");
    return;
  }

  try {
    const response = await fetch("/api/get_channel/all", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId }),
    });

    if (!response.ok) {
      console.error("Ошибка ответа от сервера:", response.statusText);
      return;
    }

    const channels = await response.json();

    const channelsList = document.getElementById('modalChannelList');
    const noChannelMessage = document.getElementById('noChannelMessage');
    const channelListContainer = document.getElementById('channelListContainer');

    channelsList.innerHTML = '';

    if (channels.length > 0) {
      channelListContainer.classList.remove('hidden');
      noChannelMessage.classList.add('hidden');

      const modalContent = document.querySelector('.modal-content-channel');
      if (modalContent) {
        modalContent.style.flexGrow = '0';
      }

      const addButtonContainer = document.querySelector('.add-button-container-channel');
      if (addButtonContainer) {
        addButtonContainer.style.display = 'block';
      }

      channels.forEach(channel => {
        const channelElement = createChannelElement(channel);
        channelsList.appendChild(channelElement);
      });
    } else {
      channelListContainer.classList.add('hidden');
      noChannelMessage.classList.remove('hidden');
    }
  } catch (error) {
    console.error('Ошибка загрузки каналов:', error);
  }
}

function openChannelsModal() {
  loadChannelsToModal().then(() => {
    if (channelModalOverlay) {
      channelModalOverlay.classList.add('animate-fade-in');
      channelModalOverlay.querySelector('.modal-container').classList.add('animate-slide-up');
    }
  });
}

function closeModal(modalElement) {
  if (modalElement) {
    modalElement.classList.remove('animate-fade-in');
    modalElement.classList.add('animate-fade-out');
    modalElement.querySelector('.modal-container').classList.remove('animate-slide-up');
    modalElement.querySelector('.modal-container').classList.add('animate-slide-down');

    setTimeout(function () {
      modalElement.classList.remove('animate-fade-out');
      modalElement.querySelector('.modal-container').classList.remove('animate-slide-down');
    }, 300);
  }
}

if (openModalBtn) {
  openModalBtn.addEventListener('click', openPostsModal);
}

if (addPostBtn) {
  addPostBtn.addEventListener('click', openPostsModal);
}

if (closeModalBtn) {
  closeModalBtn.addEventListener('click', function () {
    closeModal(modalOverlay);
  });
}

if (modalOverlay) {
  modalOverlay.addEventListener('click', function (e) {
    if (e.target === modalOverlay) {
      closeModal(modalOverlay);
    }
  });
}

if (openModalBtnChannel) {
  openModalBtnChannel.addEventListener('click', openChannelsModal);
}

if (addChannelBtn) {
  addChannelBtn.addEventListener('click', openChannelsModal);
}

if (closeChannelModalBtn) {
  closeChannelModalBtn.addEventListener('click', function () {
    closeModal(channelModalOverlay);
  });
}

if (channelModalOverlay) {
  channelModalOverlay.addEventListener('click', function (e) {
    if (e.target === channelModalOverlay) {
      closeModal(channelModalOverlay);
    }
  });
}

document.addEventListener('DOMContentLoaded', initUI);

if (viewAllPosts) {
  viewAllPosts.addEventListener('click', openPostsModal);
}

if (viewAllChannels) {
  viewAllChannels.addEventListener('click', openChannelsModal);
}