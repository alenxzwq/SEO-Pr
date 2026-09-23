// Подземка — немного интерактива

// Мобильное меню
const burger = document.querySelector("[data-burger]");
const nav = document.querySelector("[data-nav]");
if (burger && nav) {
  burger.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    burger.setAttribute("aria-expanded", open);
  });
}

// Обратный отсчёт до конца акции
document.querySelectorAll("[data-countdown]").forEach((el) => {
  const end = new Date(el.dataset.countdown + "T23:59:59");
  const plural = (n, forms) => forms[(n % 10 === 1 && n % 100 !== 11) ? 0 : (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20)) ? 1 : 2];
  const tick = () => {
    const ms = end - new Date();
    if (ms <= 0) { el.textContent = "Акция завершена"; return; }
    const d = Math.floor(ms / 864e5), h = Math.floor(ms / 36e5) % 24, m = Math.floor(ms / 6e4) % 60;
    el.textContent = `Осталось ${d} ${plural(d, ["день", "дня", "дней"])} ${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
  };
  tick();
  setInterval(tick, 30000);
});

// SEO-ПОДСКАЗКА: важный контент НЕ должен появляться только через JS —
// поисковики умеют исполнять JS, но не всегда и не сразу. Здесь JS лишь
// добавляет анимацию, сам текст уже есть в HTML. Проверьте это, отключив JS.

// ---------------------------------------------------------------------------
// Шапка: тень при прокрутке
const header = document.querySelector(".header");
if (header) {
  const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 10);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
}

// Подсветка текущего раздела в меню + закрытие мобильного меню по клику
document.querySelectorAll(".nav__link").forEach((link) => {
  const path = new URL(link.href).pathname;
  if (location.pathname.startsWith(path)) {
    link.classList.add("is-active");
    link.setAttribute("aria-current", "page");
  }
  link.addEventListener("click", () => {
    nav?.classList.remove("is-open");
    burger?.setAttribute("aria-expanded", "false");
  });
});

// Форма заявки: маска телефона и защита от двойной отправки
document.querySelectorAll('input[type="tel"]').forEach((input) => {
  input.addEventListener("input", () => {
    let d = input.value.replace(/\D/g, "");
    if (!d) { input.value = ""; return; }
    if (d[0] === "8") d = "7" + d.slice(1);
    if (d[0] !== "7") d = "7" + d;
    d = d.slice(0, 11);
    const p = [d.slice(1, 4), d.slice(4, 7), d.slice(7, 9), d.slice(9, 11)];
    let out = "+7";
    if (p[0]) out += ` (${p[0]}`;
    if (p[0].length === 3) out += ")";
    if (p[1]) out += ` ${p[1]}`;
    if (p[2]) out += `-${p[2]}`;
    if (p[3]) out += `-${p[3]}`;
    input.value = out;
  });
});
document.querySelectorAll(".booking-form").forEach((form) => {
  form.addEventListener("submit", () => {
    const btn = form.querySelector('button[type="submit"]');
    if (btn) { btn.disabled = true; btn.textContent = "Отправляем…"; }
  });
});

// Калькулятор банкета (страница меню)
const calc = document.querySelector("[data-calc]");
if (calc) {
  const guests = calc.querySelector("[data-calc-guests]");
  const guestsOut = calc.querySelector("[data-calc-guests-out]");
  const drinks = calc.querySelector("[data-calc-drinks]");
  const total = calc.querySelector("[data-calc-total]");
  const link = calc.querySelector("[data-calc-link]");
  const baseHref = link.getAttribute("href");
  const fmt = new Intl.NumberFormat("ru-RU");

  const update = () => {
    const pkg = calc.querySelector('input[name="calc-package"]:checked') || calc.querySelector('input[name="calc-package"]');
    if (!pkg) return;
    pkg.checked = true;
    const n = Number(guests.value);
    const perGuest = Number(pkg.value) + (drinks.checked ? Number(drinks.value) : 0);
    guestsOut.textContent = n;
    total.textContent = `${fmt.format(perGuest * n)} ₽`;
    const comment = `Расчёт с сайта: ${pkg.dataset.name}, ${n} гостей` + (drinks.checked ? ", пакет напитков" : "") + `, ~${fmt.format(perGuest * n)} ₽`;
    link.href = `${baseHref}?guests=${n}&comment=${encodeURIComponent(comment)}`;
  };
  calc.addEventListener("input", update);
  update();
}

// Галерея: просмотр фото на весь экран
const lightboxLinks = [...document.querySelectorAll("[data-lightbox]")];
if (lightboxLinks.length) {
  const box = document.createElement("div");
  box.className = "lightbox";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-modal", "true");
  box.hidden = true;
  box.innerHTML = `
    <button class="lightbox__close" type="button" aria-label="Закрыть">×</button>
    <button class="lightbox__nav lightbox__nav--prev" type="button" aria-label="Предыдущее фото">‹</button>
    <figure class="lightbox__figure"><img alt=""><figcaption class="mono"></figcaption></figure>
    <button class="lightbox__nav lightbox__nav--next" type="button" aria-label="Следующее фото">›</button>`;
  document.body.appendChild(box);
  const img = box.querySelector("img");
  const cap = box.querySelector("figcaption");
  let current = 0;

  const show = (i) => {
    current = (i + lightboxLinks.length) % lightboxLinks.length;
    const a = lightboxLinks[current];
    img.src = a.href;
    img.alt = a.dataset.lightbox;
    cap.textContent = `${a.dataset.lightbox} · ${current + 1} / ${lightboxLinks.length}`;
    box.hidden = false;
    document.body.style.overflow = "hidden";
  };
  const close = () => { box.hidden = true; document.body.style.overflow = ""; };

  lightboxLinks.forEach((a, i) => a.addEventListener("click", (e) => { e.preventDefault(); show(i); }));
  box.querySelector(".lightbox__close").addEventListener("click", close);
  box.querySelector(".lightbox__nav--prev").addEventListener("click", () => show(current - 1));
  box.querySelector(".lightbox__nav--next").addEventListener("click", () => show(current + 1));
  box.addEventListener("click", (e) => { if (e.target === box) close(); });
  document.addEventListener("keydown", (e) => {
    if (box.hidden) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") show(current - 1);
    if (e.key === "ArrowRight") show(current + 1);
  });
}
