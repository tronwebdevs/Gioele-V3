function update() {
  if (gameArea.isPaused){
    return;
  }

  gameArea.clear();
  gameArea.updateBG();

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

  for (i = 0; i < enemies.length; i++) {
    enemies[i].move();
    enemies[i].update();
  }

  for (i = 0; i < mainGunBullets.length; i++) {
    for (k = 0; k < enemies.length; k++) {
      if (mainGunBullets[i].collide(enemies[k])) {
        console.log('Killed #' + enemies[k].id)
        gameSocket.send(JSON.stringify({
            a: 6, // Action type
            t: 0, // gun type (0:main, 1:side)
            i: enemies[k].id // enemy id
        }));
        enemies.splice(k,1);
      }
    }
  }

  for (i = 0; i < sideGunBullets.length; i++) {
    for (k = 0; k < enemies.length; k++) {
      if (sideGunBullets[i].collide(enemies[k])) {
        console.log('Killed #' + enemies[k].id)
        gameSocket.send(JSON.stringify({
            a: 6, // Action type
            t: 1, // gun type (0:main, 1:side)
            i: enemies[k].id // enemy id
        }));
        enemies.splice(k,1);
      }
    }
  }

}
