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
    Bush = 'Bush'
    Spawn = 'Spawn'


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
        self.itemCost = itemCost
        self.damage = damage
        self.health = health
        self.maxHealth = maxHealth
        self.mana = mana
        self.maxMana = maxMana
        self.moveSpeed = moveSpeed
        self.manaRegeneration = manaRegeneration
        self.isPotion = isPotion


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
        self.me_heros = []
        self.me_units = []
        self.op_heros = []
        self.op_units = []

        self.team_num = int(input())
        self.bushAndSpawnPointCount = int(input())
        for _ in range(self.bushAndSpawnPointCount):
            entity_type, x, y, radius = input().split()
            self.bushAndSpawnPointList.append(
                BushAndSpawn(BushAndSpawnType(entity_type), int(x), int(y), int(radius)))
        self.itemCount = int(input())
        for _ in range(self.itemCount):
            self.itemList.append(Item(*list(map(int, input().split()))))
        self.basePos = (200, 590) if self.team_num == 0 else (1720, 590)
        debug('Team Number:{}'.format(self.team_num))

    def round_init(self):
        self.roundEntityList = []
        self.me_heros = []
        self.me_units = []
        self.op_heros = []
        self.op_units = []
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
            else:
                if item.unitType == UnitType.HERO:
                    self.op_heros.append(item)
                elif item.unitType == UnitType.UNIT:
                    self.op_units.append(item)

    def get_nearest_entity(self, hero):
        assert(isinstance(hero, RoundEntity))
        assert(hero.unitType, UnitType.HERO)
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
    debug_msg = ''
    debug_in = '{}'.format('-')
    g.round_init()
    Time.set()
    if g.roundType < 0:
        _act = HeroType.IRONMAN.value
    else:
        # ======================================= FIGHT =======================================
        hero = g.me_heros[0]
        assert(isinstance(hero, RoundEntity))
        G.sort_front(g.me_units)
        _x, _y = g.basePos, G.HEIGHT // 2
        for unit in g.me_units:
            assert(isinstance(unit, RoundEntity))
            if unit.health > 70:
                _x, _y = unit.x - 30 * G.num_front(hero), unit.y
                break
        G.sort_near(g.op_units, hero)
        _unitId = 0
        for unit in g.op_units:
            if M.dist_e(unit, hero) < hero.attackRange:
                _unitId = unit.unitId
        _act = '{} {} {} {}'.format(ActType.MOVE_ATTACK.value, _x, _y, _unitId)
    print(_act if debug_in else '{} {}'.format(_act, debug_in))
    return debug_msg

# game loop
_g = G()
while True:
    debug(process(_g))
    Time.get()
