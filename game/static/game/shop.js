function openTab(e) {
    // Get all elements with class="tabcontent" and hide them
    var tabcontent = document.getElementsByClassName('tabcontent');
    for (var i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = 'none';
    }

    // Get all elements with class="tablinks" and remove the class "active"
    var tablinks = document.getElementsByClassName('tablinks');
    for (var i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(' active', '');
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    var targetId = e.currentTarget.getAttribute('target');
    document.getElementById(targetId).style.display = 'block';
    e.currentTarget.className += ' active';
}

function buy(e, gunId) {
    e.preventDefault();
    confirm(`Voi comprare l'arma #${gunId}`)
}