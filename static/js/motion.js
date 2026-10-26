// GUDLFT — small progressive enhancements. Every page works without this file.
(function () {
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Count up the last number of a text, e.g. "Points available: 13"
    document.querySelectorAll('[data-countup]').forEach(function (el) {
        var match = el.textContent.match(/^([\s\S]*?)(-?\d+)(\s*)$/);
        if (!match || reduceMotion) return;
        var prefix = match[1], target = parseInt(match[2], 10), suffix = match[3];
        var duration = 900, start = null;
        function frame(now) {
            if (start === null) start = now;
            var t = Math.min((now - start) / duration, 1);
            var eased = 1 - Math.pow(1 - t, 3);
            el.textContent = prefix + Math.round(target * eased) + suffix;
            if (t < 1) requestAnimationFrame(frame);
        }
        el.textContent = prefix + '0' + suffix;
        requestAnimationFrame(frame);
    });

    // Places stepper (- / +), clamped to the input's min and max
    document.querySelectorAll('[data-stepper]').forEach(function (stepper) {
        var input = stepper.querySelector('input');
        stepper.querySelectorAll('[data-step]').forEach(function (button) {
            button.addEventListener('click', function () {
                var min = parseInt(input.min, 10) || 1;
                var max = parseInt(input.max, 10) || 12;
                var value = parseInt(input.value, 10) || 0;
                input.value = Math.min(max, Math.max(min, value + parseInt(button.dataset.step, 10)));
                input.classList.remove('bump');
                void input.offsetWidth;
                input.classList.add('bump');
            });
        });
    });

    // Loading state on submit, which also prevents double bookings
    document.querySelectorAll('form[data-loading]').forEach(function (form) {
        form.addEventListener('submit', function () {
            var button = form.querySelector('button[type="submit"]');
            if (!button) return;
            button.classList.add('is-loading');
            button.setAttribute('aria-busy', 'true');
        });
    });

    // Restore buttons when the page comes back from the browser cache
    window.addEventListener('pageshow', function (event) {
        if (!event.persisted) return;
        document.querySelectorAll('.is-loading').forEach(function (button) {
            button.classList.remove('is-loading');
            button.removeAttribute('aria-busy');
        });
    });
})();
