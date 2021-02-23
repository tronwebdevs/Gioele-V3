console.log("I am Maurizio.")
console.log("I do not forgive,")
console.log("I do not forget.")
/*        MAURIZIO:

navigator.geolocation.getCurrentPosition(
  function(pos){
    console.log("X:" + pos.coords.latitude)
    console.log("Y:" + pos.coords.longitude)
    console.log("Look out your window.")
  },
  function (err){
    console.log("Expect Me.")
  },
  {
    enableHighAccuracy: true,
    timeout: 5000,
    maximumAge: 0
  }
)
*/
console.log("Expect Me")

//garbage collection
function e_maurizio(_enemy, i){
  if (_enemy.y > gameArea.canvas.height + _enemy.radius){
    enemies.splice(i,1);
    // TODO: hit mother ship
  }
}


function b_maurizio(_bullet, i, gunType){
  if (_bullet.y <= 0){
    if (gunType == 0){
      mainGunBullets.splice(i,1);
      console.log("cancelled main bullet")
    }
    if (gunType == 1){
      sideGunBullets.splice(i,1);
      console.log("cancelled side bullet")
    }

    // gunType 2 come nemico ????


  }
}


//patterns based on enemy type
function getPattern(x){
  if (x === 0){
    switch (Math.floor(Math.random() * 2)) {
      case 0:
        return e_pattern_0;
        break;
      case 1:
        return e_pattern_1;
        break;
    }
  }
}
