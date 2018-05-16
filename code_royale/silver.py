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
    Goldmine = 0
    Tower = 1
    Barracks = 2


class Site:
    def __init__(self, site_id, x, y, radius):
        self.siteId = site_id
        self.x = x
        self.y = y
        self.radius = radius


class RoundSite(Site):
    def __init__(self, site, gold, mine_size, structure_type, owner, param_1, param_2):
        assert(isinstance(site, Site))
        Site.__init__(self, site.siteId, site.x, site.y, site.radius)
        self.structure_type = StructureType(structure_type)
        self.owner = Owner(owner)
        self.param_1 = param_1
        self.param_2 = param_2
        self.gold = gold
        self.mine_size = mine_size

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
    def is_in_enemy_tower(unit, round_sites):
        for x in round_sites:
            if x.owner == Owner.Enemy and x.structure_type == StructureType.Tower and M.dist_e(unit, x) <= x.param_2:
                return True
        return False

    @staticmethod
    def get_nearest_empty_site(me, round_sites, not_in_tower=True):
        t_list = []
        for x in round_sites:
            if x.owner == Owner.Undefined and not (not_in_tower and U.is_in_enemy_tower(x, round_sites)):
                t_list.append(x)
        if len(t_list) > 0:
            return min(t_list, key=lambda s: M.dist_e(me, s))

    @staticmethod
    def get_nearest_unit(me, units, owner, unit_type):
        t_list = []
        for x in units:
            if x.owner == owner and x.unitType == unit_type:
                t_list.append(x)
        if len(t_list) > 0:
            return min(t_list, key=lambda s: M.dist_e(me, s))

    @staticmethod
    def get_nearest_site(me, sites, owner, site_type):
        t_list = []
        for x in sites:
            if x.owner == owner and x.structure_type == site_type:
                t_list.append(x)
        if len(t_list) > 0:
            return min(t_list, key=lambda s: M.dist_e(me, s))

    @staticmethod
    def get_site_id(all_sites, structure_type, owner, param_1=None, param_2=0):
        for i in all_sites:
            if i.structure_type == structure_type and i.owner == owner and (i.structure_type == StructureType.Tower or (i.structure_type == StructureType.Barracks and i.param_2 == param_2 and (param_1 is None or i.param_1 == param_1))):
                return i.siteId

    @staticmethod
    def get_unit_num(all_units, owner, unit_type):
        return sum([1if i.unitType == unit_type and i.owner == owner else 0 for i in all_units])

    @staticmethod
    def get_site_num(all_sites, structure_type, owner, param_2=0):
        return sum([1 if i.structure_type == structure_type and i.owner == owner and (i.structure_type == StructureType.Tower or i.structure_type == StructureType.Goldmine or (i.structure_type == StructureType.Barracks and i.param_2 == param_2)) else 0 for i in all_sites])


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
        self.sites_dict = {}
        self.me = None
        self.op = None
        # custom
        self.roundCnt = 0
        self.war_started = False

    def global_init(self):
        assert(isinstance(self, G))
        self.numSites = int(input())
        for i in range(self.numSites):
            self.siteList.append(Site(*[int(j) for j in input().split()]))
            self.siteDic[self.siteList[i].siteId] = self.siteList[i]

    def round_init(self):
        self.roundCnt += 1
        self.roundUnits = []
        self.roundSites = []
        self.sites_dict = {}
        self.gold, self.touchedSite = [int(i) for i in input().split()]
        for i in range(self.numSites):
            site_id, gold, mine_size, structure_type, owner, param_1, param_2 = [int(j) for j in input().split()]
            self.roundSites.append(RoundSite(self.siteDic[site_id], gold, mine_size, structure_type, owner, param_1, param_2))
            self.sites_dict[site_id] = self.roundSites[i]
        num_units = int(input())
        for i in range(num_units):
            self.roundUnits.append(Unit(*[int(j) for j in input().split()]))
            if self.roundUnits[i].owner == Owner.Friendly and self.roundUnits[i].unitType == UnitType.QUEEN:
                self.me = self.roundUnits[i]
            elif self.roundUnits[i].owner == Owner.Enemy and self.roundUnits[i].unitType == UnitType.QUEEN:
                self.op = self.roundUnits[i]


def process(g):
    debug("{}".format("-------------------------- {} {}".format(g.roundCnt, g.war_started)))
    act = None
    nearest_site = U.get_nearest_empty_site(g.me, g.roundSites)
    debug("Nearest: {}".format(str(nearest_site)))
    if not g.war_started and (g.roundCnt > 100 or g.gold > 222 or g.gold > g.op.health*10):
        g.war_started = True
    if g.touchedSite in g.sites_dict:
        site = g.sites_dict[g.touchedSite]
        if site.structure_type == StructureType.Goldmine and site.gold > 5 and site.param_1 < site.mine_size:
            act = "BUILD {} {}".format(g.touchedSite, "MINE")
        elif site.structure_type == StructureType.Tower and site.owner == Owner.Friendly and site.param_1 < 500:  # Tower max HP 800
            act = "BUILD {} {}".format(g.touchedSite, "TOWER")
    if act is None and nearest_site is not None and g.touchedSite == nearest_site.siteId:
        site = g.sites_dict[g.touchedSite]
        if U.get_site_num(g.roundSites, StructureType.Goldmine, Owner.Friendly) < 1 and site.gold > 5:
            act = "BUILD {} {}".format(g.touchedSite, "MINE")
        elif U.get_site_num(g.roundSites, StructureType.Tower, Owner.Friendly, 1) < 2:
            act = "BUILD {} {}".format(g.touchedSite, "TOWER")
        elif U.get_site_num(g.roundSites, StructureType.Barracks, Owner.Friendly, 1) < 0:
            act = "BUILD {} BARRACKS-{}".format(g.touchedSite, "ARCHER")
        elif U.get_site_num(g.roundSites, StructureType.Barracks, Owner.Friendly, 0) < 1:
            act = "BUILD {} BARRACKS-{}".format(g.touchedSite, "KNIGHT")
        elif U.get_site_num(g.roundSites, StructureType.Barracks, Owner.Friendly, 2) < 0:
            act = "BUILD {} BARRACKS-{}".format(g.touchedSite, "GIANT")
        elif U.get_site_num(g.roundSites, StructureType.Goldmine, Owner.Friendly) < 2 and site.gold > 5:
            act = "BUILD {} {}".format(g.touchedSite, "MINE")
        elif U.get_site_num(g.roundSites, StructureType.Barracks, Owner.Friendly, 0) < 2:
            act = "BUILD {} BARRACKS-{}".format(g.touchedSite, "KNIGHT")
        elif U.get_site_num(g.roundSites, StructureType.Tower, Owner.Friendly, 1) < 3:
            act = "BUILD {} {}".format(g.touchedSite, "TOWER")
        elif U.get_site_num(g.roundSites, StructureType.Goldmine, Owner.Friendly) < 4 and site.gold > 5:
            act = "BUILD {} {}".format(g.touchedSite, "MINE")
        else:
            act = "BUILD {} {}".format(g.touchedSite, "TOWER")
    if act is None and g.touchedSite in g.sites_dict:
        site = g.sites_dict[g.touchedSite]
        if site.structure_type == StructureType.Tower and site.owner == Owner.Friendly and site.param_1 < 500:  # Tower max HP 800
            act = "BUILD {} {}".format(g.touchedSite, "TOWER")
    if act is None:
        if nearest_site is not None and sum([1 if x.owner == Owner.Friendly else 0 for x in g.roundSites]) < 10:
            debug("Go around(HP:{})".format(g.me.health))
            act = "MOVE {} {}".format(nearest_site.x, nearest_site.y)
        else:
            act = "WAIT"
    unit = U.get_nearest_unit(g.me, g.roundUnits, Owner.Enemy, UnitType.KNIGHT)
    if unit and M.dist_e(unit, g.me) < 450 - g.me.health * 2 and (act == "WAIT" or g.me.health < 80):
        debug("Escape from {} (My HP:{})".format(str(unit), g.me.health))
        nearest_tower = U.get_nearest_site(g.me, g.roundSites, Owner.Friendly, StructureType.Tower)
        if nearest_tower and M.dist_e(nearest_tower, g.me) > 200:
            act = "MOVE {} {}".format(nearest_tower.x, nearest_tower.y)
        else:
            act = "MOVE {} {}".format(g.me.x+(g.me.x-unit.x)*50, g.me.y+(g.me.y-unit.y)*50)
    print(act)
    debug("{}".format(act))

    site_knight_id = U.get_site_id(g.roundSites, StructureType.Barracks, Owner.Friendly, 0, 0)
    site_archer_id = U.get_site_id(g.roundSites, StructureType.Barracks, Owner.Friendly, 0, 1)
    site_giant_id = U.get_site_id(g.roundSites, StructureType.Barracks, Owner.Friendly, 0, 2)
    act = None
    if U.get_unit_num(g.roundUnits, Owner.Friendly, UnitType.ARCHER) < 0 and site_archer_id is not None:
        act = "TRAIN {}".format(site_archer_id) if g.gold >= 100 and g.sites_dict[site_archer_id].param_1 == 0 else "TRAIN"
    elif U.get_unit_num(g.roundUnits, Owner.Friendly, UnitType.GIANT) < 2 and site_giant_id is not None:
        act = "TRAIN {}".format(site_giant_id) if g.gold >= 140 and g.sites_dict[site_giant_id].param_1 == 0 else "TRAIN"
    elif U.get_unit_num(g.roundUnits, Owner.Friendly, UnitType.KNIGHT) < 50 and site_knight_id is not None:
        act = "TRAIN {}".format(site_knight_id) if g.gold >= 80 and g.sites_dict[site_knight_id].param_1 == 0 else "TRAIN"
    if act is None:
        act = "TRAIN"
    if not g.war_started:
        act = "TRAIN"
    print(act)
    debug("{}".format(act))


if __name__ == '__main__':
    random.seed(0)
    _g = G()
    _g.global_init()
    while True:
        _g.round_init()
        # Time.set()
        process(_g)
        # Time.get()
