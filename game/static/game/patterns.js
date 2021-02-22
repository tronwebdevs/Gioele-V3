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
}
// normal 1
function e_pattern_1() {
  this.y += 0.6;
}
