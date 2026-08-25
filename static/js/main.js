/* Progressive enhancement only. The page is complete without this file:
   the rail index is plain anchors, and nothing is hidden until JS decides
   to show it. */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Mobile bar ------------------------------------------------------- */
  var bar = document.querySelector(".bar");
  var btn = bar && bar.querySelector(".bar-btn");

  if (bar && btn) {
    btn.addEventListener("click", function () {
      var open = bar.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    bar.querySelectorAll(".bar-menu a").forEach(function (a) {
      a.addEventListener("click", function () {
        bar.classList.remove("open");
        btn.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* Rail position marker --------------------------------------------- */
  var marks = Array.prototype.slice.call(document.querySelectorAll("[data-sec]"));
  var sections = marks
    .map(function (m) { return document.getElementById(m.dataset.sec); })
    .filter(Boolean);

  if ("IntersectionObserver" in window && sections.length) {
    var spy = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          marks.forEach(function (m) {
            m.classList.toggle("on", m.dataset.sec === e.target.id);
          });
        });
      },
      { rootMargin: "-30% 0px -60% 0px", threshold: 0 }
    );
    sections.forEach(function (s) { spy.observe(s); });
  }

  /* Rise on entry ----------------------------------------------------
     Elements are only hidden once we know we can reveal them, so a
     failure here leaves the page fully readable rather than blank. */
  if (!reduced && "IntersectionObserver" in window) {
    var risers = Array.prototype.slice.call(
      document.querySelectorAll(".s-head, .link, .tool, .duty, .kit, .cred, .minor, .reach, .stats")
    );

    risers.forEach(function (el) { el.classList.add("rise"); });

    var show = function (el, delay) {
      window.setTimeout(function () { el.classList.add("up"); }, delay || 0);
    };

    var io = new IntersectionObserver(
      function (entries, obs) {
        /* Stagger the ones that come into view together, so a list of
           phases resolves in order instead of all at once. */
        var hit = entries.filter(function (e) { return e.isIntersecting; });
        hit.sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; });
        hit.forEach(function (e, i) {
          show(e.target, Math.min(i, 4) * 70);
          obs.unobserve(e.target);
        });
      },
      { rootMargin: "0px 0px -6% 0px", threshold: 0.06 }
    );

    risers.forEach(function (el) { io.observe(el); });

    /* Safety net: anything still hidden after 2.5s is shown regardless,
       so no content can be trapped behind a missed observer callback. */
    window.setTimeout(function () {
      risers.forEach(function (el) { el.classList.add("up"); });
    }, 2500);
  }
})();
