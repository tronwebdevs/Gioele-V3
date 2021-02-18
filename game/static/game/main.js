let FPS = 60;
let skin = new Image();
skin.src = 'static/game/images/skin01.png';
let background = new Image();
background.src = 'static/game/images/background.png';
let enemyskin = new Image();
enemyskin.src = 'static/game/images/enemy.png';
let mainGunBullets = [];
let sideGunBullets = [];
let enemies = [];
let enemiesBullets = [];
let spawnRate = 0.5 / FPS; // chance to spawn enemy at every frame

let test = {
    mainGun: mainGun_0,
    sideGun: sideGun_0,
    support: {
        // TODO
    },
};

const gameSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/api/game'
);
gameSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data);
};
gameSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};


/*
                  ODIO I DEPRECATI


document.body.addEventListener('keydown', function (event) {
    if (event.keyCode == 37 && !event.repeat) {
        event.preventDefault();
        moveLeft();
    }
});
document.body.addEventListener('keyup', function (event) {
    if (event.keyCode == 37) {
        event.preventDefault();
        stopPlayer();
    }
});

document.body.addEventListener('keydown', function (event) {
    if (event.keyCode == 39 && !event.repeat) {
        event.preventDefault();
        moveRight();
    }
});
document.body.addEventListener('keyup', function (event) {
    if (event.keyCode == 39) {
        event.preventDefault();
        stopPlayer();
    }
});

document.body.addEventListener('keydown', function (event) {
    if (event.keyCode == 81) {
        event.preventDefault();
        shootMainGun();
    }
});
document.body.addEventListener('keydown', function (event) {
    if (event.keyCode == 87) {
        event.preventDefault();
        shootSideGun();
    }
});
*/

document.body.onkeydown = function (e){
  if (e.keyCode === 37){
    e.preventDefault();
    moveLeft();
  }
  if (e.keyCode === 39){
    e.preventDefault();
    moveRight();
  }
  if (e.keyCode === 81){
    event.preventDefault();
    shootMainGun();
  }
  if (e.keyCode === 87){
    event.preventDefault();
    shootSideGun();
  }
}
document.body.onkeyup = function (e){
  if (e.keyCode === 37 || e.keyCode === 39){
    e.preventDefault();
    stopPlayer();
  }
}
