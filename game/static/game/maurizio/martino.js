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
    if (mainGunBullets[i] != undefined){
      mainGunBullets[i].move();
      mainGunBullets[i].update();
      b_maurizio(mainGunBullets[i], i, 0);
      collision(mainGunBullets[i], i, 0);
    }
  }
  for (i = 0; i < sideGunBullets.length; i++) {
    if (sideGunBullets[i] != undefined){
      sideGunBullets[i].move();
      sideGunBullets[i].update();
      b_maurizio(sideGunBullets[i], i, 1);
      collision(sideGunBullets[i], i, 1);
    }
  }
  for (i = 0; i < enemiesBullets.length; i++) {
    enemiesBullets[i].move();
    enemiesBullets[i].update();
  }

  /* TEMP */
        if (document.getElementById("x").checked){
          for (i = 0; i < enemies.length; i++) {
            let ctx = gameArea.canvas.getContext("2d");
            ctx.beginPath();
            ctx.lineWidth = "4";
            ctx.strokeStyle = "rgb("+ 255/enemies[i].tothp*(enemies[i].tothp-enemies[i].hp) + ","+ 255/enemies[i].tothp*enemies[i].hp +",0)";
            ctx.rect(enemies[i].x - enemies[i].radius, enemies[i].y - 2*enemies[i].radius, 2*enemies[i].radius,2);
            ctx.stroke();
          }
        }

}
