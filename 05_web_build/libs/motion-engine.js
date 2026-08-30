/**
 * Points & Reality — Minimalist Motion & Interaction Engine
 * Powered by motion.dev (Motion 12.x)
 * 
 * Clean, frictionless animations:
 * - Fluid Hero Word-by-word Reveal
 * - Hardware-accelerated Scroll Progress Bar
 * - Staggered Viewport InView Smooth Entry
 * - Elegant 3D Card Hover Perspective Tilt
 * - Magnetic Physics for Primary CTA Buttons
 * - Dynamic Rolling Numerical Counter
 * - Spring Accordion Transitions
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports'], factory);
  } else if (typeof exports === 'object' && typeof exports.nodeName !== 'string') {
    factory(exports);
  } else {
    factory((root.PointsRealityMotion = {}));
  }
}(typeof self !== 'undefined' ? self : this, function (exports) {
  'use strict';

  const Motion = window.Motion || {};

  /**
   * 1. Hero Stagger Entrance Animation
   */
  function initHeroStagger() {
    if (!Motion.animate) return;

    // Eyebrow badge entrance
    const eyebrow = document.querySelector('.eyebrow, .page-eyebrow');
    if (eyebrow) {
      Motion.animate(
        eyebrow,
        { opacity: [0, 1], y: [16, 0] },
        { duration: 0.5, ease: [0.16, 1, 0.3, 1] }
      );
    }

    // Hero title word animation
    const heroTitle = document.querySelector('.hero-title, .page-title');
    if (heroTitle && !heroTitle.dataset.animated) {
      heroTitle.dataset.animated = 'true';
      const nodes = Array.from(heroTitle.childNodes);
      heroTitle.innerHTML = '';
      nodes.forEach(node => {
        if (node.nodeType === 3) {
          const words = node.textContent.split(' ');
          words.forEach((word, i) => {
            if (word.trim()) {
              const span = document.createElement('span');
              span.className = 'hero-word';
              span.style.display = 'inline-block';
              span.textContent = word;
              heroTitle.appendChild(span);
              if (i < words.length - 1) heroTitle.appendChild(document.createTextNode(' '));
            }
          });
        } else {
          heroTitle.appendChild(node);
        }
      });

      const words = heroTitle.querySelectorAll('.hero-word, .gradient-text, em');
      if (words.length > 0) {
        Motion.animate(
          words,
          { opacity: [0, 1], y: [24, 0] },
          { delay: Motion.stagger(0.04, { start: 0.1 }), duration: 0.65, ease: [0.16, 1, 0.3, 1] }
        );
      }
    }

    // Hero description & CTA
    const heroDesc = document.querySelector('.section-desc, .page-desc');
    if (heroDesc) {
      Motion.animate(
        heroDesc,
        { opacity: [0, 1], y: [16, 0] },
        { delay: 0.2, duration: 0.6, ease: [0.16, 1, 0.3, 1] }
      );
    }

    const ctaGroup = document.querySelector('.hero-cta-group, .stage-controls');
    if (ctaGroup) {
      Motion.animate(
        ctaGroup.children,
        { opacity: [0, 1], y: [16, 0] },
        { delay: Motion.stagger(0.06, { start: 0.3 }), duration: 0.55, ease: [0.16, 1, 0.3, 1] }
      );
    }

    // 3D Stage Card entrance
    const stageCard = document.querySelector('#hero-stage, .stage-section');
    if (stageCard) {
      Motion.animate(
        stageCard,
        { opacity: [0, 1], y: [30, 0] },
        { delay: 0.35, duration: 0.75, ease: [0.16, 1, 0.3, 1] }
      );
    }
  }

  /**
   * 2. Scroll Progress Bar
   */
  function initScrollProgress(barSelector = '#scroll-progress') {
    const bar = document.querySelector(barSelector);
    if (!bar) return;

    if (Motion.scroll && Motion.animate) {
      Motion.scroll(
        Motion.animate(bar, { width: ['0%', '100%'] }, { ease: 'linear' })
      );
    } else {
      window.addEventListener('scroll', () => {
        const total = document.documentElement.scrollHeight - window.innerHeight;
        if (total > 0) {
          bar.style.width = ((window.scrollY / total) * 100) + '%';
        }
      }, { passive: true });
    }
  }

  /**
   * 3. Viewport InView Smooth Reveals
   */
  function initViewportReveals(selector = '.reveal-on-scroll') {
    const elements = document.querySelectorAll(selector);
    if (elements.length === 0) return;

    if (Motion.inView && Motion.animate) {
      Motion.inView(selector, (info) => {
        const el = info.target;
        let delay = 0;
        for (let i = 1; i <= 6; i++) {
          if (el.classList.contains(`stagger-${i}`)) {
            delay = i * 0.06;
            break;
          }
        }

        Motion.animate(
          el,
          { opacity: [0, 1], y: [24, 0] },
          { duration: 0.65, delay: delay, ease: [0.16, 1, 0.3, 1] }
        );
        el.classList.add('is-revealed');
      }, { amount: 0.1 });
    } else {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-revealed');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1 });

      elements.forEach(el => observer.observe(el));
    }
  }

  /**
   * 4. Elegant 3D Card Hover Perspective Tilt
   */
  function init3DCardTilt(selector = '.glow-border-card, .bento-card, .archive-card, .asset-card, .stat-box') {
    if (window.matchMedia && !window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      return;
    }

    const cards = document.querySelectorAll(selector);
    cards.forEach(card => {
      let bounds = null;

      function updateBounds() {
        bounds = card.getBoundingClientRect();
      }

      card.addEventListener('mouseenter', updateBounds);

      card.addEventListener('mousemove', (e) => {
        if (!bounds) updateBounds();
        const mouseX = e.clientX - bounds.left;
        const mouseY = e.clientY - bounds.top;

        const normX = (mouseX / bounds.width) * 2 - 1;
        const normY = (mouseY / bounds.height) * 2 - 1;

        const maxTilt = 4.5;
        const rotX = -normY * maxTilt;
        const rotY = normX * maxTilt;

        if (Motion.animate) {
          Motion.animate(
            card,
            {
              transform: `perspective(900px) rotateX(${rotX.toFixed(2)}deg) rotateY(${rotY.toFixed(2)}deg) translateY(-4px)`
            },
            { duration: 0.12, ease: 'easeOut' }
          );
        } else {
          card.style.transform = `perspective(900px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateY(-4px)`;
        }
      });

      card.addEventListener('mouseleave', () => {
        bounds = null;
        if (Motion.animate) {
          Motion.animate(
            card,
            {
              transform: 'perspective(900px) rotateX(0deg) rotateY(0deg) translateY(0px)'
            },
            { duration: 0.45, ease: [0.16, 1, 0.3, 1] }
          );
        } else {
          card.style.transform = 'none';
        }
      });
    });
  }

  /**
   * 5. Magnetic Physics for CTA & Navigation
   */
  function initMagneticButtons(selector = '.btn, .model-pill, .filter-pill, .lang-btn') {
    if (window.matchMedia && !window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      return;
    }

    const buttons = document.querySelectorAll(selector);
    buttons.forEach(btn => {
      btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const relX = e.clientX - (rect.left + rect.width / 2);
        const relY = e.clientY - (rect.top + rect.height / 2);

        const transX = relX * 0.2;
        const transY = relY * 0.2;

        if (Motion.animate) {
          Motion.animate(btn, { x: transX, y: transY }, { duration: 0.12, ease: 'easeOut' });
        } else {
          btn.style.transform = `translate(${transX}px, ${transY}px)`;
        }
      });

      btn.addEventListener('mouseleave', () => {
        if (Motion.animate) {
          Motion.animate(btn, { x: 0, y: 0 }, { duration: 0.4, ease: [0.34, 1.56, 0.64, 1] });
        } else {
          btn.style.transform = 'translate(0px, 0px)';
        }
      });
    });
  }

  /**
   * 6. Smooth Numerical Rolling Counter
   */
  const activeCounters = new Map();

  function animateNumber(element, startVal, endVal, prefix = '', suffix = '', duration = 0.45) {
    if (!element) return;
    const key = element;

    if (activeCounters.has(key)) {
      const prevAnim = activeCounters.get(key);
      if (prevAnim && typeof prevAnim.stop === 'function') prevAnim.stop();
    }

    if (Motion.animate) {
      const anim = Motion.animate(startVal, endVal, {
        duration: duration,
        ease: [0.16, 1, 0.3, 1],
        onUpdate: (latest) => {
          const formatted = Math.round(latest).toLocaleString();
          element.textContent = `${prefix}${formatted}${suffix}`;
        }
      });
      activeCounters.set(key, anim);
    } else {
      element.textContent = `${prefix}${Math.round(endVal).toLocaleString()}${suffix}`;
    }
  }

  /**
   * 7. Smooth Stage Viewport Transition
   */
  function transitionStage(iframe, newSrc, onComplete) {
    if (!iframe) return;

    if (Motion.animate) {
      Motion.animate(
        iframe,
        { opacity: [1, 0.2] },
        { duration: 0.15, ease: 'easeIn' }
      ).then(() => {
        iframe.src = newSrc;
        iframe.onload = () => {
          Motion.animate(
            iframe,
            { opacity: [0.2, 1] },
            { duration: 0.3, ease: [0.16, 1, 0.3, 1] }
          );
          if (onComplete) onComplete();
        };
      });
    } else {
      iframe.src = newSrc;
      if (onComplete) onComplete();
    }
  }

  /**
   * 8. FAQ Accordion
   */
  function toggleAccordion(itemElement) {
    if (!itemElement) return;
    const answer = itemElement.querySelector('.faq-answer');
    const icon = itemElement.querySelector('.faq-icon');
    const isOpen = itemElement.classList.contains('open');

    if (isOpen) {
      if (Motion.animate && answer) {
        Motion.animate(answer, { height: [answer.scrollHeight + 'px', '0px'], opacity: [1, 0] }, { duration: 0.25, ease: 'easeInOut' })
          .then(() => {
            itemElement.classList.remove('open');
            answer.style.height = '';
          });
      } else {
        itemElement.classList.remove('open');
      }

      if (Motion.animate && icon) {
        Motion.animate(icon, { rotate: [45, 0] }, { duration: 0.2, ease: [0.34, 1.56, 0.64, 1] });
      }
    } else {
      itemElement.classList.add('open');
      if (Motion.animate && answer) {
        const targetHeight = answer.scrollHeight;
        Motion.animate(answer, { height: ['0px', targetHeight + 'px'], opacity: [0, 1] }, { duration: 0.3, ease: [0.16, 1, 0.3, 1] })
          .then(() => {
            answer.style.height = 'auto';
          });
      }

      if (Motion.animate && icon) {
        Motion.animate(icon, { rotate: [0, 45] }, { duration: 0.25, ease: [0.34, 1.56, 0.64, 1] });
      }
    }
  }

  /**
   * 9. Ultra-Smooth Hardware-Accelerated Scroll Video Scrubber
   * - Maps page scroll progress (0~100%) to video duration
   * - Uses rAF + Lerp damping to eliminate seek bottlenecks and enable silky forward/reverse playback
   * - Auto-sleeps when idle to save battery and GPU cycles
   * - Provides pause/resume API when heavy 3DGS WebGL stages are active
   */
  function initScrollVideoScrubber(videoSelector = '.video-bg', options = {}) {
    const video = typeof videoSelector === 'string' ? document.querySelector(videoSelector) : videoSelector;
    if (!video) return null;

    // Prevent native auto-loop conflict
    video.pause();
    video.removeAttribute('autoplay');
    video.removeAttribute('loop');

    let targetTime = 0;
    let currentTime = 0;
    let isRunning = false;
    let isPaused = false;
    let rafId = null;
    const lerpFactor = options.lerp || 0.12;
    const minDelta = 0.015;

    function calculateTargetTime() {
      if (!video.duration || isNaN(video.duration)) return;
      const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      const scrollProgress = Math.min(1, Math.max(0, window.scrollY / maxScroll));
      targetTime = scrollProgress * video.duration;
    }

    function update() {
      if (isPaused) {
        isRunning = false;
        return;
      }

      const delta = targetTime - currentTime;
      if (Math.abs(delta) > minDelta) {
        currentTime += delta * lerpFactor;
        if (typeof video.fastSeek === 'function') {
          video.fastSeek(currentTime);
        } else {
          video.currentTime = currentTime;
        }
        rafId = requestAnimationFrame(update);
      } else {
        currentTime = targetTime;
        if (Math.abs(video.currentTime - currentTime) > 0.01) {
          video.currentTime = currentTime;
        }
        isRunning = false;
      }
    }

    function onScroll() {
      if (isPaused) return;
      calculateTargetTime();
      if (!isRunning) {
        isRunning = true;
        rafId = requestAnimationFrame(update);
      }
    }

    if (video.readyState >= 1) {
      calculateTargetTime();
    } else {
      video.addEventListener('loadedmetadata', calculateTargetTime, { once: true });
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', calculateTargetTime, { passive: true });

    return {
      pause: () => {
        isPaused = true;
        if (rafId) cancelAnimationFrame(rafId);
        isRunning = false;
      },
      resume: () => {
        if (!isPaused) return;
        isPaused = false;
        onScroll();
      },
      destroy: () => {
        isPaused = true;
        if (rafId) cancelAnimationFrame(rafId);
        window.removeEventListener('scroll', onScroll);
        window.removeEventListener('resize', calculateTargetTime);
      }
    };
  }

  /**
   * 10. Ultra-Silky Canvas Image Sequence Scrubber (Apple-Style 60+ FPS)
   * - Preloads WebP image sequence into memory
   * - Eliminates hardware video decoder seek latency completely (0.0ms drawImage)
   * - Flawless forward and reverse scrubbing on scroll
   * - Aspect-ratio cover rendering on HTML5 canvas
   */
  function initScrollCanvasSequence(canvasSelector = '#video-canvas', options = {}) {
    const canvas = typeof canvasSelector === 'string' ? document.querySelector(canvasSelector) : canvasSelector;
    if (!canvas) return null;
    const ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) return null;

    const frameCount = options.frameCount || 93;
    const getPath = options.framePath || ((i) => `assets/hero-sequence/frame_${String(i).padStart(3, '0')}.webp`);
    const lerpFactor = options.lerp || 0.18;

    const images = new Array(frameCount);
    let loadedCount = 0;
    let isPaused = false;
    let isRunning = false;
    let targetFrame = 1;
    let currentFrame = 1;
    let rafId = null;

    function resizeCanvas() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      renderCurrentFrame();
    }

    function renderCurrentFrame() {
      const idx = Math.min(frameCount, Math.max(1, Math.round(currentFrame)));
      const img = images[idx - 1];
      if (!img || !img.complete || img.naturalWidth === 0) return;

      const cw = canvas.width;
      const ch = canvas.height;
      const iw = img.naturalWidth;
      const ih = img.naturalHeight;

      // Cover calculation
      const hRatio = cw / iw;
      const vRatio = ch / ih;
      const ratio = Math.max(hRatio, vRatio);
      const nw = iw * ratio;
      const nh = ih * ratio;
      const nx = (cw - nw) / 2;
      const ny = (ch - nh) / 2;

      ctx.drawImage(img, nx, ny, nw, nh);
    }

    function update() {
      if (isPaused) {
        isRunning = false;
        return;
      }

      const delta = targetFrame - currentFrame;
      if (Math.abs(delta) > 0.06) {
        currentFrame += delta * lerpFactor;
        renderCurrentFrame();
        rafId = requestAnimationFrame(update);
      } else {
        currentFrame = targetFrame;
        renderCurrentFrame();
        isRunning = false;
      }
    }

    function onScroll() {
      if (isPaused) return;
      const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      const scrollProgress = Math.min(1, Math.max(0, window.scrollY / maxScroll));
      targetFrame = 1 + scrollProgress * (frameCount - 1);

      if (!isRunning) {
        isRunning = true;
        rafId = requestAnimationFrame(update);
      }
    }

    // Preload images
    for (let i = 1; i <= frameCount; i++) {
      const img = new Image();
      img.src = getPath(i);
      img.onload = () => {
        loadedCount++;
        if (i === 1 || (loadedCount === 1 && currentFrame === 1)) {
          renderCurrentFrame();
        }
      };
      images[i - 1] = img;
    }

    window.addEventListener('resize', resizeCanvas, { passive: true });
    window.addEventListener('scroll', onScroll, { passive: true });
    resizeCanvas();

    return {
      pause: () => {
        isPaused = true;
        if (rafId) cancelAnimationFrame(rafId);
        isRunning = false;
      },
      resume: () => {
        if (!isPaused) return;
        isPaused = false;
        onScroll();
      },
      destroy: () => {
        isPaused = true;
        if (rafId) cancelAnimationFrame(rafId);
        window.removeEventListener('scroll', onScroll);
        window.removeEventListener('resize', resizeCanvas);
      }
    };
  }

  // Export public API
  exports.initHeroStagger = initHeroStagger;
  exports.initScrollProgress = initScrollProgress;
  exports.initViewportReveals = initViewportReveals;
  exports.init3DCardTilt = init3DCardTilt;
  exports.initMagneticButtons = initMagneticButtons;
  exports.animateNumber = animateNumber;
  exports.transitionStage = transitionStage;
  exports.toggleAccordion = toggleAccordion;
  exports.initScrollVideoScrubber = initScrollVideoScrubber;
  exports.initScrollCanvasSequence = initScrollCanvasSequence;

  // Auto-init
  if (typeof document !== 'undefined') {
    const init = () => {
      initHeroStagger();
      initScrollProgress();
      initViewportReveals();
      init3DCardTilt();
      initMagneticButtons();
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  }
}));
