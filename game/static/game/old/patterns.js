// bullet patterns

//straight
let pattern_0 = function() {
  this.y += this.speedY;
}

//   woblblbl
let pattern_1 = function() {
  this.y += this.speedY;
  this.x = this.constX + this.mult*Math.cos(this.arg*3.14/180);
  this.arg += 7;
  this.mult += 0.5;
}


//bullet behaviors
let behavior_0 = function () {
  this.constX = this.x;
  this.arg = 90;
  this.mult = 0;
}
