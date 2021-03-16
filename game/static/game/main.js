let FPS = 60;
let player = {};
let skin = new Image();
skin.src = 'static/game/images/skin_01.png';
let background = new Image();
background.src = 'static/game/images/background.png';
let canvasround = false;
let currentround = 0;
let enemyskin = new Image();
enemyskin.src = 'static/game/images/enemy.png';
let mainGunBullets = [];
let sideGunBullets = [];
let enemies = [];
let enemiesBullets = [];

let MOTHERLIVES = 3;
function TEMP_SHIT(){
  MOTHERLIVES --;
  if (MOTHERLIVES == 0) {
    clearInterval(gameArea.interval);
    let ctx = gameArea.canvas.getContext('2d');
    ctx.fillStyle = "red";
    ctx.textAlign = "center";
    ctx.font = "bold 30px RetroGaming";
    ctx.fillText("Nave Madre distrutta", gameArea.canvas.width/2, gameArea.canvas.height/2);
  }
}

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
