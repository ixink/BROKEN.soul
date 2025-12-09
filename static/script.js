function toggleLearnMore(id) {
    const el = document.getElementById('more-' + id);
    if (el) el.classList.toggle('hidden');
}

function confirmDelete(postIndex) {
    if (confirm("Are you sure you want to remove this story? This cannot be undone.")) {
        document.getElementById('delete-form-' + postIndex).submit();
    }
}

// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', () => {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.transition = 'opacity 1s';
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 1000);
        }, 6000);
    });
});