//
// UPDATE VISIT LOG (for analiytics)
//
/*
// Check if device is has touch screen (https://www.geeksforgeeks.org/how-to-detect-touch-screen-device-using-javascript/)
istouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0 || navigator.msMaxTouchPoints > 0;
// Request update to API
fetch('/api/vl/', {
    method: 'POST',
    headers: { 'Content-type': 'application/json;charset=UTF-8' },
    body: JSON.stringify({
        l: navigator.language,
        ua: navigator.userAgent,
        p: navigator.platform,
        sw: window.innerWidth,
        sh: window.innerHeight,
        r: document.referrer,
        ts: istouch
    })
});
*/

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

            // FIXED ?
            enemies.push(new Enemy(enemy.id, 0, enemy.pos.x, enemy.pos.y, enemy.hp, 15));

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
