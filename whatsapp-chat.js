(() => {
  const label = document.querySelector('.floating-whatsapp > .whatsapp-chat-label');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (!label) return;

  let lastNudge = -Infinity;
  label.addEventListener('animationend', () => label.classList.remove('is-scrolling'));
  window.addEventListener('scroll', () => {
    const now = performance.now();
    if (reducedMotion.matches || now - lastNudge < 1800) return;

    lastNudge = now;
    label.classList.add('is-scrolling');
  }, { passive: true });
})();
