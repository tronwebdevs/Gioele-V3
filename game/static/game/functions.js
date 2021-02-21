function startGame() {
    gameSocket.send(JSON.stringify({a:0}));
  gameArea.start();
  player = new Player(test);
  player.equip.mainGun.check();
  document.getElementById("gameStartButton").disabled = true;
}
function pauseGame() {
  //gameArea.pause();
  console.log("WIP")
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
