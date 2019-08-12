# https://www.codingame.com/ide/puzzle/platinum-rift-episode-2
from queue import PriorityQueue
from random import randint
import sys
import math
import time
class C:
    pass
class M:
    pass
class U:
    @staticmethod
    def debug(msg):
        print('DEBUG: {}'.format(msg), file=sys.stderr)
    @staticmethod
    def search_path(graph, start, end, fun_g=None, fun_h=None):
        # graph is list of list like [[1, 2], [3], [3, 1], [0]]
        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = [None for _ in range(len(graph))]
        cost_so_far = [-1 for _ in range(len(graph))]
        cost_so_far[start] = 0
        c = 0
        while not frontier.empty():
            c += 1
            _, current = frontier.get()
            if current == end: break
            for n in graph[current]:
                if fun_g is None: new_cost = cost_so_far[current] + 1
                else: new_cost = cost_so_far[current] + fun_g(current, n)
                if cost_so_far[n] < 0 or new_cost < cost_so_far[n]:
                    cost_so_far[n] = new_cost
                    if fun_h is None: priority = new_cost + (end - n)
                    else: priority = new_cost + fun_h(n, end)
                    frontier.put((priority, n))
                    came_from[n] = current
        res = [end]
        while res[0] != start:
            res.insert(0, came_from[res[0]])
        # U.debug('{} {} {}'.format(start, end, res))
        return res
    @staticmethod
    def dijsktra(graph, initial):
        """
        :param graph: graph is list of list like [[1, 2], [3], [3, 1], [0]]
        :param initial: initial node
        :return: distance - list of distance to initial node
        :return: path - next node to initial node
        """
        distance = [-1 for _ in range(len(graph))]
        distance[initial] = 0
        path = [n for n in range(len(graph))]
        nodes = set([n for n in range(len(graph))])
        while nodes:
            min_node = None
            for node in nodes:
                if distance[node] >= 0:
                    if min_node is None:
                        min_node = node
                    elif distance[node] < distance[min_node]:
                        min_node = node
            if min_node is None:
                break
            nodes.remove(min_node)
            current_weight = distance[min_node]
            for edge in graph[min_node]:
                weight = current_weight + 1  # graph.distances[(min_node, edge)]
                if distance[edge] < 0 or weight < distance[edge]:
                    distance[edge] = weight
                    path[edge] = min_node
        return distance, path
    @staticmethod
    def searching(graph, initial, max_length, cmp, visited_set=None):
        if visited_set is None:
            initial = [initial]
            visited_set = set()
        if max_length < 0:
            return None
        for node in initial:
            if node in visited_set: continue
            if cmp(node):
                return node
            visited_set.add(node)
            res = U.searching(graph, graph[node], max_length - 1, cmp, visited_set)
            visited_set.remove(node)
            if res: return res
class COMMON:
    def __init__(self):
        self.round = 0
        self.action_str = ''
class GCOMMON(COMMON):
    class Zone:
        def __init__(self, z, o, p0, p1, v, p):
            self.pods = [0, 0]
            self.z_id, self.owner_id, self.pods[0], self.pods[1], self.visible, self.platinum = (z, o, p0, p1, v, p)
        def __str__(self):
            return 'z_id:{}, owner:{} p0:{} p1:{} visable:{}, plat:{}'.format(self.z_id, self.owner_id, self.pods[0], self.pods[1], self.visible, self.platinum)
    def __init__(self):
        COMMON.__init__(self)
        self.player_count, self.my_id, self.zone_count, self.link_count = [int(i) for i in input().split()]
        self.link = [[] for _ in range(self.link_count)]
        self.platinum = 0
        self.zones = [GCOMMON.Zone(0, 0, 0, 0, 0, 0) for _ in range(self.zone_count)]
        self.visable_zones = []
        self.my_pods_zones = []
        for i in range(self.zone_count): input()
        for i in range(self.link_count):
            zone_1, zone_2 = [int(j) for j in input().split()]
            self.link[zone_1].append(zone_2)
            self.link[zone_2].append(zone_1)
    def round_update(self):
        self.round += 1
        self.visable_zones = []
        self.my_pods_zones = []
        self.platinum = int(input())  # your available Platinum
        for i in range(self.zone_count):
            z = GCOMMON.Zone(*[int(j) for j in input().split()])
            self.zones[z.z_id] = z
            if z.visible == 1:
                self.visable_zones.append(z)
            if z.pods[self.my_id] > 0:
                self.my_pods_zones.append(z)
        self.action_str = ''
    def action(self):
        if len(self.action_str) > 0: print(self.action_str)
        else: print('WAIT')
        print('WAIT')
class G(GCOMMON):
    class ZonesState:
        ST_ZONE_LOST = 0
        ST_PLATINUM_LOST = 1
        ST_UNIT_LOST = 2
        class Zone:
            def __init__(self, owner=-1, platinum=-1, update_round=0):
                self.owner = owner
                self.platinum = platinum
                self.update_round = update_round
            def __str__(self):
                return 'owner:{} platinum:{} update_round:{}'.format(self.owner, self.platinum, self.update_round)
        def __init__(self, g):
            assert(isinstance(g, G))
            self.g = g
            self.zones = [self.Zone() for _ in range(g.zone_count)]
        def update(self):
            g = self.g
            for zone in g.visable_zones:
                assert(isinstance(zone, GCOMMON.Zone))
                self.zones[zone.z_id].update_round = self.g.round
                self.zones[zone.z_id].owner = zone.owner_id
                self.zones[zone.z_id].platinum = zone.platinum
        def get_zone(self, z_id):
            return self.zones[z_id]
        def get_zones(self):
            return self.zones
    def __init__(self):
        GCOMMON.__init__(self)
        self.visit_cnt = [0 for _ in range(self.zone_count)]
        self.my_pod_id = self.op_pod_id = None
        self.op_base_path = None
        self.platinum_zones = []
        self.platinum_inc = 0  # increased amount of platinum
        self.platinum_prev = 0  # number of platinum last round
        self.home_pods_est = 10
        self.zones_state = self.ZonesState(self)
    def move(self, number, id_src, id_dest):
        self.action_str += '{} {} {} '.format(number, id_src, id_dest)
        if id_src == self.my_pod_id and id_dest != self.my_pod_id:
            self.home_pods_est -= number
        elif id_src != self.my_pod_id and id_dest == self.my_pod_id:
            self.home_pods_est += number
    def get_base_id(self):
        if self.round != 1: return
        for zone in self.zones:
            assert (isinstance(zone, G.Zone))
            if zone.owner_id == self.my_id:
                self.my_pod_id = zone.z_id
            elif zone.owner_id == 1 - self.my_id:
                self.op_pod_id = zone.z_id
            if self.my_pod_id is not None and self.op_pod_id is not None:
                break
        U.debug('{} {}'.format(self.my_pod_id, self.op_pod_id))
        self.op_base_path = U.dijsktra(self.link, self.op_pod_id)[1]
        self.my_base_path = U.dijsktra(self.link, self.my_pod_id)[1]
    def platinum_monitor(self):
        pod_inc = self.zones[self.my_pod_id].pods[self.my_id] - self.home_pods_est
        platinum_inc = self.platinum - (self.platinum_prev - pod_inc * 20)
        self.platinum_prev = self.platinum
        self.home_pods_est = self.zones[self.my_pod_id].pods[self.my_id]
        U.debug('platinum:{}, platinum_inc: {}, pod_inc:{}'.format(self.platinum, platinum_inc, pod_inc))
    def zones_monitor(self):
        self.zones_state.update()
    def processing(self):
        handled_zone = set()
        def is_zone_platinum(zone_idx):
            if zone_idx in handled_zone: return False
            zone = self.zones_state.get_zone(zone_idx)
            assert(isinstance(zone, G.ZonesState.Zone))
            return True if zone.owner != self.my_id and zone.platinum > 0 else False
        def is_zone_not_visited(zone_idx):
            if zone_idx in handled_zone: return False
            z = self.zones_state.get_zone(zone_idx)
            assert(isinstance(z, G.ZonesState.Zone))
            return True if z.owner != self.my_id else False
        for zone in self.my_pods_zones:
            assert(isinstance(zone, G.Zone))
            handled_zone.add(zone.z_id)
            for i in range(zone.pods[self.my_id]):
                dest_id = U.searching(self.link, zone.z_id, 1, is_zone_platinum)
                if dest_id is not None:
                    handled_zone.add(dest_id)
                    path = U.search_path(self.link, zone.z_id, dest_id)
                    self.move(1, zone.z_id, path[1])
                    continue
                dest_id = U.searching(self.link, zone.z_id, 1, is_zone_not_visited)
                if dest_id is not None:
                    handled_zone.add(dest_id)
                    path = U.search_path(self.link, zone.z_id, dest_id)
                    self.move(1, zone.z_id, path[1])
                    continue
                self.move(zone.pods[self.my_id] - i, zone.z_id, self.op_base_path[zone.z_id])
                break
if __name__ == '__main__':
    _g = G()
    while True:
        _g.round_update()
        if _g.round == 1: _g.get_base_id()
        _g.platinum_monitor()
        _g.zones_monitor()
        _g.processing()
        _g.action()
