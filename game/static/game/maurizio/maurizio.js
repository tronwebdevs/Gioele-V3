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
    gameSocket.send(JSON.stringify({
      a: 5, // Action type
      i: _enemy.id // enemy id
    }));

      TEMP_SHIT();
  }
}

function b_maurizio(_bullet, i, gunType){
  if (_bullet.y <= 0){
    if (gunType == 0){
      mainGunBullets.splice(i,1);
    }
    if (gunType == 1){
      sideGunBullets.splice(i,1);
    }
  }
  if (_bullet.y >= gameArea.canvas.height){
    if (gunType == 2){
      enemiesBullets.splice(i,1);
    }
  }
}

function collision(bullet,i,g){
  if (bullet === undefined){
    return;
  }
  for (k = 0; k < enemies.length; k++) {
    if (bullet.collide(enemies[k])) {
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

function e_collision(bullet){


}

//patterns based on enemy type (x)
function getPattern(x){
  if (x == 0){
    switch (Math.floor(Math.random() * 2)) {
      case 0:
        return {pattern: e0_pattern_0, behavior: e0_behavior_0};
        break;
      case 1:
        return {pattern: e0_pattern_1, behavior: e0_behavior_1};
        break;
    }
  }
  if (x == 1){
    return {pattern: e1_pattern_0, behavior: e1_behavior_0};
  }
  if (x == 2){
    console.log("WORK IN PROGRESS")
    return {pattern: e0_pattern_0, behavior: e0_behavior_0};
  }
}


//returns rbg value based on hp
function getRGB(hp, maxhp){
  if (hp >= maxhp/2){
    let R = Math.floor(255*maxhp/hp-255);
    return "rgb("+R+",255,0)";
  } else  {
    let G = Math.floor(255*hp/(maxhp/2));
    return "rgb(255,"+G+",0)";
  }
}
