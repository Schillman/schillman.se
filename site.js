/* One job: reveal sections as they enter the viewport.
   Everything else in the motion system is CSS, so this file failing to load
   costs nothing but the stagger. The .reveal hidden state is gated on the .js
   class in site.css, and .js is set by an inline one liner in each <head>
   before first paint, so with scripting off no content is ever hidden.
   Reduced motion is handled entirely in CSS: this observer still runs and still
   adds .is-in, and the media query pins those elements visible regardless. */
(function () {
  var targets = document.querySelectorAll(".reveal");
  if (!targets.length) return;

  if (!("IntersectionObserver" in window)) {
    for (var i = 0; i < targets.length; i++) targets[i].classList.add("is-in");
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-in");
      io.unobserve(entry.target);
    });
  }, { rootMargin: "0px 0px -12% 0px", threshold: 0.08 });

  targets.forEach(function (el) { io.observe(el); });
})();
