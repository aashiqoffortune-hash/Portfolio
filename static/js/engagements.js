/* Engagements — currency switch.
 *
 * Progressive enhancement only. Both figures are already in the markup as
 * data attributes and the INR one is rendered server-side, so with this file
 * blocked the page keeps a complete price list and every word around it.
 *
 * The choice is remembered per visitor because the currency someone reads in
 * is a property of them, not of the page — a returning reader who switched to
 * USD once should not have to switch again. Storage is wrapped: a private
 * window or blocked site data throws on access rather than returning null.
 */
(function () {
  "use strict";

  var KEY = "salvo.engagements.currency";
  var buttons = document.querySelectorAll(".pk-cur button");
  var prices = document.querySelectorAll(".pk-price");

  if (!buttons.length || !prices.length) return;

  function apply(cur) {
    var attr = "data-" + cur;
    prices.forEach(function (el) {
      var next = el.getAttribute(attr);
      if (next) el.textContent = next;
    });
    buttons.forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-cur") === cur));
    });
  }

  buttons.forEach(function (b) {
    b.addEventListener("click", function () {
      var cur = b.getAttribute("data-cur");
      apply(cur);
      try { localStorage.setItem(KEY, cur); } catch (e) { /* storage blocked */ }
    });
  });

  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* storage blocked */ }
  if (saved === "usd" || saved === "inr") apply(saved);
})();
