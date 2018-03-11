# https://www.codingame.com/ide/challenge/botters-of-the-galaxy
import time
import random
import sys
import math
from enum import Enum, IntEnum
from queue import PriorityQueue

# ===== items list =====
# Name                    Cost   Damage Health  maxH     Mana   maxM    Speed  ManaRe  isPotion
# [ Golden_Blade_14        934    129    0       0        0      0       63     0       0 ]
# [ mana_potion            25      0     0       0        50     0       0      0       1 ]
# [ Golden_Boots_13        984     0     0       0        100    100     150    13      0 ]
# ...

# ===== UNITS =====
# TYPE	                MEELE  HEALTH   DAMAGE  RANGE   MOVESPEED   ATTACKTIME  GOLD	MANA    MANAREG
# TOWER	                false  3000	    100	    400     0           0.2         0       0       0
# UNIT	                true   400	    25      90      150         0.2         30      0       0
# UNIT	                false  250	    35      300     150         0.2         50      0       0
# GROOT	                true   400	    35      150     250         0.2         100     0       0
# HERO-VALKYRIE	        true   1400	    65      130     200         0.1         300     155	    2
# HERO-DEADPOOL	        true   1380	    80      110     200         0.1         300     100	    1
# HERO-IRONMAN	        false  820	    60      270     200         0.1         300     200	    2
# HERO-DOCTOR_STRANGE	false  955	    50      45      200         0.1         300     300	    2
# HERO-HULK	            true   1450	    80      95      200         0.1         300     90      1

# ===== Hero stats and skill details =====
#
# Name	Stats	Skills
# Deadpool
#   health 1380
#   mana 100
#   damage 80
#   move speed 200
#   mana regen 1
#   range 110
#       COUNTER
#           reflects all damage he takes towards the closest entity enemy and recovers health while COUNTER was active. Dies if health reaches 0.
#           manacost: 40
#           cast duration: 0.05
#           range: 350
#           duration in rounds: 1
#           cooldown: 5
#           damage: damage received * 1.5
#       WIRE x y
#           throws a missile that stuns the first enemy it hits, a huge electric shock is sent through the wire damaging that enemy
#           manacost 50
#           range: 200
#           radius: 50
#           stun time: current turn and next 1 turns
#           cast duration: 0.3
#           cooldown: 9
#           damage multiplier: target hero's maxMana * 0.5
#       STEALTH x y
#           becomes temporarily invisible
#           manacost 30
#           duration : 5
#           cooldown: 6
# Hulk
#   health 1450
#   mana 90
#   damage 80
#   move speed 200
#   mana regen 1
#   range 95
#       CHARGE unitId
#           moves next to the target and attacks it
#           manacost: 20
#           cast duration: instant
#           range: 500
#           cooldown: 4
#       EXPLOSIVESHIELD
#           temporarily shields itself. if the shield is destroyed before it expires, it explodes and damages all nearby enemies
#           manacost: 30
#           duration in rounds: 4
#           temporary health bonus: maxHealth*0.07 + 50
#           explosion range: 151
#           explosion damage: 50
#           cooldown: 8
#       BASH unitId
#           attacks and stuns an enemy entity excluding towers
#           manacost: 40
#           duration: current round and next round
#           range: 150
#           cooldown: 10
# Valkyrie
#   health 1400
#   mana 155
#   damage 65
#   move speed 200
#   mana regen 2
#   range 130
#       SPEARFLIP unitId
#           moves target unit to the opposite side of the lancer
#           manacost: 20
#           cast duration: 0
#           range: 155
#           cooldown: 3
#           damage: attack damage * 0.4
#       JUMP x y
#           jumps to target location and damages closest enemy
#           manacost 35
#           cast duration: 0.05
#           range: 250
#           cooldown: 3
#           damage: attack damage
#       POWERUP
#           temporarily boosts its own attributes
#           manacost: 50
#           duration: 4
#           cooldown: 7
#           bonus range: 10
#           bonus attack damage: speed * 0.3
# Ironman
#   health 820
#   mana 200
#   damage 60
#   move speed 200
#   mana regen 2
#   range 270
#       BLINK x y
#           jumps to target location and recovers 20 mana
#           manacost: 16
#           range: 200
#           cast duration: 0.05
#           cooldown: 3
#       FIREBALL x y
#           throws a ball of fire that damages all enemy heroes and neutral creatures in a line
#           manacost: 60
#           range: 900
#           flytime: 0.9
#           impact radius: 50
#           damage: current mana * 0.2 + 55 * distance traveled / 1000
#           cast duration: instant
#           cooldown: 6
#       BURNING x y
#           makes that target location burn and damages all enemy units in the area
#           manacost: 50
#           range: 250
#           radius: 100
#           cast duration: instant
#           damage: manaRegeneration * 3 + 30
#           cooldown: 5
# Doctor Strange
#   health 955
#   mana 300
#   damage 50
#   move speed 200
#   mana regen 2
#   range 245
#       AOEHEAL
#           heals all nearby allied units
#           manacost: 50
#           cast duration: instant
#           range: 250
#           radius: 100
#           healing amount: mana * 0.2
#           cooldown: 7
#       SHIELD unitId
#           gives a shield to an allied units
#           manacost 20
#           duration in rounds: 2
#           range: 500
#           temporary health bonus: maxMana * 0.3
#           cooldown: 6
#       PULL unitId
#           pulls unitId towards the Dr. Strange's current location, drains some of its mana if it's an enemy hero
#           manacost 40
#           displacement range: 200
#           cast range: 300
#           mana drained from target: target's manaRegeneration * 3 + 5
#           cooldown: 5


class M:  # math function
    @staticmethod
    def dist(x1, y1, x2, y2):
        x = x1 - x2
        y = y1 - y2
        if x < 0:
            x = -x
        if y < 0:
            y = -y
        try:
            return G.dist_map[y][x]
        except:
            if x > y:
                _max = x
                _min = y
            else:
                _max = y
                _min = x
            return _max + _min * 22 / 64

    @staticmethod
    def dist_e(e1, e2):
        assert(isinstance(e1, RoundEntity))
        assert(isinstance(e2, RoundEntity))
        return M.dist(e1.x, e1.y, e2.x, e2.y)


class U:
    range_point_dict = {}

    @staticmethod
    def num_front(e_or_n):
        if isinstance(e_or_n, RoundEntity):
            return 1 - e_or_n.team - e_or_n.team
        elif isinstance(e_or_n, int):
            return 1 - e_or_n - e_or_n

    @staticmethod
    def is_entity_front(e_pos, ref, e_pos_team=None):
        assert(isinstance(ref, RoundEntity))
        if isinstance(e_pos, RoundEntity):
            e_pos_team = e_pos.team
            return (e_pos.x - ref.x >= 0 and e_pos_team == 0) or (e_pos.x - ref.x <= 0 and e_pos_team == 1)
        else:  # e_pos is a point, etc: (0,0)
            assert(e_pos_team == 0 or e_pos_team == 1)
            return (e_pos[0] - ref.x >= 0 and e_pos_team == 0) or (e_pos[0] - ref.x <= 0 and e_pos_team == 1)

    @staticmethod
    def get_range_pos(hero_or_radius, team=0):
        if isinstance(hero_or_radius, RoundEntity):
            team = hero_or_radius.team
            radius = hero_or_radius.movement_speed
        else:
            radius = hero_or_radius
        if radius in U.range_point_dict:
            return U.range_point_dict[radius]
        else:
            l = int(radius * 0.9)
            _res = []
            if team == 0:
                for _x in range(-l, l, 30):
                    for _y in range(l, -l, -30):
                        if M.dist(_x, _y, 0, 0) < l:
                            _res.append((_x, _y))
            else:
                for _x in range(l, -l, -30):
                    for _y in range(l, -l, -30):
                        if M.dist(_x, _y, 0, 0) < l:
                            _res.append((_x, _y))
            U.range_point_dict[radius] = _res
            return _res

    @staticmethod
    def get_shoot_range(unit):
        assert(isinstance(unit, RoundEntity))
        if unit.unitType == UnitType.TOWER:
            return unit.attackRange
        elif unit.unitType == UnitType.UNIT or unit.unitType == UnitType.GROOT:
            return unit.movement_speed * 0.8 + unit.attackRange
        elif unit.unitType == UnitType.HERO:
            return unit.movement_speed * 0.9 + unit.attackRange

    @staticmethod
    def get_nearest_entity(entity_list, this, target_team, target_type):
        assert(isinstance(this, RoundEntity))
        res = None
        _min_dis = 1e9
        for _ in entity_list:
            assert(isinstance(_, RoundEntity))
            if _.team == target_team and _.unitType == target_type:
                _dis = M.dist_e(this, _)
                if _dis < _min_dis:
                    _min_dis = _dis
                    res = _
        return _min_dis, res

    # @staticmethod
    # def sort_front(entity_list):
    #     assert(isinstance(entity_list, list))
    #     entity_list.sort(key=lambda entity: (1-2*entity.team)*entity.x + entity.team*G.WIDTH, reverse=True)
    #
    # @staticmethod
    # def sort_near(entity_list, entity_c):
    #     assert(isinstance(entity_list, list))
    #     assert(isinstance(entity_c, RoundEntity))
    #     entity_list.sort(key=lambda entity: M.dist_e(entity_c, entity))

    @staticmethod
    def unit_sorted_by_front(unit_dict, unit_type, team_num):
        assert(isinstance(unit_dict, dict))
        assert(isinstance(unit_type, UnitType))
        _res = []
        for unit in unit_dict[unit_type]:
            if unit.team == team_num:
                _res.append(unit)
        _res.sort(key=lambda u: -U.num_front(team_num) * u.x)
        return _res

    @staticmethod
    def unit_sorted_by_health(unit_dict, unit_type, team_num):
        assert(isinstance(unit_dict, dict))
        assert(isinstance(unit_type, UnitType))
        _res = []
        for unit in unit_dict[unit_type]:
            if unit.team == team_num:
                _res.append(unit)
        _res.sort(key=lambda u: u.health)
        return _res

    @staticmethod
    def aggro_unit(hero, entity_list):
        assert(isinstance(hero, RoundEntity))
        _res = []
        for _ in entity_list:
            if M.dist_e(hero, _) < 300 and hero.team == _.team and _.unitType == UnitType.UNIT:
                _res.append(_)
        return _res

    @staticmethod
    def out_of_tower(unit):
        assert(isinstance(unit, RoundEntity))
        if unit.team == 0:
            return unit.x < 1800
        else:
            return unit.x > 120

    @staticmethod
    def test():
        frontier = PriorityQueue()
        frontier.empty()
        frontier.put((0x040, 0xda7a))
        _ = frontier.get()[1]

    @staticmethod
    def get_nesest_entity(ref, entity_list, team_num_list=(-1, 0, 1)):
        assert(isinstance(ref, RoundEntity))
        _min_dist = 1e9
        _res = None
        for _ in entity_list:
            assert(isinstance(_, RoundEntity))
            if _.team in team_num_list:
                _dist = M.dist_e(ref, _)
                if _dist < _min_dist:
                    _min_dist = _dist
                    _res = _
        return _res


def debug(msg):
    print('DEBUG:{}'.format(msg), file=sys.stderr)


class Time:
    min_t = 1e9
    max_t = sum_t = num = count = 0
    rsp_limit = 50

    @staticmethod
    def set():
        Time.count = time.time()

    @staticmethod
    def get():
        _t = time.time() - Time.count
        Time.num += 1
        Time.sum_t += _t
        Time.min_t = min(_t, Time.min_t)
        Time.max_t = max(_t, Time.max_t)
        ave = Time.sum_t / Time.num
        debug('Time:{} ms, min:{} ms, max:{} ms, ave:{} ms'.format(
            int(_t*1000), int(Time.min_t*1000), int(Time.max_t*1000), int(ave*1000)))

    @staticmethod
    def left():
        return Time.rsp_limit - int((time.time() - Time.count)*1000)


class BushAndSpawnType(Enum):
    Bush = 'BUSH'
    Spawn = 'SPAWN'


class UnitType(Enum):
    UNIT = 'UNIT'
    HERO = 'HERO'
    TOWER = 'TOWER'
    GROOT = 'GROOT'


class ActType(Enum):
    WAIT = 'WAIT'  #
    MOVE = 'MOVE'  # x y
    ATTACK = 'ATTACK'  # unitId
    ATTACK_NEAREST = 'ATTACK_NEAREST'  # unitType [UNIT, HERO, TOWER, GROOT]
    MOVE_ATTACK = 'MOVE_ATTACK'  # x y unitId
    BUY = 'BUY'  # itemName
    SELL = 'SELL'  # itemName


class HeroType(Enum):
    UNKNOWN = '-'
    DEADPOOL = 'DEADPOOL'
    VALKYRIE = 'VALKYRIE'
    DOCTOR_STRANGE = 'DOCTOR_STRANGE'
    HULK = 'HULK'
    IRONMAN = 'IRONMAN'


class BushAndSpawn:
    def __init__(self, e_type, x, y, radius):
        self.e_type = BushAndSpawnType(e_type)
        self.x = int(x)
        self.y = int(y)
        self.radius = int(radius)

    def __str__(self):
        return '{}:({},{}),{}'.format(self.e_type.value, self.x, self.y, self.radius)


class Item:
    def __init__(self, itemName, itemCost, damage, health, maxHealth, mana, maxMana, moveSpeed, manaRegeneration, isPotion):
        self.itemName = itemName
        self.itemCost = int(itemCost)
        self.damage = int(damage)
        self.health = int(health)
        self.maxHealth = int(maxHealth)
        self.mana = int(mana)
        self.maxMana = int(maxMana)
        self.moveSpeed = int(moveSpeed)
        self.manaRegeneration = int(manaRegeneration)
        self.isPotion = int(isPotion)


class RoundEntity:
    def __init__(self, unitId, team, unitType,
                 x, y, attackRange, health, max_health,
                 shield, attack_damage, movement_speed,
                 stun_duration, gold_value,
                 countDown1 = 0, countDown2 = 0, countDown3 = 0,
                 mana = 0, maxMana = 0, manaRegeneration = 0,
                 heroType = 0, isVisible = 0, itemsOwned = 0):
        self.unitId = int(unitId)
        self.team = int(team)
        self.unitType = UnitType(unitType)
        self.x = int(x)
        self.y = int(y)
        self.attackRange = int(attackRange)
        self.health = int(health)
        self.max_health = int(max_health)
        self.shield = int(shield)
        self.attack_damage = int(attack_damage)
        self.movement_speed = int(movement_speed)
        self.stun_duration = int(stun_duration)
        self.gold_value = int(gold_value)
        # heroes only
        self.countDown1 = int(countDown1)
        self.countDown2 = int(countDown2)
        self.countDown3 = int(countDown3)
        self.mana = int(mana)
        self.maxMana = int(maxMana)
        self.manaRegeneration = int(manaRegeneration)
        self.heroType = HeroType(heroType)
        self.isVisible = int(isVisible)
        self.itemsOwned = int(itemsOwned)

    def __str__(self):
        return 'Id:{}|{}|{}|({},{})'.format(self.unitId, self.team, self.unitType.value, self.x, self.y)


class G:
    WIDTH = 1920
    HEIGHT = 750
    dist_map = [[0 for _ in range(750)] for __ in range(750)]

    def __init__(self):
        # global items
        self.hero_num = 0
        self.team_num = 0
        self.bushAndSpawnPointCount = 0
        self.bushAndSpawnPointList = []
        self.itemCount = 0
        self.itemList = []
        # round variables
        self.me_gold = 0
        self.op_gold = 0
        self.roundType = 0
        self.roundEntityCount = 0
        self.roundEntityList = []
        # custom
        self.me_heroes_type = []
        self.u = {}
        self.id_dict = []

        self.team_num = int(input())
        self.op_team = 1 - self.team_num
        self.bushAndSpawnPointCount = int(input())
        for _ in range(self.bushAndSpawnPointCount):
            bush_and_spawn = BushAndSpawn(*input().split())
            debug(str(bush_and_spawn))
            self.bushAndSpawnPointList.append(bush_and_spawn)
        self.itemCount = int(input())
        for _ in range(self.itemCount):
            item = input().split()
            debug('{}'.format(item))
            self.itemList.append(Item(*item))
        self.basePos = (100, 540) if self.team_num == 0 else (1820, 540)
        debug('Team Number:{}'.format(self.team_num))
        self.global_init()

    def global_init(self):
        assert(isinstance(self, G))
        for y in range(750):
            for x in range(750):
                if x >= y:
                    G.dist_map[y][x] = math.sqrt(x*x + y*y)
                    G.dist_map[x][y] = G.dist_map[y][x]

    def round_init(self):
        self.roundEntityList = []
        self.u = {UnitType.HERO: [], UnitType.GROOT: [], UnitType.UNIT: [], UnitType.TOWER: []}
        self.me_gold = int(input())
        self.op_gold = int(input())
        self.roundType = int(input())  # a positive value will show the number of heroes that await a command
        self.roundEntityCount = int(input())
        _dict = self.id_dict
        self.id_dict = {}
        for _ in range(self.roundEntityCount):
            item = RoundEntity(*input().split())
            self.roundEntityList.append(item)
            self.u[item.unitType].append(item)
            # update id_dict
            if item.unitId in _dict:
                self.id_dict[item.unitId] = (item, _dict[item.unitId][0])
            else:
                self.id_dict[item.unitId] = (item, item)

    def get_hero(self):
        if len(self.me_heroes_type) == 0:
            self.me_heroes_type.append(HeroType.DOCTOR_STRANGE)
            return HeroType.DOCTOR_STRANGE.value
        else:
            self.me_heroes_type.append(HeroType.IRONMAN)
            return HeroType.IRONMAN.value

    def is_inrange(self, p):
        return 0 <= p[0] < G.WIDTH and 0 <= p[1] < G.HEIGHT


class Arbiter:
    g = None
    hero_status = [[0], [0]]  # [[HeroStatus], [HeroStatus]]
    hero_old_status = [[0], [0]]  # [[HeroStatus], [HeroStatus]]
    my_heroes = []
    towers = []
    heroes_attack_points = [[], []]
    unit_front_list = []
    op_unit_front_list = []
    unit_health_list = []
    op_unit_health_list = []
    attacking_grootid = -1
    class HeroStatus(IntEnum):
        AGGRO = 0

    class HeroAction(IntEnum):
        KILL_HERO  = 1
        ESCAPE_HERO  = 2
        ESCAPE_AGGRO = 3
        SKILLS       = 4
        ATTACK_HERO  = 5
        ATTACK_TOWER = 6
        LAST_HIT     = 7
        DENY         = 8
        BUY          = 9
        SELL         = 10
        ATTACK_GROOT = 11
        ATTACK_UNIT  = 12
        FOLLOW_UNIT  = 13
        WAIT_MATE    = 14
        IDLE         = 15
        MAX          = 16

    def __init__(self, game_info):
        assert(isinstance(game_info, G))
        Arbiter.g = game_info

    @staticmethod
    def is_safe(g, hero):
        return True

    @staticmethod
    def update_round_param(g):
        assert(isinstance(g, G))
        Arbiter.my_heroes = [None for _ in range(2)]
        for _ in Arbiter.g.u[UnitType.HERO]:
            if _.team == g.team_num and _.heroType == g.me_heroes_type[0]:
                Arbiter.my_heroes[0] = _
            elif _.team == g.team_num and _.heroType == g.me_heroes_type[1]:
                Arbiter.my_heroes[1] = _
        Arbiter.towers = [None for _ in range(2)]
        for _ in Arbiter.g.u[UnitType.TOWER]:
                Arbiter.towers[_.team] = _
        Arbiter.unit_front_list = U.unit_sorted_by_front(g.u, UnitType.UNIT, g.team_num)
        Arbiter.op_unit_front_list = U.unit_sorted_by_front(g.u, UnitType.UNIT, g.op_team)
        Arbiter.unit_health_list = U.unit_sorted_by_health(g.u, UnitType.UNIT, g.team_num)
        Arbiter.op_unit_health_list = U.unit_sorted_by_health(g.u, UnitType.UNIT, g.op_team)
        for _idx in range(len(Arbiter.my_heroes)):
            if not Arbiter.my_heroes[_idx] is None:
                Arbiter.heroes_attack_points[_idx] = U.get_range_pos(Arbiter.my_heroes[_idx])

    @staticmethod
    def gen_choices(g, hero_idx):
        _new_choices = [None for _ in range(Arbiter.HeroAction.MAX.value)]
        hero = Arbiter.my_heroes[hero_idx]
        if hero is None:
            return _new_choices
        assert(isinstance(g, G))
        assert(isinstance(hero, RoundEntity))
        assert(hero.heroType == g.me_heroes_type[0] or hero.heroType == g.me_heroes_type[1])
        unit_front_list = Arbiter.unit_front_list
        op_unit_front_list = Arbiter.op_unit_front_list
        unit_health_list = Arbiter.unit_health_list
        op_unit_health_list = Arbiter.op_unit_health_list
        attack_points = Arbiter.heroes_attack_points[hero_idx]
        towers = Arbiter.towers
        for s in Arbiter.HeroAction:
            if s == Arbiter.HeroAction.KILL_HERO:
                _r = None
                if [_ for _ in Arbiter.my_heroes].count(None) == 0:
                    for op_hero in g.u[UnitType.HERO]:
                        if op_hero.team != g.team_num:
                            if (op_hero.health < (Arbiter.my_heroes[0].attack_damage + Arbiter.my_heroes[1].attack_damage) * 2 or op_hero.health < (Arbiter.my_heroes[0].attack_damage + Arbiter.my_heroes[1].attack_damage)) and \
                                Arbiter.my_heroes[0].health > 450 and Arbiter.my_heroes[1].health > 450 and \
                                M.dist_e(Arbiter.my_heroes[0], op_hero) < U.get_shoot_range(Arbiter.my_heroes[0]) and \
                                M.dist_e(Arbiter.my_heroes[1], op_hero) < U.get_shoot_range(Arbiter.my_heroes[1]):
                                debug('KILL:{}'.format(str(op_hero)))
                                _r = ('MOVE_ATTACK {} {} {} ; KILL'.format(op_hero.x, op_hero.y, op_hero.unitId),)
            elif s == Arbiter.HeroAction.ESCAPE_HERO:
                _r = None
                debug('{},{}'.format(hero.x, g.u[UnitType.TOWER][0].x - 20))
                if (hero.team == 0 and hero.x > g.u[UnitType.TOWER][1].x - 20) or (hero.team == 1 and hero.x < g.u[UnitType.TOWER][0].x + 20):
                    _r = ('MOVE {} {} ; Escape from tower'.format(hero.x-hero.movement_speed * U.num_front(hero), hero.y),)
                if len(op_unit_front_list)> 0 and len(unit_front_list)> 0 and M.dist_e(hero, op_unit_front_list[0]) < hero.attackRange:
                    if hero.team == 0 and hero.x < g.u[UnitType.TOWER][0].x - 20:
                        _r = ('ATTACK {} ; ATTACK'.format(op_unit_front_list[0].unitId),)
                    elif hero.team == 1 and hero.x > g.u[UnitType.TOWER][1].x + 20:
                        _r = ('ATTACK {} ; ATTACK'.format(op_unit_front_list[0].unitId),)
                elif len(op_unit_front_list)> 0 and g.id_dict[hero.unitId][0].health - g.id_dict[hero.unitId][1].health > 20 and M.dist_e(hero, op_unit_front_list[0]) < op_unit_front_list[0].attackRange:
                    _r = ('MOVE_ATTACK {} {} {} ; MOVE_ATTACK'.format(int(hero.x - U.num_front(hero) * hero.movement_speed), hero.y, op_unit_front_list[0].unitId),)
                elif not U.out_of_tower(hero) and \
                        (len(unit_front_list) > 0 and len(op_unit_front_list)> 0 and (hero.x - unit_front_list[0].x) * U.num_front(hero) > 0):
                    _r = ('MOVE_ATTACK {} {} {} ; MOVE_ATTACK'.format(int(unit_front_list[0].x - 20 * U.num_front(hero)), hero.y, op_unit_front_list[0].unitId),)

            elif s == Arbiter.HeroAction.ESCAPE_AGGRO:
                _r = None
                # debug('AGGRO:hero-{} {}'.format(hero_idx, Arbiter.hero_old_status[hero_idx][Arbiter.HeroStatus.AGGRO.value]))
                aggro = Arbiter.hero_old_status[hero_idx][Arbiter.HeroStatus.AGGRO.value]
                if aggro > 0:
                    is_safe = True
                    for op_unit in g.u[UnitType.HERO] + g.u[UnitType.UNIT] + g.u[UnitType.TOWER]:
                        if op_unit.team == g.op_team and M.dist_e(hero, op_unit) < U.get_shoot_range(op_unit):
                            is_safe = False
                            break
                    if is_safe:
                        Arbiter.hero_status[hero_idx][Arbiter.HeroStatus.AGGRO.value] = 0
                        continue
                    Arbiter.hero_status[hero_idx][Arbiter.HeroStatus.AGGRO.value] = aggro - 1
                    debug('ESCAPE_AGGRO:{} - {}'.format(hero.unitId, aggro))
                    _r = ('MOVE {} {} ; ESCAPE_AGGRO'.format(int(hero.x - U.num_front(hero) * (U.get_shoot_range(hero))), hero.y),)
            elif s == Arbiter.HeroAction.SKILLS:
                _r = None
#       BURNING x y
#           makes that target location burn and damages all enemy units in the area
#           manacost: 50
#           range: 250
#           radius: 100
#           cast duration: instant
#           damage: manaRegeneration * 3 + 30
#           cooldown: 5
                if False and hero.heroType == HeroType.IRONMAN and hero.countDown3 == 0 and hero.mana > 50:  # BURNING
                    for op_hero in g.u[UnitType.HERO]:  # Burning hero
                        if op_hero.team == g.op_team and 300 > M.dist_e(hero, op_hero):
                            for p in U.get_range_pos(249):  # check no unit attack me
                                if M.dist(hero.x+p[0], hero.y+p[1], op_hero.x, op_hero.y) < 100 and g.is_inrange((hero.x+p[0], hero.y+p[1])):
                                    safe_flag = True
                                    for op_unit in g.u[UnitType.HERO] + g.u[UnitType.UNIT] + g.u[UnitType.TOWER]:
                                        if M.dist_e(hero, op_unit) < op_unit.attackRange and op_unit.unitId != op_hero and op_unit.team == g.op_team:
                                            safe_flag = False
                                            break
                                    if safe_flag:
                                        debug('BURNING HERO:{}'.format(op_hero.unitId))
                                        _r = ('BURNING {} {} ; BURNING'.format(hero.x+p[0], hero.y+p[1]),)
                                        break
                    if _r:
                        continue
                    for op_unit in op_unit_health_list:  # Burning unit
                        if len(unit_front_list) == 0 or U.get_shoot_range(hero) < M.dist_e(hero, op_unit) or hero.mana < 100:
                            continue
                        for p in U.get_range_pos(249):
                            if not U.is_entity_front((hero.x+p[0], hero.y+p[1]), unit_front_list[0], hero.team):
                                if unit_front_list[0].health > 100:
                                    if 75 > M.dist(hero.x+p[0], hero.y+p[1], op_unit.x, op_unit.y) and g.is_inrange((hero.x+p[0], hero.y+p[1])):
                                        debug('BURNING Unit:{}'.format(op_unit.unitId))
                                        _r = ('BURNING {} {} ; BURNING'.format(hero.x+p[0], hero.y+p[1]),)
                                        break
                        if _r:
                            break
#       FIREBALL x y
#           throws a ball of fire that damages all enemy heroes and neutral creatures in a line
#           manacost: 60
#           range: 900
#           flytime: 0.9
#           impact radius: 50
#           damage: current mana * 0.2 + 55 * distance traveled / 1000
#           cast duration: instant
#           cooldown: 6
                elif hero.heroType == HeroType.IRONMAN and hero.countDown2 == 0 and hero.mana > 60:  # FIREBALL
                    for op_unit in g.u[UnitType.HERO]:  # FIREBALL unit
                        if op_unit is None or op_unit.team == g.team_num or M.dist_e(op_unit, hero) < 400 or \
                                op_unit.team == g.team_num or M.dist_e(op_unit, hero) > 800 or \
                                not g.basePos[1] - 120 < hero.y < g.basePos[1] + 120 or \
                                not g.basePos[1] - 120 < op_unit.y < g.basePos[1] + 120:
                            continue
                        debug('FIREBALL Unit:{}'.format(op_unit.unitId))
                        _r = ('FIREBALL {} {}'.format(op_unit.x, op_unit.y),)
                        break
#       AOEHEAL
#           heals all nearby allied units
#           manacost: 50
#           cast duration: instant
#           range: 250
#           radius: 100
#           healing amount: mana * 0.2
#           cooldown: 7
                elif hero.heroType == HeroType.DOCTOR_STRANGE and hero.countDown1 == 0 and hero.mana > 50:  # AOEHEAL
                    heroNum = 2 - Arbiter.my_heroes.count(None)
                    heroes = Arbiter.my_heroes
                    if len(unit_front_list) > 0 and not U.is_entity_front(hero, unit_front_list[0], g.team_num):
                        if heroNum == 1:
                            if hero.max_health - hero.health > hero.mana * 0.2 + 20 and len(unit_front_list) > 0 and \
                                    not U.is_entity_front((hero.x, hero.y), unit_front_list[0], hero.team):
                                debug('AOEHEAL Unit:{}'.format(hero.unitId))
                                _r = ('AOEHEAL {} {}'.format(hero.x, hero.y),)
                        else:
                            if heroes[0].max_health - heroes[0].health > hero.mana * 0.2 + 20 or \
                                            heroes[1].max_health - heroes[1].health > hero.mana * 0.2 + 20 and \
                                            M.dist_e(heroes[0], heroes[1]) < 98:
                                debug('AOEHEAL Unit:{}'.format(hero.unitId))
                                _r = ('AOEHEAL {} {} ; AOEHEAL'.format(
                                    (heroes[0].x + heroes[1].x) // 2,
                                    (heroes[0].y + heroes[1].y)//2),)
#       SHIELD unitId
#           gives a shield to an allied units
#           manacost 20
#           duration in rounds: 2
#           range: 500
#           temporary health bonus: maxMana * 0.3
#           cooldown: 6
                elif hero.heroType == HeroType.DOCTOR_STRANGE and hero.countDown2 == 0 and hero.mana > 100:  # SHIELD
                    for unit in unit_health_list:  # SHIELD unit
                        if len(unit_front_list) == 0 or unit.max_health - unit.health < 100:
                            continue
                        if not U.is_entity_front((hero.x, hero.y), unit_front_list[0], hero.team):
                            if 499 > M.dist(hero.x, hero.y, unit.x, unit.y):
                                debug('SHIELD Unit:{}'.format(unit.unitId))
                                _r = ('SHIELD {}'.format(unit.unitId),)
                                break
                        if _r:
                            break
            elif s == Arbiter.HeroAction.ATTACK_HERO:
                _r = None
                for op_hero in g.u[UnitType.HERO]:
                    if op_hero.team == g.op_team and U.get_shoot_range(hero) > M.dist_e(hero, op_hero):
                        for p in attack_points:  # no op_hero attack me
                            if M.dist(hero.x+p[0], hero.y+p[1], op_hero.x, op_hero.y) < hero.attackRange and g.is_inrange((hero.x+p[0], hero.y+p[1])):
                                safe_flag = U.out_of_tower(hero)
                                for op_unit in g.u[UnitType.HERO] + g.u[UnitType.UNIT] + g.u[UnitType.TOWER]:
                                    if M.dist(hero.x+p[0], hero.y+p[1], op_unit.x, op_unit.y) < op_unit.attackRange and op_unit.unitId != op_hero and op_unit.team == g.op_team:
                                        safe_flag = False
                                        break
                                if safe_flag:
                                    debug('ATTACK HERO:{}'.format(op_hero.unitId))
                                    _r = ('MOVE_ATTACK {} {} {} ; ATTACK HERO'.format(hero.x+p[0], hero.y+p[1], op_hero.unitId), 'AGGRO')
                                    break
                        if _r:
                            break
            elif False and s == Arbiter.HeroAction.ATTACK_TOWER:  # !!! NOT Checked
                _r = None
                if len(unit_front_list) == 0 or U.get_shoot_range(hero) < M.dist_e(hero, towers[g.op_team]):
                    continue
                exit_flag = True  # Check if there is a unit in tower's attack range
                for _i in range(len(unit_front_list)):
                    unit = unit_front_list[_i]
                    if M.dist_e(unit, towers[g.op_team]) < towers[g.op_team].attackRange:
                        _dec_heal = g.id_dict[unit.unitId][1].health - unit.health
                        if unit.health - _dec_heal > 10:
                            exit_flag = False
                            break
                if exit_flag:
                    continue
                exit_flag = False  # Check if no op_unit will attack me
                for op_unit in op_unit_front_list:
                    safe_flag = False
                    for unit in unit_front_list:
                        if M.dist_e(unit, op_unit) < op_unit.attackRange:
                            _dec_heal = g.id_dict[unit.unitId][1].health - unit.health
                            if unit.health - _dec_heal > 5:
                                safe_flag = True
                                break
                    if not safe_flag:
                        exit_flag = True
                        break
                if exit_flag:
                    continue
                for p in attack_points:  # no op_hero attack me
                    safe_flag = True
                    for op_hero in g.u[UnitType.HERO]:
                        if op_hero.unitId == g.op_team  and g.is_inrange((hero.x+p[0], hero.y+p[1])) and \
                                op_hero.attackRange < M.dist(hero.x+p[0], hero.y+p[1], op_hero.x, op_hero.y):
                            safe_flag = False
                            break
                    if safe_flag:
                        debug('ATTACK Tower:{}'.format(towers[g.op_team].health))
                        _r = ('MOVE_ATTACK {} {} {} ; MOVE_ATTACK'.format(hero.x+p[0], hero.y+p[1], towers[g.op_team].unitId),)
                        break

            elif s == Arbiter.HeroAction.LAST_HIT:
                _r = None
                if unit_front_list:
                    for op_unit in op_unit_health_list:
                        _dec_heal = g.id_dict[op_unit.unitId][1].health - op_unit.health
                        if not (hero.attack_damage >= op_unit.health - _dec_heal > 0) or len(unit_front_list) == 0:
                            continue
                        for p in attack_points:
                            if not U.is_entity_front((hero.x+p[0], hero.y+p[1]), unit_front_list[0], hero.team):
                                if unit_front_list[0].health > 10:
                                    if hero.attackRange > M.dist(hero.x+p[0], hero.y+p[1], op_unit.x, op_unit.y) and g.is_inrange((hero.x+p[0], hero.y+p[1])):
                                        debug('ATTACK LastHit:{}'.format(op_unit.unitId))
                                        _r = ('MOVE_ATTACK {} {} {} ; LAST_HIT'.format(hero.x+p[0], hero.y+p[1], op_unit.unitId),)
                                        break
                        if _r:
                            break
            elif s == Arbiter.HeroAction.DENY and False:
                _r = None
                if len(unit_front_list) > 0 and (g.roundType % 3) == 0:
                    for unit in unit_health_list:
                        for p in attack_points:
                            if not U.is_entity_front((hero.x+p[0], hero.y+p[1]), unit_front_list[0], hero.team) and U.out_of_tower(hero):
                                if sum([0 if _ is None else _.attack_damage for _ in Arbiter.my_heroes]) > unit_front_list[0].health > 10:
                                    if hero.attackRange > M.dist(hero.x+p[0], hero.y+p[1], unit.x, unit.y) and g.is_inrange((hero.x+p[0], hero.y+p[1])):
                                        debug('Deny LastHit:{}'.format(unit.unitId))
                                        _r = ('MOVE_ATTACK {} {} {} ; DENY'.format(hero.x+p[0], hero.y+p[1], unit.unitId),)
                                        break
                        if _r:
                            break
            elif s == Arbiter.HeroAction.BUY:
                _r = None
                for unit in unit_health_list:
                    if U.is_entity_front(hero, unit):
                        break
                    _dec_heal = g.id_dict[unit.unitId][1].health - unit.health
                    if unit.health < _dec_heal:
                        continue
                    if g.me_gold > 70 and hero.health < 450 and hero.itemsOwned <= 3:
                        _r = ('BUY larger_potion',)
                        break
                    if hero.heroType == HeroType.IRONMAN and hero.itemsOwned < 4:
                        # (itemName, itemCost, damage, health, maxHealth, mana, maxMana, moveSpeed, manaRegeneration, isPotion):
                        g.itemList.sort(key=lambda item: item.damage / item.itemCost, reverse=True)
                        for item in g.itemList:
                            if g.me_gold > item.itemCost > (50 + 50 * hero.itemsOwned) and item.damage > 0 and item.isPotion != 1:
                                _r = ('BUY {} ; BUY'.format(item.itemName),)
                                break
                    elif hero.heroType == HeroType.DOCTOR_STRANGE and hero.itemsOwned < 4:
                        g.itemList.sort(key=lambda item: item.manaRegeneration / item.itemCost, reverse=True)
                        for item in g.itemList:
                            if g.me_gold > item.itemCost > (0 + 100 * hero.itemsOwned) and item.manaRegeneration > 0 and item.isPotion != 1:
                                _r = ('BUY {} ; BUY'.format(item.itemName),)
                                break
                        if not _r:
                            g.itemList.sort(key=lambda item: item.damage / item.itemCost, reverse=True)
                            for item in g.itemList:
                                if g.me_gold > item.itemCost > (123 + 100 * hero.itemsOwned) and item.manaRegeneration > 0 and item.isPotion != 1:
                                    _r = ('BUY {} ; BUY'.format(item.itemName),)
                                    break
                    if _r:
                        break

            elif s == Arbiter.HeroAction.SELL:
                _r = None
            elif s == Arbiter.HeroAction.ATTACK_GROOT:
                _r = None
                if HeroType.DOCTOR_STRANGE not in [_.heroType if _.team != g.team_num else None for _ in g.u[UnitType.HERO]]:
                    continue
                if len(g.u[UnitType.GROOT]) > 0 and [_ for _ in Arbiter.my_heroes].count(None) == 0 and \
                                Arbiter.my_heroes[0].health > 270 and Arbiter.my_heroes[1].health > 270:
                    debug('ATTACK_GROOT debug')
                    if Arbiter.attacking_grootid not in g.id_dict:
                        if len(unit_front_list) > 0 and not U.is_entity_front((G.WIDTH/2+U.num_front(hero)*300,0), unit_front_list[0], g.team_num):
                            groots = g.u[UnitType.GROOT][:]
                            groots.sort(key=lambda x:(5e3 - M.dist_e(x, hero)) + 0 if (G.WIDTH/2-x.x)*U.num_front(hero)>0 else -1e5, reverse=True)
                            if U.is_entity_front((G.WIDTH/2+U.num_front(hero)*100,0), groots[0], g.team_num):
                                Arbiter.attacking_grootid = groots[0].unitId
                if Arbiter.attacking_grootid in g.id_dict:
                    groot = g.id_dict[Arbiter.attacking_grootid][0]
                    debug('select attacking groot as {}'.format(str(groot)))
                    _r = ('MOVE_ATTACK {} {} {} ; ATTACK_GROOT'.format(groot.x+random.randint(-100, 100), groot.y+random.randint(-100, 100), groot.unitId),)
            elif s == Arbiter.HeroAction.ATTACK_UNIT:
                _r = None
                if unit_front_list:
                    op_units = []
                    for unit in g.u[UnitType.UNIT]:
                        if unit.team == g.team_num:
                            op_units.append(unit)
                    op_units.sort(key=lambda u: u.health-u.x*U.num_front(g.team_num))
                    for op_unit in op_units:
                        if len(unit_front_list) == 0 or U.get_shoot_range(hero) < M.dist_e(hero, op_unit):
                            continue
                        for p in attack_points:
                            if not U.is_entity_front((hero.x+p[0], hero.y+p[1]), unit_front_list[0], hero.team) and U.out_of_tower(hero):
                                if unit_front_list[0].health > 50:
                                    if hero.attackRange > M.dist(hero.x+p[0], hero.y+p[1], op_unit.x, op_unit.y) and g.is_inrange((hero.x+p[0], hero.y+p[1])):
                                        debug('ATTACK Unit:{}'.format(op_unit.unitId))
                                        _r = ('MOVE_ATTACK {} {} {} ; ATTACK_UNIT'.format(hero.x+p[0], hero.y+p[1], op_unit.unitId),)
                                        break
                        if _r:
                            break
            elif s == Arbiter.HeroAction.FOLLOW_UNIT:
                _r = None
                if len(unit_front_list) > 0:
                    for u in unit_front_list:
                        assert(isinstance(u, RoundEntity))
                        if u.health > 120:
                            if hero.heroType == HeroType.IRONMAN and 20 < hero.mana < hero.maxMana - 5:
                                _r = ('BLINK {} {} ; FOLLOW_UNIT'.format(u.x - U.num_front(g.team_num)*100, u.y),)
                            else:
                                _r = ('MOVE {} {} ; FOLLOW_UNIT'.format(u.x - U.num_front(g.team_num)*100, u.y),)
                            break
            elif s == Arbiter.HeroAction.WAIT_MATE:
                _r = None
            elif s == Arbiter.HeroAction.IDLE:
                debug('IDLE')
                _r = ('MOVE {} {} ; IDLE'.format(g.basePos[0] - U.num_front(g.team_num) * 5, g.basePos[1]),)
            else: # HeroAction.MAX
                continue
            # if _r:
            #     debug('{} -> {}'.format(s, _r))
            _new_choices[s.value] = _r
        return _new_choices

    @staticmethod
    def gen_action(g, heroes_choices):
        assert(isinstance(g, G))
        assert(isinstance(heroes_choices, list))
        hero_act = ['WAIT', 'WAIT']
        buying_flag = True if 'BUY' in hero_act[0] and 'BUY' in hero_act[1] else False
        for idx in range(2):
            if heroes_choices[idx]:
                for act in heroes_choices[idx]:
                    if act:
                        if buying_flag and heroes_choices[idx].heroType == HeroType.IRONMAN:
                            continue
                        hero_act[idx] = act[0]
                        if len(act) > 1 and 'AGGRO' in act[1]:
                            Arbiter.hero_status[idx][Arbiter.HeroStatus.AGGRO.value] = 1
                        break
        return hero_act[0], hero_act[1]

    @staticmethod
    def hero_process(g):
        _heroes_choices = [None, None]
        Arbiter.update_round_param(g)
        for _idx in range(len(Arbiter.my_heroes)):
            _choices = Arbiter.gen_choices(g, _idx)
            _heroes_choices[_idx] = _choices
        _res = Arbiter.gen_action(g, _heroes_choices)
        Arbiter.hero_old_status = Arbiter.hero_status
        Arbiter.hero_status = [[0], [0]]  # [[HeroStatus], [HeroStatus]]
        return _res


def process(g):
    hero1_act, hero2_act = Arbiter.hero_process(g)
    # debug([str(_) for _ in U.unit_sorted_by_front(g.u, UnitType.UNIT, g.team_num)])
    if Arbiter.my_heroes[0] is not None:
        print(hero1_act)
    if Arbiter.my_heroes[1] is not None:
        print(hero2_act)


if __name__ == '__main__':
    random.seed(0)
    _g = G()
    Arbiter(_g)
    debug_in = '{}'.format('-')
    for _ in range(2):
        _g.round_init()  # pick hero
        print(_g.get_hero())
    while True:
        _g.round_init()
        # Time.set()
        process(_g)
        # Time.get()
