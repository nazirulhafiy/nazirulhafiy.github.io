const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

document.querySelectorAll("[data-carousel-module]").forEach((module) => {
  const track = module.querySelector("[data-carousel]");
  const cards = [...module.querySelectorAll("[data-card]")];
  const previousButton = module.querySelector("[data-prev]");
  const nextButton = module.querySelector("[data-next]");
  const currentLabel = module.querySelector("[data-current]");
  const totalLabel = module.querySelector("[data-total]");
  const dotsContainer = module.querySelector("[data-dots]");

  if (!track || !cards.length || !previousButton || !nextButton || !currentLabel || !dotsContainer) {
    return;
  }

  let currentIndex = 0;

  if (totalLabel) {
    totalLabel.textContent = String(cards.length);
  }

  const dots = cards.map((card, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "carousel-dot";
    button.setAttribute("aria-label", `Show card ${index + 1}`);
    button.addEventListener("click", () => goTo(index));
    dotsContainer.append(button);
    return button;
  });

  function update(index) {
    currentIndex = Math.max(0, Math.min(index, cards.length - 1));
    currentLabel.textContent = String(currentIndex + 1);
    previousButton.disabled = currentIndex === 0;
    nextButton.disabled = currentIndex === cards.length - 1;

    dots.forEach((dot, dotIndex) => {
      dot.setAttribute("aria-current", dotIndex === currentIndex ? "true" : "false");
    });
  }

  function goTo(index) {
    const targetIndex = Math.max(0, Math.min(index, cards.length - 1));
    const firstCardLeft = cards[0].offsetLeft;

    track.scrollTo({
      left: cards[targetIndex].offsetLeft - firstCardLeft,
      behavior: reduceMotion.matches ? "auto" : "smooth",
    });
    update(targetIndex);
  }

  previousButton.addEventListener("click", () => goTo(currentIndex - 1));
  nextButton.addEventListener("click", () => goTo(currentIndex + 1));

  track.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      goTo(currentIndex - 1);
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      goTo(currentIndex + 1);
    }
    if (event.key === "Home") {
      event.preventDefault();
      goTo(0);
    }
    if (event.key === "End") {
      event.preventDefault();
      goTo(cards.length - 1);
    }
  });

  let scrollFrame;

  track.addEventListener(
    "scroll",
    () => {
      window.cancelAnimationFrame(scrollFrame);
      scrollFrame = window.requestAnimationFrame(() => {
        const firstCardLeft = cards[0].offsetLeft;
        const maximumScroll = track.scrollWidth - track.clientWidth;

        if (maximumScroll - track.scrollLeft <= 3) {
          update(cards.length - 1);
          return;
        }

        const nearestIndex = cards.reduce((nearest, card, index) => {
          const nearestDistance = Math.abs(
            cards[nearest].offsetLeft - firstCardLeft - track.scrollLeft,
          );
          const cardDistance = Math.abs(card.offsetLeft - firstCardLeft - track.scrollLeft);
          return cardDistance < nearestDistance ? index : nearest;
        }, 0);

        update(nearestIndex);
      });
    },
    { passive: true },
  );

  update(0);
});
