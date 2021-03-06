function update() {
  gameArea.clear();
  gameArea.updateBG();

  if (Object.keys(player).length == 0){
    return;
  }

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
    b_maurizio(enemiesBullets[i], i, 2);
    e_collision(enemiesBullets[i], i);
  }

  showRound()
  displayOptions();

  GUI.update(0);
  GUI.update(1);
}

//default canvas
(function (){
    let ctx = gameArea.canvas.getContext('2d');
    gameArea.canvas.width = 800;
    gameArea.canvas.height = 600;
    ctx.fillStyle = "white";
    ctx.textAlign = "center";
    ctx.font = "bold 100px RetroGaming";
    ctx.fillText("GIOELE V3", gameArea.canvas.width/2, gameArea.canvas.height/2);
    ctx.font = "bold 50px RetroGaming";
    ctx.fillText("clicca per giocare", gameArea.canvas.width/2, gameArea.canvas.height/1.5);
})();

//animation at game start
function startAnim(callback){
  let ctx = gameArea.canvas.getContext('2d');
  ctx.font = "bold 100px RetroGaming";
  ctx.fillStyle = "black";
  ctx.textAlign = "center";
  let temp = 0;
  let tempInt = setInterval(function(){
    ctx.globalAlpha = 0+temp;
    ctx.drawImage(background,0,0);
    ctx.globalAlpha = 1-temp;
    ctx.fillStyle = 'rgb('+temp*255+','+temp*255+','+temp*255+')';
    ctx.fillText("GIOELE V3", 400, 300);
    temp+=0.02;
    if (temp >= 1){
      ctx.globalAlpha = 1;
      clearInterval(tempInt);
      callback();
    }
  }, Math.round(1000/FPS))
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
    let ctx = gameArea.context;
    ctx.font = "30px RetroGaming";
    ctx.fillStyle = "red";
    ctx.textAlign = "center";
    ctx.fillText("Ondata " + currentround, gameArea.canvas.width/2, gameArea.canvas.height/4);
  }
}

function displayOptions(){
  if (document.getElementById("opt_1").checked){
    for (i = 0; i < enemies.length; i++) {
      let ctx = gameArea.context;
      ctx.beginPath();
      ctx.lineWidth = "4";
      ctx.strokeStyle = getRGB(enemies[i].hp, enemies[i].tothp);
      ctx.moveTo(enemies[i].x - enemies[i].radius, enemies[i].y - 2*enemies[i].radius);
      ctx.lineTo(enemies[i].x + enemies[i].radius, enemies[i].y - 2*enemies[i].radius);
      ctx.stroke();
    }
  }
  if (document.getElementById("opt_2").checked){
    let ctx = gameArea.context;
    for (i = 0; i < enemies.length; i++) {
      ctx.beginPath();
      ctx.lineWidth = enemies[i].radius + "";
      ctx.strokeStyle = "rgba(255,0,0,0.5)";
      ctx.arc(enemies[i].x, enemies[i].y, enemies[i].radius/2, 0, 2*Math.PI);
      ctx.stroke();
    }
    ctx.beginPath();
    ctx.lineWidth = player.radius + "";
    ctx.strokeStyle = "rgba(255,0,0,0.5)";
    ctx.arc(player.x, player.y, player.radius/2, 0, 2*Math.PI);
    ctx.stroke();

    ctx.beginPath();
    ctx.lineWidth = "2";
    ctx.strokeStyle = "white";
    ctx.arc(player.x, player.y, 2, 0, 2*Math.PI);
    ctx.stroke();
  }
  if (document.getElementById("opt_3").checked){
    let ctx = gameArea.context;
    ctx.beginPath();
    ctx.lineWidth = "2";
    ctx.strokeStyle = "rgba(255,0,0,0.5)";
    ctx.moveTo(player.x, player.y);
    ctx.lineTo(player.x, 0);
    ctx.stroke();
  }


}
