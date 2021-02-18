let gameArea = {
  canvas: document.getElementById("gameCanvas"),
  bgy : 0, //background Y

  start : function(){
    this.context = this.canvas.getContext("2d");
    this.canvas.width = 800;
    this.canvas.height = 600;
    //richiama la funzione update
    this.interval = setInterval(update, Math.round(1000/FPS));
  },
  clear : function(){
    this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
  },
  updateBG : function(){
    this.context.drawImage(background, 0, this.bgy);
    this.context.drawImage(background, 0, - 1199 + this.bgy);
    this.bgy++;
    if (this.bgy >= 1200){
      this.bgy = 0;
    }
  }
};

class Player {
  constructor(equip){
    this.width = 60,
    this.height = 60,
    this.x = 400;
    this.y = 550;

    this.isMoving = false;
    this.direction = 0; // -1 left | +1 right
    this.acc = 0; // in pixel*FPS, aumenta di 1 ad ogni frame se il player si muove altrimenti culaton
    this.maxSpeed = 5;

    this.equip = equip;
  }
  update() {
    let ctx = gameArea.context;
    ctx.drawImage(skin, this.x, this.y)
  }
  changePos() {
    if (this.direction * this.acc > 0){
      this.acc += this.direction * 5;
    } else {
      this.acc += this.direction * 10;
    }

    if (!this.isMoving){
      if (this.acc > 0){
        this.acc -= 2.5;
      } else {
        this.acc += 2.5;
      }
      if (this.acc >= -2.0 && this.acc <= 2.0){
        this.acc = 0;
      }
    }

    this.x += Math.round((this.acc/FPS)*10) / 10;
  }
}

class Bullet {
  constructor(x, y, speedY, isEnemy, pattern, behavior = function(){}){
    this.speedY = speedY;
    this.speedX = 2;
    this.x = x;
    this.y = y;
    this.isEnemy = isEnemy;
    this.pattern = pattern;
    this.behavior = behavior;
    this.behavior()
    if (!this.isEnemy) {
      this.speedY = -this.speedY;
    }
  }
  update() {
    let ctx = gameArea.canvas.getContext("2d");
    ctx.fillStyle = "white";
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.arc(this.x, this.y, 2, 0, 2 * Math.PI);
    ctx.closePath();
    ctx.fill();
  }
  move(){
    this.pattern();
  }
  collide(enemy){
    if (Math.sqrt( (this.x-enemy.x)*(this.x-enemy.x) + (this.y-enemy.y)*(this.y-enemy.y) ) < enemy.radius){
      return true;
    }
  }
}

class Enemy {
  constructor(id, x, radius){
    this.id = id;
    this.x = x;
    this.y = 0;
    this.radius = radius;
  }
  update() {
    let ctx = gameArea.context;
    ctx.drawImage(enemyskin, this.x - 15, this.y - 15)
  }
  move() {
    this.y++;
  }
}
