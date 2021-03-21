//  MAIN GUNS

class MainGun {
  constructor(id, name, cooldown, damage){
    this.id = id;
    this.name = name;
    this.cooldown = cooldown;
    this.damage = damage;
    this.isReady = true;
  }
  shoot() {
    if (this.isReady) {
      mainGunBullets.push(new Bullet(player.x , player.y, 8, pattern_0));
      mainGunBullets[mainGunBullets.length-1].behavior();
      this.isReady = false;

      let timeout = setTimeout(function(){
        player.equip.mainGun.isReady = true;
      }, this.cooldown);
    }
  }
}

// SIDE GUN
class SideGun {
  constructor(id, name, cooldown, damage){
    this.id = id;
    this.name = name;
    this.cooldown = cooldown;
    this.damage = damage;
    this.isReady = true;
  }
  shoot() {
    if (this.isReady) {
      let tempx = player.x;
      sideGunBullets.push(new Bullet(tempx, player.y, 3, pattern_1, behavior_0));
      let tempvar = 0;
      let tempint = setInterval(function(){
        if (tempvar >= 5) {
          clearInterval(tempint);
        }
        sideGunBullets.push(new Bullet(tempx, player.y, 3, pattern_1, behavior_0));
        tempvar++;
      },50);
      this.isReady = false;

      let timeout = setTimeout(function(){
        player.equip.sideGun.isReady = true;
      }, this.cooldown);
    }
  }
}
