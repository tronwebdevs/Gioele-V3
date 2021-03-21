function startGame() {
  document.getElementById("gameCanvas").onclick = function() {}
  startAnim(function(){
    //setTimeout(function(){
      gameSocket.send(JSON.stringify({a:0}));
    //},2000);
    console.log("---- GAME STARTED")
    gameArea.start();
  });
}

document.getElementById("gameCanvas").onclick = function() {
  startGame();
}

function setPlayer(obj) {
  let mg, sg;
  if (obj.main_gun){
    mg = new MainGun(
      obj.main_gun.id,
      obj.main_gun.name,
      obj.main_gun.cooldown,
      obj.main_gun.damage
    )
  }
  if (obj.side_gun){
    sg = new SideGun(
      obj.side_gun.id,
      obj.side_gun.name,
      obj.side_gun.cooldown,
      obj.side_gun.damage
    )
  }
  player = new Player(
    obj.hp,
    obj.shield,
    {
    mainGun: mg,
    sideGun: sg
  });
}

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
  if (player.equip.mainGun){
    player.equip.mainGun.shoot();
  }
}
function shootSideGun() {
  if (player.equip.sideGun){
    player.equip.sideGun.shoot();
  }
}
