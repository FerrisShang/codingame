# https://www.codingame.com/ide/challenge/code-royale
import time
import random
import sys
import math
from enum import Enum


class Owner(Enum):
    Undefined = -1
    Friendly = 0
    Enemy = 1


class StructureType(Enum):
    Empty = -1
    Tower = 1
    Barracks = 2


class Site:
    def __init__(self, siteId, x, y, radius):
        self.siteId = siteId
        self.x = x
        self.y = y
        self.radius = radius


class RoundSite(Site):
    def __init__(self, site, ignore_1, ignore_2, structure_type, owner, param_1, param_2):
        assert(isinstance(site, Site))
        Site.__init__(self, site.siteId, site.x, site.y, site.radius)
        self.structure_type = StructureType(structure_type)
        self.owner = Owner(owner)
        self.param_1 = param_1
        self.param_2 = param_2

    def __str__(self):
        return "ID:{} ({},{}) T:{}".format(self.siteId, self.x, self.y, self.structure_type.name)


class UnitType(Enum):
    QUEEN = -1
    KNIGHT = 0
    ARCHER = 1
    GIANT = 2


class Unit:
    def __init__(self, x, y, owner, unit_type, health):
        self.x = x
        self.y = y
        self.owner = Owner(owner)
        self.unitType = UnitType(unit_type)
        self.health = health

    def __str__(self):
        return "T:{} ({},{})".format(self.unitType, self.x, self.y)


class M:  # math function
    @staticmethod
    def dist(x1, y1, x2, y2):
        return math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))

    @staticmethod
    def dist_e(e1, e2):
        return math.sqrt((e1.x-e2.x)*(e1.x-e2.x)+(e1.y-e2.y)*(e1.y-e2.y))


class U:
    @staticmethod
    def get_nearest_empty_site(me, round_sites):
        max_len = 1e9
        t = min(round_sites, key=lambda x: max_len if x.owner != Owner.Undefined else M.dist_e(me, x))
        if t.owner != max_len:
            return t
        else:
            return None

    @staticmethod
    def get_nearest_unit(me, units, owner, unit_type):
        max_len = 1e9
        t = min(units, key=lambda x: max_len if x.owner != owner or x.unitType != unit_type else M.dist_e(me, x))
        if t.owner != max_len:
            return t
        else:
            return None

    @staticmethod
    def get_site_id(all_sites, structure_type, owner, param_2=0):
        for i in all_sites:
            if i.structure_type == structure_type and i.owner == owner and (i.structure_type == StructureType.Tower or (i.structure_type == StructureType.Barracks and i.param_2 == param_2)):
                return i.siteId

    @staticmethod
    def get_unit_num(all_units, owner, unit_type):
        return sum([1if i.unitType == unit_type and i.owner == owner else 0 for i in all_units])

    @staticmethod
    def get_site_num(all_sites, structure_type, owner, param_2=0):
        return sum([1 if i.structure_type == structure_type and i.owner == owner and
                        (i.structure_type == StructureType.Tower or (i.structure_type == StructureType.Barracks and i.param_2 == param_2))
                        else 0 for i in all_sites])


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


class G:
    WIDTH = 1920
    HEIGHT = 1000
    Q_SPEED = 60
    Q_RADIUS = 30

    def __init__(self):
        # global items
        self.numSites = 0
        self.siteList = []
        self.siteDic = {}

        self.gold = 0
        self.touchedSite = 0
        self.roundUnits = []
        self.roundSites = []
        self.me = None
        self.op = None

    def global_init(self):
        assert(isinstance(self, G))
        self.numSites = int(input())
        for i in range(self.numSites):
            self.siteList.append(Site(*[int(j) for j in input().split()]))
            self.siteDic[self.siteList[i].siteId] = self.siteList[i]

    def round_init(self):
        self.roundUnits = []
        self.roundSites = []
        self.gold, self.touchedSite = [int(i) for i in input().split()]
        for i in range(self.numSites):
            # ignore_1: used in future leagues
            # ignore_2: used in future leagues
            # structure_type: -1 = No structure, 2 = Barracks
            # owner: -1 = No structure, 0 = Friendly, 1 = Enemy
            site_id, ignore_1, ignore_2, structure_type, owner, param_1, param_2 = [int(j) for j in input().split()]
            self.roundSites.append(RoundSite(self.siteDic[site_id], ignore_1, ignore_2, structure_type, owner, param_1, param_2))
        num_units = int(input())
        for i in range(num_units):
            self.roundUnits.append(Unit(*[int(j) for j in input().split()]))
            if self.roundUnits[i].owner == Owner.Friendly and self.roundUnits[i].unitType == UnitType.QUEEN:
                self.me = self.roundUnits[i]
            elif self.roundUnits[i].owner == Owner.Enemy and self.roundUnits[i].unitType == UnitType.QUEEN:
                self.op = self.roundUnits[i]


def process(g):
    act = None
    nearest_site = U.get_nearest_empty_site(g.me, g.roundSites)
    if nearest_site is not None and g.touchedSite == nearest_site.siteId:
        if U.get_site_num(g.roundSites, StructureType.Barracks, Owner.Friendly, 1) < 1:
            act = "BUILD {} BARRACKS-{}".format(g.touchedSite, "ARCHER")
        elif U.get_site_num(g.roundSites, StructureType.Barracks, Owner.Friendly, 0) < 1:
            act = "BUILD {} BARRACKS-{}".format(g.touchedSite, "KNIGHT")
        elif U.get_site_num(g.roundSites, StructureType.Barracks, Owner.Friendly, 2) < 1:
            act = "BUILD {} BARRACKS-{}".format(g.touchedSite, "GIANT")
        else:
            act = "BUILD {} {}".format(g.touchedSite, "TOWER")
    if act is None:
        if nearest_site is not None and sum([1 if x.owner == Owner.Friendly else 0 for x in g.roundSites]) < 10:
            act = "MOVE {} {}".format(nearest_site.x, nearest_site.y)
        else:
            act = "WAIT"
    unit = U.get_nearest_unit(g.me, g.roundUnits, Owner.Enemy, UnitType.KNIGHT)
    if M.dist_e(unit, g.me) < 150:
        act = "MOVE {} {}".format(g.me.x*2-unit.x, g.me.y*2-unit.y)
    print(act)

    site_knight_id = U.get_site_id(g.roundSites, StructureType.Barracks, Owner.Friendly, 0)
    site_archer_id = U.get_site_id(g.roundSites, StructureType.Barracks, Owner.Friendly, 1)
    site_giant_id = U.get_site_id(g.roundSites, StructureType.Barracks, Owner.Friendly, 2)
    if U.get_unit_num(g.roundUnits, Owner.Friendly, UnitType.ARCHER) < 5 and site_archer_id is not None:
        print("TRAIN {}".format(site_archer_id))
    elif U.get_unit_num(g.roundUnits, Owner.Friendly, UnitType.GIANT) < 1 and site_giant_id is not None:
        print("TRAIN {}".format(site_giant_id))
    elif U.get_unit_num(g.roundUnits, Owner.Friendly, UnitType.KNIGHT) < 50 and site_knight_id is not None:
        print("TRAIN {}".format(site_knight_id))
    else:
        print("TRAIN")


if __name__ == '__main__':
    random.seed(0)
    _g = G()
    _g.global_init()
    while True:
        _g.round_init()
        # Time.set()
        process(_g)
        # Time.get()
