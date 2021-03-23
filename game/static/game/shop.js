
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

function closeItemModal() {
    closeModal('cbm')
    setModalError(null);
}

function buy(e, itemId, itemName, itemType) {
    e.preventDefault();
    var modal = document.getElementById('cbm');
    modal.setAttribute('data-item-type', itemType);
    modal.setAttribute('data-item-id', itemId);
    if (itemType === 'gun') {
        openModal('cbm', 'Conferma', `Voi comprare l'arma "${itemName}"?`);
    } else {
        openModal('cbm', 'Conferma', `Voi comprare la skin "${itemName}"?`);
    }
}

function setModalError(message) {
    var el = document.getElementById('modal-error');
    el.style.display = message === null ? 'none' : 'block';
    el.childNodes[0].innerText = message;
}

function confirmBuy() {
    var token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    var modal = document.getElementById('cbm');
    itemType = modal.getAttribute('data-item-type');
    itemId = modal.getAttribute('data-item-id');

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
            closeItemModal();
        }
    }).catch(console.error);
}

(function(){
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeItemModal();
        }
    })
}())