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
function e_pattern_0() {
  this.y += 0.4;
  if (Math.floor(this.y) == this.p_y && !this.hasShot){
    this.hasShot = true;
    console.log("BUM id:" + this.id + " this y:" + this.y + " p_y: " + this.p_y )
    let deltaX = this.x - (player.x + player.width/2);
    let deltaY = Math.abs(this.y - player.y - player.height/2);
    enemiesBullets.push(new Bullet(this.x, this.y, 4, function(){
      this.y += this.speedY;
      this.x -= this.speedY * Math.tan(this.ang);
    }, function() {
      this.ang = Math.atan(deltaX/deltaY);
    }));
  }
}
// normal 1
function e_pattern_1() {
  this.y += 0.6;
}
