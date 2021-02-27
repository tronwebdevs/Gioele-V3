function update() {
  if (gameArea.isPaused){
    return;
  }

  gameArea.clear();
  gameArea.updateBG();

  player.changePos();
  player.update();

  for (i = 0; i < enemies.length; i++) {
    enemies[i].move();
    enemies[i].update();
    e_maurizio(enemies[i], i);
  }  
  for (i = 0; i < mainGunBullets.length; i++) {
    mainGunBullets[i].move();
    mainGunBullets[i].update();
    collision(mainGunBullets[i], 0);
    b_maurizio(mainGunBullets[i], i, 0);
  }
  for (i = 0; i < sideGunBullets.length; i++) {
    sideGunBullets[i].move();
    sideGunBullets[i].update();
    collision(sideGunBullets[i], 1);
    b_maurizio(sideGunBullets[i], i, 1);
  }

}
