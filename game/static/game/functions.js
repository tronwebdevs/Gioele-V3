// esegue la funzione ad ogni frame
function update() {
  if (gameArea.isPaused){
    return;
  }

  gameArea.clear();
  gameArea.update();

  player.changePos();
  player.update();

  for (i = 0; i < mainGunBullets.length; i++) {
    mainGunBullets[i].move();
    mainGunBullets[i].update();
  }
  for (i = 0; i < sideGunBullets.length; i++) {
    sideGunBullets[i].move();
    sideGunBullets[i].update();
  }

  if (Math.random() < spawnRate){
    enemies.push(new Enemy(
      Math.floor(Math.random() * (gameArea.canvas.width - 50)) + 50,
      15));
  }

  for (i = 0; i < enemies.length; i++) {
    enemies[i].move();
    enemies[i].update();
  }

  for (i = 0; i < mainGunBullets.length; i++) {
    for (k = 0; k < enemies.length; k++) {
      if (mainGunBullets[i].collide(enemies[k])) {
        enemies.splice(k,1);
      }
    }
  }

  for (i = 0; i < sideGunBullets.length; i++) {
    for (k = 0; k < enemies.length; k++) {
      if (sideGunBullets[i].collide(enemies[k])) {
        enemies.splice(k,1);
      }
    }
  }

}



function startGame() {
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
