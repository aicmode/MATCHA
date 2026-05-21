/* ================================================================
   KISSA MATCHA — Script
================================================================ */

(() => {
  'use strict';

  // ── Nav: scroll effect ──────────────────────────────────────
  const nav = document.getElementById('nav');
  const onScroll = () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ── Nav: mobile toggle ──────────────────────────────────────
  const navToggle  = document.getElementById('navToggle');
  const navDrawer  = document.getElementById('navDrawer');
  const navOverlay = document.getElementById('navOverlay');

  function closeDrawer() {
    navToggle.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
    navDrawer.classList.remove('open');
    navDrawer.setAttribute('aria-hidden', 'true');
    navOverlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  navToggle.addEventListener('click', () => {
    const isOpen = navDrawer.classList.toggle('open');
    navToggle.classList.toggle('open', isOpen);
    navToggle.setAttribute('aria-expanded', String(isOpen));
    navDrawer.setAttribute('aria-hidden', String(!isOpen));
    navOverlay.classList.toggle('open', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  navOverlay.addEventListener('click', closeDrawer);

  document.querySelectorAll('.nav__drawer-link').forEach(link => {
    link.addEventListener('click', closeDrawer);
  });

  // ── Hero: loaded class (subtle zoom-out) ────────────────────
  window.addEventListener('load', () => {
    document.querySelector('.hero')?.classList.add('loaded');
  });

  // ── Reveal on scroll ────────────────────────────────────────
  const revealEls = document.querySelectorAll('.reveal');

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -48px 0px' }
  );

  revealEls.forEach(el => observer.observe(el));

  // ── Active nav link on scroll ───────────────────────────────
  const sections  = document.querySelectorAll('section[id]');
  const navLinks  = document.querySelectorAll('.nav__link');

  const sectionObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          navLinks.forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
          });
        }
      });
    },
    { rootMargin: '-50% 0px -50% 0px' }
  );

  sections.forEach(s => sectionObserver.observe(s));

  // ── Contact form ────────────────────────────────────────────
  const form        = document.getElementById('contactForm');
  const formSuccess = document.getElementById('formSuccess');

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();

      const name  = form.querySelector('#name').value.trim();
      const email = form.querySelector('#email').value.trim();

      if (!name || !email) {
        shakeInvalid(form);
        return;
      }

      // Simulate async send
      const btn = form.querySelector('.btn--primary');
      const originalText = btn.querySelector('.btn__text').textContent;
      btn.querySelector('.btn__text').textContent = 'Sending…';
      btn.disabled = true;

      setTimeout(() => {
        form.style.opacity = '0';
        form.style.transform = 'translateY(-10px)';
        form.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        setTimeout(() => {
          form.style.display = 'none';
          formSuccess.classList.add('visible');
        }, 400);
      }, 1200);
    });
  }

  function shakeInvalid(el) {
    el.style.animation = 'none';
    el.offsetHeight; // reflow
    el.style.animation = 'shake 0.4s ease';
    const style = document.createElement('style');
    style.textContent = `@keyframes shake {
      0%,100%{transform:translateX(0)}
      20%{transform:translateX(-8px)}
      40%{transform:translateX(8px)}
      60%{transform:translateX(-5px)}
      80%{transform:translateX(5px)}
    }`;
    document.head.appendChild(style);
  }

  // ── Gallery: simple lightbox ────────────────────────────────
  const galleryItems = document.querySelectorAll('.gallery__item');

  galleryItems.forEach(item => {
    item.addEventListener('click', () => {
      const img = item.querySelector('img');
      const caption = item.querySelector('.gallery__caption')?.textContent || '';

      const overlay = document.createElement('div');
      overlay.className = 'lightbox';
      overlay.innerHTML = `
        <div class="lightbox__backdrop"></div>
        <div class="lightbox__content">
          <img src="${img.src}" alt="${img.alt}" />
          <p class="lightbox__caption">${caption}</p>
        </div>
        <button class="lightbox__close" aria-label="Close">✕</button>
      `;

      // Inline styles for lightbox
      Object.assign(overlay.style, {
        position: 'fixed', inset: '0',
        zIndex: '200',
        display: 'flex', alignItems: 'center', justifyContent: 'center'
      });

      const backdrop = overlay.querySelector('.lightbox__backdrop');
      Object.assign(backdrop.style, {
        position: 'absolute', inset: '0',
        background: 'rgba(0,0,0,0.92)',
        cursor: 'zoom-out'
      });

      const content = overlay.querySelector('.lightbox__content');
      Object.assign(content.style, {
        position: 'relative', zIndex: '1',
        maxWidth: '90vw', maxHeight: '88vh',
        display: 'flex', flexDirection: 'column',
        gap: '16px', alignItems: 'center'
      });

      const lbImg = overlay.querySelector('.lightbox__content img');
      Object.assign(lbImg.style, {
        maxWidth: '100%', maxHeight: '80vh',
        width: 'auto', height: 'auto',
        objectFit: 'contain',
        animation: 'fadeInUp 0.35s ease'
      });

      const lbCaption = overlay.querySelector('.lightbox__caption');
      Object.assign(lbCaption.style, {
        fontFamily: "'Jost', sans-serif",
        fontSize: '0.7rem', fontWeight: '300',
        letterSpacing: '0.2em', textTransform: 'uppercase',
        color: 'rgba(201,169,110,0.8)'
      });

      const closeBtn = overlay.querySelector('.lightbox__close');
      Object.assign(closeBtn.style, {
        position: 'absolute', top: '24px', right: '28px',
        background: 'none', border: '1px solid rgba(255,255,255,0.2)',
        color: 'rgba(255,255,255,0.7)',
        width: '44px', height: '44px',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        cursor: 'pointer', fontSize: '1rem', zIndex: '2',
        transition: 'border-color 0.25s, color 0.25s'
      });

      const close = () => {
        overlay.style.opacity = '0';
        overlay.style.transition = 'opacity 0.25s ease';
        setTimeout(() => overlay.remove(), 250);
        document.body.style.overflow = '';
      };

      backdrop.addEventListener('click', close);
      closeBtn.addEventListener('click', close);
      document.addEventListener('keydown', (ev) => {
        if (ev.key === 'Escape') close();
      }, { once: true });

      document.body.appendChild(overlay);
      document.body.style.overflow = 'hidden';

      // Fade in
      overlay.style.opacity = '0';
      overlay.style.transition = 'opacity 0.3s ease';
      requestAnimationFrame(() => { overlay.style.opacity = '1'; });
    });
  });

  // ── Smooth scroll for anchors ───────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      const offset = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-h')) || 72;
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });

  // ── Parallax: hero image subtle ─────────────────────────────
  const heroImg = document.querySelector('.hero__img');
  if (heroImg && window.matchMedia('(prefers-reduced-motion: no-preference)').matches) {
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      if (y < window.innerHeight) {
        heroImg.style.transform = `scale(1) translateY(${y * 0.18}px)`;
      }
    }, { passive: true });
  }

})();
