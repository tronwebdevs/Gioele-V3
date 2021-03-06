/*





*/



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

//push new enemy
gameSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    if (data.r === 1) {
      if (Object.keys(player).length == 0){
        console.log(data)
        setPlayer(data.player)
        console.log("---- PLAYER LOADED")
      } else {
        player.updateStats(data.player.hp, data.player.shield)
      }
    }
    if (data.r === 2 && data.lifes == 0) {
      /// TODO: VITE NAVE MADRE E GUI
    }
    if (data.r === 3) {
      for (let enemy of data.enemies) {
        enemies.push(new Enemy(enemy.id, enemy.type, enemy.pos.x, enemy.pos.y, enemy.hp, enemy.damage, enemy.rarity, 15));
      }
      checkRound(data.round)
    }
    if (data.r == 5) {
      clearInterval(gameArea.interval);
      let ctx = gameArea.canvas.getContext('2d');
      ctx.fillStyle = "red";
      ctx.textAlign = "center";
      ctx.font = "bold 30px RetroGaming";
      ctx.fillText(data.m, gameArea.canvas.width/2, gameArea.canvas.height/2);
      gameSocket.close();
    }
};

gameSocket.onclose = function (e) {
    wsConnEl.innerText = 'error';
    wsConnEl.style.color = 'red';
    console.error('Chat socket closed unexpectedly');
};

(function (){
  async function getData() {
  const response = await fetch('/api/shop/?functions=plain', {
    method: 'GET',
  });
  return response.json();
  }

  getData().then(data => {
    console.log(data);
  });
})();
