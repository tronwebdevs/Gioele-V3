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
    gameSocket.send(JSON.stringify({
      a: 5, // Action type
      i: _enemy.id // enemy id
    }));
    enemies.splice(i,1);
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

function collision(x,i,g){
  if (x === undefined){
    return;
  }
  for (k = 0; k < enemies.length; k++) {
    if (x.collide(enemies[k])) {
      gameSocket.send(JSON.stringify({
          a: 6, // Action type
          g: g, // gun type (0:main, 1:side)
          i: enemies[k].id // enemy id
      }));

      if (g == 0){
        mainGunBullets.splice(i,1);
        enemies[k].hp -= player.equip.mainGun.damage;
      }
      if (g == 1){
        sideGunBullets.splice(i,1);
        enemies[k].hp -= player.equip.sideGun.damage;
      }
      if (enemies[k].hp <= 0){
        enemies.splice(k,1);
      }
    }
  }
}

//patterns based on enemy type (x)
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
