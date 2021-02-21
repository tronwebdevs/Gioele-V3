let FPS = 60;
let skin = new Image();
skin.src = 'static/game/images/skin_01.png';
let background = new Image();
background.src = 'static/game/images/background.png';
let enemyskin = new Image();
enemyskin.src = 'static/game/images/enemy.png';
let mainGunBullets = [];
let sideGunBullets = [];
let enemies = [];
let enemiesBullets = [];

  let test = {
      mainGun: mainGun_0,
      sideGun: sideGun_0,
      support: {
          // TODO
      },
  };

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
