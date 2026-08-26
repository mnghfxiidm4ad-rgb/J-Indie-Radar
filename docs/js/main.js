(function () {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      nav.classList.toggle("is-open");
    });
  }

  const buttons = document.querySelectorAll("[data-filter]");
  const cards = document.querySelectorAll("[data-genres]");
  const empty = document.querySelector(".empty");
  if (!buttons.length) return;

  function applyFilter(filter) {
    buttons.forEach(function (b) {
      b.classList.toggle("is-active", b.getAttribute("data-filter") === filter);
    });
    let shown = 0;
    cards.forEach(function (card) {
      const genres = (card.getAttribute("data-genres") || "").toLowerCase();
      const match = filter === "all" || genres.indexOf(filter.toLowerCase()) !== -1;
      card.style.display = match ? "" : "none";
      if (match) shown += 1;
    });
    if (empty) empty.style.display = shown ? "none" : "block";
  }

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const filter = btn.getAttribute("data-filter");
      applyFilter(filter);
      if (filter && filter !== "all") {
        history.replaceState(null, "", "#" + filter);
      } else {
        history.replaceState(null, "", location.pathname);
      }
    });
  });

  const hash = (location.hash || "").replace("#", "").toLowerCase();
  const known = Array.prototype.map.call(buttons, function (b) {
    return b.getAttribute("data-filter");
  });
  if (hash && known.indexOf(hash) !== -1) applyFilter(hash);
})();
