
// Hippity hoppity, your code is now MY property
// (https://stackoverflow.com/a/11767598)
function getCook(cookiename) {
    var cookiestring=RegExp(cookiename+"=[^;]+").exec(document.cookie);
    return decodeURIComponent(!!cookiestring ? cookiestring.toString().replace(/^[^=]+./,"") : "");
}


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

function openModal(title, description) {
    document.body.className = 'stop-scrolling';
    window.scrollTo(0, 0);
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
    document.getElementById('confirm-buy').className += ' active';
    document.getElementById('cb-title').innerText = title;
    document.getElementById('cb-desc').innerText = description;
}

function closeModal(event) {
    document.body.className = '';
    var el = document.getElementById('confirm-buy');
    el.className = el.className.replace(' active', '');
    setModalError(null);
}

function buy(e, itemId, itemName, itemType) {
    e.preventDefault();
    document.getElementById('confirm-buy').setAttribute('data-item-type', itemType);
    document.getElementById('confirm-buy').setAttribute('data-item-id', itemId);
    if (itemType === 'gun') {
        openModal('Conferma', `Voi comprare l'arma "${itemName}"?`);
    } else {
        openModal('Conferma', `Voi comprare la skin "${itemName}"?`);
    }
}

function setModalError(message) {
    var el = document.getElementById('modal-error');
    el.style.display = message === null ? 'none' : 'block';
    el.childNodes[0].innerText = message;
}

function confirmBuy(event) {
    var token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    itemType = document.getElementById('confirm-buy').getAttribute('data-item-type');
    itemId = document.getElementById('confirm-buy').getAttribute('data-item-id');

    var respStatus = 0;
    fetch(`/api/shop/${itemType}s/${itemId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
        body: encodeURIComponent('csrfmiddlewaretoken') + '=' + encodeURIComponent(token) + '&',
    })
    .then(resp => {
        respStatus = resp.status;
        return resp.json();
    })
    .then(data => {
        if (respStatus !== 200) {
            setModalError(data.detail);
        } else {
            for (var el of document.getElementById(itemType + '-' + itemId).childNodes) {
                if (el.className && el.className.includes('card-footer')) {
                    const newEl = document.createElement('span');
                    newEl.className = 'card-footer own-text';
                    newEl.innerText = 'Comprata';
                    el.parentNode.replaceChild(newEl, el)
                    break;
                }
            }
            closeModal();
        }
    }).catch(console.error);
}

(function(){
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeModal();
        }
    })
}())