// bullet patterns

//straight
function pattern_0() {
  this.y -= this.speedY;
}

//   woblblbl
function pattern_1() {
  this.y -= this.speedY;
  this.x = this.constX + this.mult*Math.cos(this.arg*3.14/180);
  this.arg += 7;
  this.mult += 0.5;
}


//bullet behaviors
function behavior_0() {
  this.constX = this.x;
  this.arg = 90;
  this.mult = 0;
}


// enemies patterns

// normal 0
function e0_pattern_0() {
  this.y += 0.7;
  if (Math.floor(this.y) == this.p_y && !this.hasShot){
    this.hasShot = true;
    enemiesBullets.push(new Bullet(this.x, this.y, 4, function(){
      this.y += this.speedY;
      this.x -= this.speedY * Math.tan(this.ang);
    }, function() {
      this.ang = Math.atan((this.x - player.x - player.width/2)/Math.abs(this.y - player.y - player.height/2));
    }));
  }
}
function e0_behavior_0(){
  this.p_y = Math.floor(Math.random()*(gameArea.canvas.height/2));
  this.hasShot = false;
}
// normal 1
function e0_pattern_1() {
  this.y += this.speed;
  if (Math.floor(this.y) == this.p_y && !this.hasShot){
    this.speed = 0;
    this.shotInterval++;
    if (Number.isInteger(this.shotInterval/FPS)){
      this.shotCounter++;
      enemiesBullets.push(new Bullet(this.x, this.y, 4, function(){
        this.y += this.speedY;
        this.x -= this.speedY * Math.tan(this.ang);
      }, function() {
        this.ang = Math.atan((this.x - player.x - player.width/2)/Math.abs(this.y - player.y - player.height/2));
      }));
    }
    if (this.shotCounter>=3){
      this.hasShot = true;
      this.speed = 0.5;
    }
  }
}
function e0_behavior_1(){
  this.speed = 0.5;
  this.p_y = Math.floor(Math.random()*(gameArea.canvas.height/2));
  this.hasShot = false;
  this.shotInterval = 0;
  this.shotCounter = 0;
}

//kamikaze 0
function e1_pattern_0() {
  this.y += this.speedY;
  if (this.speedY <= 1){
    this.speedY += 0.01
  }
  if (this.y <= gameArea.canvas.height/2){  
    this.ang = Math.atan((this.x - player.x - player.width/2)/Math.abs(this.y - player.y - player.height/2));
  }
  this.x -= 1 * Math.tan(this.ang);
}
function e1_behavior_0() {
  this.speedY = 0.2;
}
