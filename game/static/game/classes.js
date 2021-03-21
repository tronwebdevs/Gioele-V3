let gameArea = {
  canvas: document.getElementById("gameCanvas"),
  bgy : 0, //background Y pos

  start : function() {
    this.context = this.canvas.getContext("2d");
    //richiama la funzione update
    this.interval = setInterval(update, Math.round(1000/FPS));
  },
  clear : function() {
    this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
  },
  updateBG : function() {
    this.context.drawImage(background, 0, this.bgy);
    this.context.drawImage(background, 0, - 1199 + this.bgy);
    this.bgy += 0.2;
    if (this.bgy >= 1200){
      this.bgy = 0;
    }
  }
};

let GUI = {
  coords : {
    health : {x1: 10, x2: 110, y: 15},
    shield : {x1: 150, x2: 250, y: 15}
  },
  update : function(b){
    let x1,x2,y,color;
    let ctx = gameArea.context;

    if (b == 0){
      x1 = this.coords.health.x1;
      x2 = this.coords.health.x2;
      y = this.coords.health.y;
      color = getRGB(player.hp, 100);
    }
    if (b == 1){
      x1 = this.coords.shield.x1;
      x2 = this.coords.shield.x2;
      y = this.coords.shield.y;
      color = "rgb(0,180,255)";
    }

    ctx.beginPath();
    ctx.lineWidth = "10";
    ctx.strokeStyle = color;
    ctx.moveTo(x1, y);
    ctx.lineTo(x2, y);
    ctx.stroke();
  },/*
  updateCooldown : function(x){
    let cooldown = 0;
    let val = 0;
    let ctx = gameArea.context;

    if (x == 0 && player.equip.mainGun){
      cooldown = player.equip.mainGun.cooldown;
    }
    if (x == 1 && player.equip.sideGun){
      cooldown = player.equip.sideGun.cooldown;
    }

    let temp = setInterval(function(){
      val ++;
      ctx.beginPath();
      ctx.lineWidth = "10";
      ctx.strokeStyle = "rgb(100,200,255)";
      ctx.moveTo(player.x + player.radius, player.y);
      ctx.lineTo(player.x + player.radius, 0);
      ctx.stroke();
      if (val >= 100){
        clearInterval(temp);
      }
    }, cooldown/100)

  }*/
};

class Player {
  constructor(hp, shield, equip){
    this.hp = hp;
    this.shield = shield;
    this.radius = 30,
    this.x = 400;
    this.y = 530;

    this.isMoving = false;
    this.direction = 0; // -1 left | +1 right
    this.acc = 0; // in pixel*FPS, aumenta di 1 ad ogni frame se il player si muove altrimenti culaton
    this.maxSpeed = 5;

    this.equip = equip;
  }
  updateStats(hp, shield){
    this.hp = hp;
    this.shield = shield;
  }
  update() {
    let ctx = gameArea.context;
    ctx.save();
    ctx.setTransform(1, 0, -Math.round(this.acc/FPS)/70, 1, this.x-this.radius, this.y-this.radius);
    ctx.drawImage(skin, 0, 0)
    ctx.restore();
  }
  changePos() {
    //accelerazione
    if (this.direction * this.acc > 0){
      this.acc += this.direction * 5;
    } else {
      this.acc += this.direction * 10;
    }

    //decelerazione
    if (!this.isMoving){
      if (this.acc > 0){
        this.acc -= 5;
      } else {
        this.acc += 5;
      }
      if (this.acc >= -5 && this.acc <= 5){
        this.acc = 0;
      }
    }

    //spostamento
    this.x += Math.round((this.acc/FPS)*10) / 10;
    if (this.x < 0){
      this.x = 0;
      this.acc = 0;
    }
    if (this.x > gameArea.canvas.width){
      this.x = gameArea.canvas.width;
      this.acc = 0;
    }
  }
}

class Bullet {
  constructor(x, y, speedY, pattern, behavior = function(){}){
    this.speedY = speedY;
    this.speedX = 2;
    this.x = x;
    this.y = y;
    this.pattern = pattern;
    this.behavior = behavior;
    this.behavior()
  }
  update() {
    let ctx = gameArea.context;
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

class E_Bullet extends Bullet {
  constructor(e_id, x, y, damage, speedY, pattern, behavior = function(){}){
    super(x, y, speedY, pattern, behavior);
    this.damage = damage;
    this.e_id = e_id;
  }
  collide(){
    if (this.y >= gameArea.canvas.height - player.y - player.radius){
      if (Math.sqrt( (this.x-player.x)*(this.x-player.x) + (this.y-player.y)*(this.y-player.y) ) < player.radius ){
        return true;
      }
    }
  }
}

class Enemy {
  constructor(id, type, x, y, hp, damage, rarity, radius){
    this.id = id;
    this.type = type;
    let temp = getPattern(this.type);
    this.pattern = temp.pattern;
    this.behavior = temp.behavior;
    this.behavior();
    this.x = x;
    this.y = y;
    this.hp = hp;
    this.tothp = hp;
    this.damage = damage;
    this.rarity = rarity;
    this.radius = radius;
  }
  update() {
    let ctx = gameArea.context;
    ctx.drawImage(enemyskin, this.x - this.radius, this.y - this.radius)
    for (let i = 0; i < this.rarity; i++){
      ctx.beginPath();
      ctx.filter = "blur(5px)";
      ctx.lineWidth = enemies[i].radius + "";
      ctx.strokeStyle = "rgba(255,255,0,0.3)";
      ctx.arc(this.x, this.y, this.radius/2, 0, 2*Math.PI);
      ctx.stroke();
      ctx.filter = "blur(0px)";
    }
  }
  move() {
    this.pattern();
  }
}
