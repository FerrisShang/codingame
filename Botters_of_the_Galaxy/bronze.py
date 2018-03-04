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
# [ Legendary_Gadget_16    1229    0     2462    2462     0      0       0      0       0 ]
# [ mana_potion            25      0     0       0        50     0       0      0       1 ]
# [ Bronze_Gadget_1        46      0     0       0        92     92      0      0       0 ]
# [ Bronze_Blade_4         148     14    0       0        0      0       0      1       0 ]
# [ xxl_potion             330     0     500     0        0      0       0      0       1 ]
# [ Bronze_Blade_2         168     18    0       0        86     86      0      0       0 ]
# [ Bronze_Blade_3         113     16    0       0        0      0       0      0       0 ]
# [ Legendary_Blade_18     1113    198   0       0        100    100     0      0       0 ]
# [ Bronze_Boots_5         148     5     0       0        100    100     18     0       0 ]
# [ Silver_Blade_8         324     13    0       0        0      0       0      5       0 ]
# [ Silver_Blade_7         273     4     368     368      0      0       0      0       0 ]
# [ Silver_Blade_9         343     21    90      90       0      0       0      3       0 ]
# [ Silver_Gadget_6        300     0     381     381      100    100     0      0       0 ]
# [ Silver_Gadget_10       494     0     132     132      100    100     0      8       0 ]
# [ Golden_Boots_13        984     0     0       0        100    100     150    13      0 ]
# [ Golden_Boots_11        1010    0     0       0        88     88      150    14      0 ]
# [ Golden_Boots_15        579     0     567     567      100    100     56     0       0 ]
# [ larger_potion          70      0     100     0        0      0       0      0       1 ]
# [ Legendary_Boots_19     1268    150    0      0        0      0       150    4       0 ]
# [ Legendary_Gadget_20    1500    0      1928   1928     0      0       0      32      0 ]
# [ Golden_Blade_12        943     109    0      0        0      0       10     7       0 ]
# [ Legendary_Boots_17     1194    0      0      0        100    100     137    22      0 ]

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
        return math.sqrt((x1-x2)**2+(y1-y2)**2)

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
    def get_range_pos(hero):
        assert(isinstance(hero, RoundEntity))
        if hero.movement_speed in U.range_point_dict:
            return U.range_point_dict[hero.movement_speed]
        else:
            l = int(hero.movement_speed * 0.9)
            _res = []
            for _x in range(-l, l, 10):
                for _y in range(-l, l, 10):
                    if M.dist(_x, _y, 0, 0) < l:
                        _res.append((_x, _y))
            U.range_point_dict[hero.movement_speed] = _res
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

    @staticmethod
    def sort_front(entity_list):
        assert(isinstance(entity_list, list))
        entity_list.sort(key=lambda entity: (1-2*entity.team)*entity.x + entity.team*G.WIDTH, reverse=True)

    @staticmethod
    def sort_near(entity_list, entity_c):
        assert(isinstance(entity_list, list))
        assert(isinstance(entity_c, RoundEntity))
        entity_list.sort(key=lambda entity: M.dist_e(entity_c, entity))

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
    def aggro_unit(hero, entity_list):
        assert(isinstance(hero, RoundEntity))
        _res = []
        for _ in entity_list:
            if M.dist_e(hero, _) < 300 and hero.team == _.team and _.unitType == UnitType.UNIT:
                _res.append(_)
        return _res

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

    def __init__(self):
        # global items
        self.hero_num = 0
        self.team_num = 0
        self.op_team = 1 - self.team_num
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
        self.basePos = (200, 590) if self.team_num == 0 else (1720, 590)
        debug('Team Number:{}'.format(self.team_num))

    def global_init(self):
        pass

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
            self.me_heroes_type.append(HeroType.IRONMAN)
            return HeroType.IRONMAN.value
        else:
            self.me_heroes_type.append(HeroType.DOCTOR_STRANGE)
            return HeroType.DOCTOR_STRANGE.value


class Arbiter:
    g = None
    hero_status = [[(0,)], [(0,)]]  # [[HeroStatus], [HeroStatus]]

    class HeroStatus(IntEnum):
        AGGRO  = 0

    class HeroAction(IntEnum):
        ESCAPE_HERO  = 0
        ESCAPE_AGGRO = 1
        SKILLS       = 2
        ATTACK_HERO  = 3
        ATTACK_TOWER = 4
        LAST_HIT     = 5
        DENY         = 6
        BUY          = 7
        SELL         = 8
        ATTACK_UNIT  = 9
        FOLLOW_UNIT  = 10
        FOLLOW_GROOT = 11
        WAIT_MATE    = 12
        IDLE         = 13
        MAX          = 14

    def __init__(self, game_info):
        assert(isinstance(game_info, G))
        Arbiter.g = game_info

    @staticmethod
    def gen_choices(hero):
        g = Arbiter.g
        assert(isinstance(hero, RoundEntity))
        assert(isinstance(g, G))
        assert(hero.heroType == g.me_heroes_type[0] or hero.heroType == g.me_heroes_type[1])
        _hero_idx = 0 if hero.heroType == g.me_heroes_type[0] else 1
        _new_choices = [None for _ in range(Arbiter.HeroAction.MAX.value)]

        unit_front_list = U.unit_sorted_by_front(g.u, UnitType.UNIT, g.team_num)
        op_unit_front_list = U.unit_sorted_by_front(g.u, UnitType.UNIT, g.op_team)
        attack_points = U.get_range_pos(hero)
        for s in Arbiter.HeroAction:
            if s == Arbiter.HeroAction.ESCAPE_HERO:
                # _tmp = 0
                # for _enemy in g.u[UnitType.HERO]:
                #     if _enemy.team == g.op_team and _enemy
                _res = None
            elif s == Arbiter.HeroAction.ESCAPE_AGGRO:
                _res = None
            elif s == Arbiter.HeroAction.SKILLS:
                _res = None
            elif s == Arbiter.HeroAction.ATTACK_HERO:
                _res = None
            elif s == Arbiter.HeroAction.ATTACK_TOWER:
                _res = None
            elif s == Arbiter.HeroAction.LAST_HIT:
                _res = None
            elif s == Arbiter.HeroAction.DENY:
                _res = None
            elif s == Arbiter.HeroAction.BUY:
                _res = None
            elif s == Arbiter.HeroAction.SELL:
                _res = None
            elif s == Arbiter.HeroAction.ATTACK_UNIT:
                _res = None
                if unit_front_list:
                    for op_unit in op_unit_front_list:
                        for p in attack_points:
                            if hero.attackRange > M.dist(hero.x+p[0], hero.y+p[1], op_unit.x, op_unit.y):
                                _res = ('MOVE_ATTACK {} {} {}'.format(hero.x+p[0], hero.y+p[1], op_unit.unitId),)
                                break
                        if _res:
                            break

            elif s == Arbiter.HeroAction.FOLLOW_UNIT:
                _res = None
                if len(unit_front_list) > 0:
                    for u in unit_front_list:
                        assert(isinstance(u, RoundEntity))
                        if u.health > 80:
                            _res = ('MOVE {} {}'.format(u.x - U.num_front(g.team_num)*20+random.randint(-5, 5),
                                                        u.y + random.randint(-150, 150)),)
                            break
            elif s == Arbiter.HeroAction.FOLLOW_GROOT:
                _res = None
            elif s == Arbiter.HeroAction.WAIT_MATE:
                _res = None
            elif s == Arbiter.HeroAction.IDLE:
                _res = ('MOVE {} {}'.format(g.basePos[0], g.basePos[1]),)
            else: # HeroAction.MAX
                _res = None
                continue
            # if _res:
            #     debug('{} -> {}'.format(s, _res))
            _new_choices[s.value] = _res
        return _hero_idx, _new_choices

    @staticmethod
    def gen_action(heroes_choices):
        assert(isinstance(heroes_choices, list))
        g = Arbiter.g
        hero_act = ['WAIT', 'WAIT']
        for idx in range(2):
            if heroes_choices[idx]:
                for act in heroes_choices[idx]:
                    if act:
                        hero_act[idx] = act[0]
                        break
        return hero_act[0], hero_act[1]

    @staticmethod
    def hero_process():
        g = Arbiter.g
        _heroes_choices = [None, None]
        for _ in Arbiter.g.u[UnitType.HERO]:
            if _.team == g.team_num:
                _index, _choices = Arbiter.gen_choices(_)
                _heroes_choices[_index] = _choices
        return Arbiter.gen_action(_heroes_choices)


def process(g):
    Time.set()
    hero1_act, hero2_act = Arbiter.hero_process()
    # debug([str(_) for _ in U.unit_sorted_by_front(g.u, UnitType.UNIT, g.team_num)])
    print(hero1_act + '\n' + hero2_act)


if __name__ == '__main__':
    random.seed(0)
    _g = G()
    Arbiter(_g)
    debug_in = '{}'.format('-')
    for _ in range(2):
        _g.round_init()  # pick hero
        print(_g.get_hero())
    _g.global_init()
    while True:
        _g.round_init()
        process(_g)
        Time.get()
