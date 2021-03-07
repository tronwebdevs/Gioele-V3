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

  showRound()

  displayOptions();
}


//GRAPHICS
function checkRound(x){
  if (currentround != x){
    currentround = x;
    canvasround = true;
    setTimeout(function(){
      canvasround = false;
    }, 2000);
  }
}
function showRound(){
  if (canvasround){
    let ctx = gameArea.canvas.getContext("2d");
    ctx.font = "30px Audiowide";
    ctx.fillStyle = "red";
    ctx.textAlign = "center";
    ctx.fillText("Ondata " + currentround, gameArea.canvas.width/2, gameArea.canvas.height/4);
  }
}

function displayOptions(){
  if (document.getElementById("opt_1").checked){
    for (i = 0; i < enemies.length; i++) {
      let ctx = gameArea.canvas.getContext("2d");
      ctx.beginPath();
      ctx.lineWidth = "4";
      ctx.strokeStyle = "rgb("+ 255/enemies[i].tothp*(enemies[i].tothp-enemies[i].hp) + ","+ 255/enemies[i].tothp*enemies[i].hp +",0)";
      ctx.moveTo(enemies[i].x - enemies[i].radius, enemies[i].y - 2*enemies[i].radius);
      ctx.lineTo(enemies[i].x + enemies[i].radius, enemies[i].y - 2*enemies[i].radius);
      ctx.stroke();
    }
  }
  if (document.getElementById("opt_2").checked){
    for (i = 0; i < enemies.length; i++) {
      let ctx = gameArea.canvas.getContext("2d");
      ctx.beginPath();
      ctx.lineWidth = enemies[i].radius + "";
      ctx.strokeStyle = "rgba(255,0,0,0.5)";
      ctx.arc(enemies[i].x, enemies[i].y, enemies[i].radius/2, 0, 2*Math.PI);
      ctx.stroke();
    }
  }
  if (document.getElementById("opt_3").checked){
    let ctx = gameArea.canvas.getContext("2d");
    ctx.beginPath();
    ctx.lineWidth = "2";
    ctx.strokeStyle = "rgba(255,0,0,0.5)";
    ctx.moveTo(player.x + player.width/2, player.y);
    ctx.lineTo(player.x + player.width/2, 0);
    ctx.stroke();
  }


}
