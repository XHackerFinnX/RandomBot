document.addEventListener("DOMContentLoaded", () => {
  // Инициализируем слайдеры для каждого экрана
  initializeSlider("giveaways-slider", "slider-indicators") // Main screen
  initializeSlider("giveaways-slider-success", "slider-indicators-success") // Success screen
  initializeSlider("giveaways-slider-true", "slider-indicators-true") // Success true screen

  function initializeSlider(sliderId, indicatorsId) {
    const slider = document.getElementById(sliderId)
    const indicatorsContainer = document.getElementById(indicatorsId)

    if (!slider || !indicatorsContainer) return

    const indicators = indicatorsContainer.querySelectorAll(".indicator")
    const slides = slider.children
    let currentSlide = 0
    let isTransitioning = false

    // Отключаем нативный scroll-snap для лучшего контроля
    slider.style.scrollSnapType = "none"

    // Функция для обновления активного индикатора
    function updateIndicators() {
      indicators.forEach((indicator, index) => {
        indicator.classList.toggle("active", index === currentSlide)
      })
    }

    // Функция для перехода к слайду
    function goToSlide(index, smooth = true) {
      if (isTransitioning || index < 0 || index >= slides.length) return

      isTransitioning = true
      const slideWidth = slider.offsetWidth

      slider.scrollTo({
        left: slideWidth * index,
        behavior: smooth ? "smooth" : "auto",
      })

      currentSlide = index
      updateIndicators()

      // Разблокируем переходы через небольшую задержку
      setTimeout(() => {
        isTransitioning = false
      }, 300)
    }

    // Обработчики для индикаторов
    indicators.forEach((indicator, index) => {
      indicator.addEventListener("click", () => {
        goToSlide(index)
      })
    })

    // Улучшенная обработка touch событий
    let touchStartX = 0
    let touchStartY = 0
    let touchEndX = 0
    let touchEndY = 0
    let isSwiping = false

    slider.addEventListener(
      "touchstart",
      (e) => {
        if (isTransitioning) return

        touchStartX = e.touches[0].clientX
        touchStartY = e.touches[0].clientY
        isSwiping = true
      },
      { passive: true },
    )

    slider.addEventListener(
      "touchmove",
      (e) => {
        if (!isSwiping || isTransitioning) return

        touchEndX = e.touches[0].clientX
        touchEndY = e.touches[0].clientY

        // Определяем направление свайпа
        const deltaX = Math.abs(touchEndX - touchStartX)
        const deltaY = Math.abs(touchEndY - touchStartY)

        // Если горизонтальный свайп преобладает, предотвращаем вертикальный скролл
        if (deltaX > deltaY && deltaX > 10) {
          e.preventDefault()
        }
      },
      { passive: false },
    )

    slider.addEventListener(
      "touchend",
      (e) => {
        if (!isSwiping || isTransitioning) return

        isSwiping = false

        const deltaX = touchStartX - touchEndX
        const deltaY = Math.abs(touchStartY - touchEndY)
        const minSwipeDistance = 50

        // Проверяем, что это горизонтальный свайп
        if (Math.abs(deltaX) > minSwipeDistance && Math.abs(deltaX) > deltaY) {
          if (deltaX > 0) {
            // Свайп влево - следующий слайд
            goToSlide(currentSlide + 1)
          } else {
            // Свайп вправо - предыдущий слайд
            goToSlide(currentSlide - 1)
          }
        }
      },
      { passive: true },
    )

    // Обработка изменения размера окна
    let resizeTimeout
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimeout)
      resizeTimeout = setTimeout(() => {
        goToSlide(currentSlide, false)
      }, 100)
    })

    // Обработчики кнопок участия для этого слайдера
    slider.querySelectorAll(".participate-btn").forEach((btn) => {
      btn.addEventListener("click", function (e) {
        e.preventDefault()
        e.stopPropagation()

        // Предотвращаем случайные клики во время свайпа
        if (isTransitioning) return

        console.log(`Участие в розыгрыше из слайдера ${sliderId}`)

        // Анимация нажатия
        this.style.transform = "scale(0.95)"
        setTimeout(() => {
          this.style.transform = ""
        }, 150)
      })
    })

    // Инициализация
    updateIndicators()
  }
})
