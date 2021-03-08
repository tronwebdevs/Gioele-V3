function startGame() {
  gameSocket.send(JSON.stringify({a:0}));
  console.log("---- GAME STARTED")

  //while (Object.keys(player).length != 0) {
  //  console.log("---- CANVAS CREATED")
    gameArea.start();
  //}

  document.getElementById("gameStartButton").disabled = true;
}
function pauseGame() {
  //gameArea.pause();
  console.log("WIP")
}

function setPlayer(obj) {
  let mg, sg;
  if (obj.main_gun){
    mg = new MainGun(obj.main_gun.id, obj.main_gun.name, obj.main_gun.cooldown, obj.main_gun.damage)
  }
  if (obj.side_gun){
    sg = new SideGun(obj.side_gun.id, obj.side_gun.name, obj.side_gun.cooldown, obj.side_gun.damage)
  }
  player = new Player({
    mainGun: mg,
    sideGun: sg
  });
}


//CONTROLS
/*
function moveLeft(){
  clearInterval(accInterval);
  player.speedX = -speed;
  accInterval = setInterval(function(){
    player.speedX -= 1;
    if (player.speedX <= -maxSpeed){
      clearInterval(accInterval);
    }
  },200);
}
function moveRight(){
  clearInterval(accInterval);
  player.speedX = speed;
  accInterval = setInterval(function(){
    player.speedX += 1;
    if (player.speedX >= maxSpeed){
      clearInterval(accInterval);
    }
  },200);
}
function stopPlayer() {
  player.speedX = 0;
  clearInterval(accInterval);
}
*/
function moveLeft(){
  player.isMoving = true;
  player.direction = -1;
}
function moveRight(){
  player.isMoving = true;
  player.direction = 1;
}
function stopPlayer() {
  player.isMoving = false;
  player.direction = 0;
}

function shootMainGun() {
  player.equip.mainGun.shoot();
}
function shootSideGun() {
  player.equip.sideGun.shoot();
}


//INTERFACE
function reloadGun(gunType, cooldown){
  let bar = document.getElementById(gunType+"GunReady");
  bar.max = 100;
  bar.value = 0;

  let interval = setInterval(function(){
    bar.value ++;
    if (bar.value >= bar.max){
      clearInterval(interval);
    }
  }, cooldown/100)
};
