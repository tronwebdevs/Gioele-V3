//  MAIN GUNS

let mainGun_0 = {
  id : "MG0",
  name : "Blaster Mk1",
  cooldown : 1200,
  isReady : true,
  check : function(){
    // TODO:  anticheat
  },
  shoot : function(){
    if (this.isReady) {
      mainGunBullets.push(new Bullet(player.x + player.width/2, player.y, 8, false, pattern_0));
      mainGunBullets[mainGunBullets.length-1].behavior();
      this.isReady = false;

      gameSocket.send(JSON.stringify({
        a: 5,
        t: 0
      }));

      reloadGun("main", this.cooldown);
      let timeout = setTimeout(function(){
        test.mainGun.isReady = true;
      }, this.cooldown);
    }
  }
}




// SIDE GUNS

let sideGun_0 = {
  id : "SG0",
  name : "Cannone a Onde",
  cooldown : 3000,
  isReady : true,
  check : function(){
    // TODO:  anticheat
  },
  shoot : function(){
    if (this.isReady) {
      let tempx = player.x + player.width/2;
      sideGunBullets.push(new Bullet(tempx, player.y, 3, false, pattern_1, behavior_0));
      let tempvar = 0;
      let tempint = setInterval(function(){
        if (tempvar >= 5) {
          clearInterval(tempint);
        }
        sideGunBullets.push(new Bullet(tempx, player.y, 3, false, pattern_1, behavior_0));
        tempvar++;
      },50);
      this.isReady = false;

      gameSocket.send(JSON.stringify({
        a: 5,
        t: 1
      }));

      reloadGun("side", this.cooldown);
      let timeout = setTimeout(function(){
        test.sideGun.isReady = true;
      }, this.cooldown);
    }
  }
}
