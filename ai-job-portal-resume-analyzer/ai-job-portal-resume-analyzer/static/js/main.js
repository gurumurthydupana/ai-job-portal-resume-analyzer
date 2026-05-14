/**
 * AI Job Portal — Main JavaScript
 * Handles: skill tag animations, score animations, search UX, form validation
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── Auto-dismiss alert messages after 4 seconds ──
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 4000);
    });

    // ── Animate progress bars on load ──
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function (bar) {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        setTimeout(function () {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = targetWidth;
        }, 200);
    });

    // ── Skill bar animations ──
    const skillBars = document.querySelectorAll('.skill-bar');
    skillBars.forEach(function (bar) {
        const targetWidth = bar.dataset.width || '0%';
        bar.style.width = '0%';
        setTimeout(function () {
            bar.style.width = targetWidth;
        }, 300);
    });

    // ── Search form: clear button ──
    const searchInputs = document.querySelectorAll('input[name="keyword"]');
    searchInputs.forEach(function (input) {
        if (input.value) {
            input.focus();
        }
    });

    // ── Job card: highlight on hover ──
    const jobCards = document.querySelectorAll('.job-card');
    jobCards.forEach(function (card) {
        card.addEventListener('mouseenter', function () {
            card.style.borderLeft = '4px solid #0d6efd';
        });
        card.addEventListener('mouseleave', function () {
            card.style.borderLeft = '';
        });
    });

    // ── Confirm delete actions ──
    const deleteForms = document.querySelectorAll('form[data-confirm]');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const message = form.dataset.confirm || 'Are you sure you want to delete this?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // ── Tooltip initialization ──
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    // ── Character counter for textareas ──
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(function (ta) {
        const maxLen = ta.getAttribute('maxlength');
        const counter = document.createElement('small');
        counter.className = 'text-muted';
        counter.textContent = `0 / ${maxLen} characters`;
        ta.parentNode.appendChild(counter);
        ta.addEventListener('input', function () {
            counter.textContent = `${ta.value.length} / ${maxLen} characters`;
        });
    });

    console.log('AI Job Portal JS initialized ✓');
});
