# https://www.codingame.com/ide/10334676e733c3a4c89aadf31df4c9aa59b99f92
import time
import random
import sys
import math
from enum import Enum


class M:  # math function
    @staticmethod
    def dist(x1, y1, x2, y2):
        return math.sqrt((x1-x2)**2+(y1-y2)**2)

    @staticmethod
    def dist_e(e1, e2):
        assert(isinstance(e1, RoundEntity))
        assert(isinstance(e2, RoundEntity))
        return M.dist(e1.x, e1.y, e2.x, e2.y)


def debug(msg):
    print('DEBUG:'+msg, file=sys.stderr)


class Time:
    min_t = 1e9
    max_t = 0
    sum_t = 0
    num = 0
    count = 0
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
        self.e_type = e_type
        self.x = x
        self.y = y
        self.radius = radius


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


class G:
    WIDTH = 1920
    HEIGHT = 750

    def __init__(self):
        # global items
        self.hero_num = 0
        self.team_num = 0
        self.bushAndSpawnPointCount = 0
        self.bushAndSpawnPointList = []
        self.itemCount = 0
        self.itemList = []
        # round variables
        self.me_item_num = 0
        self.me_gold = 0
        self.op_gold = 0
        self.roundType = 0
        self.roundEntityCount = 0
        self.roundEntityList = []
        # custom
        self.me_heros = []
        self.me_units = []
        self.me_towers = []
        self.me_off_pos = []
        self.op_heros = []
        self.op_units = []
        self.op_towers = []

        self.team_num = int(input())
        self.bushAndSpawnPointCount = int(input())
        for _ in range(self.bushAndSpawnPointCount):
            entity_type, x, y, radius = input().split()
            self.bushAndSpawnPointList.append(
                BushAndSpawn(BushAndSpawnType(entity_type), int(x), int(y), int(radius)))
        self.itemCount = int(input())
        for _ in range(self.itemCount):
            item = input().split()
            debug('{}'.format(item))
            self.itemList.append(Item(*item))
        self.basePos = (200, 590) if self.team_num == 0 else (1720, 590)
        debug('Team Number:{}'.format(self.team_num))

    def round_init(self):
        self.roundEntityList = []
        self.me_heros = []
        self.me_units = []
        self.me_towers = []
        self.op_heros = []
        self.op_units = []
        self.op_towers = []
        self.me_gold = int(input())
        self.op_gold = int(input())
        self.roundType = int(input())  # a positive value will show the number of heroes that await a command
        self.roundEntityCount = int(input())
        for _ in range(self.roundEntityCount):
            item = RoundEntity(*input().split())
            self.roundEntityList.append(item)
            if item.team == self.team_num:
                if item.unitType == UnitType.HERO:
                    self.me_heros.append(item)
                elif item.unitType == UnitType.UNIT:
                    self.me_units.append(item)
                elif item.unitType == UnitType.TOWER:
                    self.me_towers.append(item)
            else:
                if item.unitType == UnitType.HERO:
                    self.op_heros.append(item)
                elif item.unitType == UnitType.UNIT:
                    self.op_units.append(item)
                elif item.unitType == UnitType.TOWER:
                    self.op_towers.append(item)

    @staticmethod
    def get_range_pos(hero):
        assert(isinstance(hero, RoundEntity))
        l = int(hero.movement_speed * 0.9)
        res = []
        for _x in range(-l, l, 10):
            for _y in range(-l, l, 10):
                if M.dist(_x, _y, hero.x, hero.y) < l:
                    res.append((hero.x+_x, hero.y+_y))
        return res

    def get_nearest_entity(self, hero):
        assert(isinstance(hero, RoundEntity))
        res = None
        _min_dis = 1e9
        for _ in self.roundEntityList:
            assert(isinstance(_, RoundEntity))
            if _.team != self.team_num:
                _dis = M.dist_e(hero, _) - _.attackRange
                if _dis < _min_dis:
                    _min_dis = _dis
                    res = _
        return _min_dis, res

    def get_hero(self):
        if self.hero_num == 0:
            self.hero_num += 1
            return HeroType.IRONMAN.value
        else:
            self.hero_num += 1
            return HeroType.VALKYRIE.value

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
    def num_front(entity):
        assert(isinstance(entity, RoundEntity))
        return 1 - entity.team - entity.team


def process(g):
    debug_in = '{}'.format('-')
    g.round_init()
    Time.set()
    if g.roundType < 0:
        _act = g.get_hero()
        print(_act if debug_in else '{} {}'.format(_act, debug_in))
        return
    else:
        for hero_idx in range(g.hero_num):
            _act = None
            hero = g.me_heros[hero_idx]
            op_tower = g.op_towers[0]
            assert(isinstance(hero, RoundEntity))
            # ======================================= FIGHT =======================================
            G.sort_front(g.me_units)
            _x, _y = g.basePos[0] - G.num_front(hero) * 10, g.basePos[1]
            for unit in g.me_units:
                assert(isinstance(unit, RoundEntity))
                if unit.health > 75:
                    _x, _y = unit.x - 20 * G.num_front(hero), unit.y
                    if M.dist(_x, _y, op_tower.x, op_tower.y) < op_tower.attackRange:
                        _x = op_tower.x - (op_tower.attackRange + 10) * G.num_front(hero)
                    break
            # Attack Op unit
            G.sort_near(g.op_units, hero)
            _unitId = -1
            for unit in g.op_units:
                if M.dist_e(unit, hero) < hero.attackRange and M.dist_e(op_tower, hero) > op_tower.attackRange:
                    _unitId = unit.unitId
            _act = '{} {} {} {}'.format(ActType.MOVE_ATTACK.value, _x, _y, _unitId)
            print(_act if debug_in else '{} {}'.format(_act, debug_in))

# game loop
_g = G()
while True:
    process(_g)
    Time.get()
