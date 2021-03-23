function openModal(id, title, content) {
    var modal = document.getElementById(id);
    // Check if modal is already opened
    if (!modal.classList.contains('active')) {
        // Prevent scrolling
        document.body.className = 'stop-scrolling';
        window.scrollTo(0, 0);
        document.body.scrollTop = 0;
        document.documentElement.scrollTop = 0;
    
        modal.className += ' active';
        document.getElementById(id + '-title').innerText = title;
        document.getElementById(id + '-content').innerText = content;
    }
}

function closeModal(id) {
    // Re-enable scrolling
    document.body.className = '';

    var el = document.getElementById(id);
    el.className = el.className.replace(' active', '');
}
