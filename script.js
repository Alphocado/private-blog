(function () {
  const html = document.documentElement;
  const toggle = document.getElementById("theme-toggle");

  // Set tema awal dari localStorage
  const saved = localStorage.getItem("theme") || "light";
  html.setAttribute("data-theme", saved);

  // Toggle klik
  if (toggle) {
    toggle.addEventListener("click", function () {
      const current = html.getAttribute("data-theme");
      const next = current === "light" ? "dark" : "light";
      html.setAttribute("data-theme", next);
      localStorage.setItem("theme", next);
    });
  }
})();
