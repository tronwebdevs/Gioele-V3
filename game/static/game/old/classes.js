let gameArea = {
  canvas: document.getElementById("gameCanvas"),
  isPaused : false,
  bgcounter : 0,
  bgy : 0,

  start : function(){
    this.context = this.canvas.getContext("2d");
    this.canvas.width = 800;
    this.canvas.height = 600;
    //richiama la funzione update
    this.interval = setInterval(update, Math.round(1000/FPS));
  },
  pause : function(){
    this.isPaused ^= true;
  },
  stop : function(){
    //TO DO
  },
  clear : function(){
    this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
  },
  update : function(){
    this.context.drawImage(background, 0, this.bgy);
    this.context.drawImage(background, 0, - 1200 + this.bgy);
    this.bgcounter++;
    if (this.bgcounter == 2) {
      this.bgcounter = 0;
      this.bgy++;
    }
    if (this.bgy == 1200){
      this.bgy = 0;
    }
  }
};

class Player {
  constructor(equip){
    this.width = 30,
    this.height = 30,
    this.x = 400;
    this.y = 500;
    this.speedX = 0;
    this.equip = equip;
  }
  update() {
    let ctx = gameArea.context;
    ctx.drawImage(skin, this.x, this.y)
  }
  changePos() {
    if (this.x <= 0){
      this.x = 1;
      this.speedX = 0;
      return;
    }
    if (this.x >= gameArea.canvas.width-this.width) {
      this.x = gameArea.canvas.width-this.width-1;
      this.speedX = 0;
      return;
    }
    this.x += this.speedX;
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
  constructor(x, radius){
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