/* Light/dark, remembered.
 *
 * Loaded from <head> WITHOUT defer, on purpose. It has to set the attribute
 * before the first paint: deferred, a reader who chose dark gets a flash of the
 * full-brightness page first, which on a site built for sensory needs is the one
 * bug worst worth having. It is small enough that the blocking cost is noise.
 *
 * The system preference is the default and is handled in CSS. This only stores a
 * deliberate override, so someone who never touches the toggle keeps following
 * their OS — including when it changes at sunset.
 */
(function () {
  var KEY = "pp-theme";

  function stored() {
    try {
      var v = localStorage.getItem(KEY);
      return v === "light" || v === "dark" ? v : null;
    } catch (e) {
      /* Safari in private mode throws on localStorage. A reader who cannot be
       * remembered should still get a working toggle for this page. */
      return null;
    }
  }

  function systemIsDark() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function apply(theme) {
    if (theme) document.documentElement.setAttribute("data-theme", theme);
    else document.documentElement.removeAttribute("data-theme");
  }

  apply(stored());

  function label(btn) {
    var dark = (document.documentElement.getAttribute("data-theme") || (systemIsDark() ? "dark" : "light")) === "dark";
    btn.setAttribute("aria-pressed", String(dark));
    btn.title = dark ? "Switch to light" : "Switch to dark";
    btn.querySelector(".theme-icon").textContent = dark ? "☾" : "☀";
    btn.querySelector(".theme-text").textContent = dark ? "Dark" : "Light";
  }

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.hidden = false;
    label(btn);
    btn.addEventListener("click", function () {
      var nowDark = (document.documentElement.getAttribute("data-theme") || (systemIsDark() ? "dark" : "light")) === "dark";
      var next = nowDark ? "light" : "dark";
      apply(next);
      try { localStorage.setItem(KEY, next); } catch (e) {}
      label(btn);
    });

    /* If the reader has no stored choice, follow the system when it changes. */
    if (window.matchMedia) {
      window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
        if (!stored()) label(btn);
      });
    }
  });

  /* The service worker, registered from here because this is the only script on
   * all seven pages — penguin-pebbling.js is the game and lives on one of them.
   *
   * On `load` rather than immediately: this file runs from <head> without defer
   * so the theme lands before the first paint, and registering a worker in that
   * window would compete with the thing it is there to protect. Nothing about
   * the site needs the worker to be early.
   *
   * Over file:// there is no service worker and no error worth showing. */
  if ("serviceWorker" in navigator && location.protocol !== "file:") {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/sw.js").catch(function () {
        /* Offline support is an enhancement; the site works without it. */
      });
    });
  }
})();
