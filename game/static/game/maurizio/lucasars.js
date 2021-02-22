// FIXME: temp cookie, remove soon
document.cookie = 'visit_id=kdfjghskdjfghkdsjfhgkdsjfgk';

const gameSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/api/game'
);
let wsConnEl = document.getElementById('ws-conn')
wsConnEl.innerText = 'open';
wsConnEl.style.color = 'green';


gameSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    if (data.r === 3) {
        for (let enemy of data.enemies) {


            // TO FIX
            let y = - Math.floor(Math.random() * 300);
            console.log(y)
            enemies.push(new Enemy(enemy.id, 0, enemy.x, y, 15));


        }
        console.log(data.enemies);
    } else {
        console.log(data);
    }
};
gameSocket.onclose = function (e) {
    wsConnEl.innerText = 'error';
    wsConnEl.style.color = 'red'
    console.error('Chat socket closed unexpectedly');
};
