/* Shared behaviour for the vivisection lab pages.
   Dark is the default (matches the original Gemma page); toggle persists. */
(function () {
  var KEY = "vivisection-theme";
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  // default dark unless the user explicitly chose light
  if (saved === "light") document.body.classList.remove("dark");
  else document.body.classList.add("dark");

  function label(btn) {
    var dark = document.body.classList.contains("dark");
    btn.textContent = dark ? "☼ Light" : "☾ Dark";
    btn.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
  }

  function wire() {
    document.querySelectorAll(".theme-btn").forEach(function (btn) {
      label(btn);
      btn.addEventListener("click", function () {
        document.body.classList.toggle("dark");
        try { localStorage.setItem(KEY, document.body.classList.contains("dark") ? "dark" : "light"); } catch (e) {}
        document.querySelectorAll(".theme-btn").forEach(label);
      });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", wire);
  else wire();
})();
