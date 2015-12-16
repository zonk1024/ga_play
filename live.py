#!/usr/bin/env python

from math import sqrt
from random import randint, sample

# rough percentage of the groupings that live
DIAGNALS = True
SURVIVABILITY = 10
LIMIT = 10
POP_SIZE = 100

GRID = '''73167176531330624919225119674426574742355349194934
96983520312774506326239578318016984801869478851843
85861560789112949495459501737958331952853208805511
12540698747158523863050715693290963295227443043557
66896648950445244523161731856403098711121722383113
62229893423380308135336276614282806444486645238749
30358907296290491560440772390713810515859307960866
70172427121883998797908792274921901699720888093776
65727333001053367881220235421809751254540594752243
52584907711670556013604839586446706324415722155397
53697817977846174064955149290862569321978468622482
83972241375657056057490261407972968652414535100474
82166370484403199890008895243450658541227588666881
16427171479924442928230863465674813919123162824586
17866458359124566529476545682848912883142607690042
24219022671055626321111109370544217506941658960408
07198403850962455444362981230987879927244284909188
84580156166097919133875499200524063689912560717606
05886116467109405077541002256983155200055935729725
71636269561882670428252483600823257530420752963450'''.split('\n')

GRID2 = ''
for y, line in enumerate(GRID):
    for x, value in enumerate(line):
        GRID2 += str(randint(0, 9))
    GRID2 += '\n'
GRID = GRID2[:-1].split('\n')

LEN_X = len(GRID[0])
LEN_Y = len(GRID)


def colorize(text, color='red'):
    colors = {
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'darkcyan': '\033[36m',
        'blue': '\033[94m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'bold': '\033[1m',
        'underline': '\033[4m',
    }
    return '{}{}\033[0m'.format(colors.get(color, 'red'), text)


class Node(object):
    nodes = {}

    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.nodes[(x, y)] = self

    def neighbors(self, banned=None, diagnals=DIAGNALS):
        if banned is None:
            banned = set()
        output = {}

        try:
            output[(self.x - 1, self.y)] = self.nodes[(self.x - 1, self.y)]
        except KeyError:
            pass
        try:
            output[(self.x + 1, self.y)] = self.nodes[(self.x + 1, self.y)]
        except KeyError:
            pass
        try:
            output[(self.x, self.y - 1)] = self.nodes[(self.x, self.y - 1)]
        except KeyError:
            pass
        try:
            output[(self.x, self.y + 1)] = self.nodes[(self.x, self.y + 1)]
        except KeyError:
            pass

        if diagnals:
            try:
                output[(self.x - 1, self.y - 1)] = self.nodes[(self.x - 1, self.y - 1)]
            except KeyError:
                pass
            try:
                output[(self.x + 1, self.y  - 1)] = self.nodes[(self.x + 1, self.y - 1)]
            except KeyError:
                pass
            try:
                output[(self.x - 1, self.y + 1)] = self.nodes[(self.x - 1, self.y + 1)]
            except KeyError:
                pass
            try:
                output[(self.x + 1, self.y + 1)] = self.nodes[(self.x + 1, self.y + 1)]
            except KeyError:
                pass

        for key in output:
            if key in banned:
                del(output[key])

        return output

    @property
    def coords(self):
        return self.x, self.y

    @classmethod
    def get_node(cls, *coords):
        if type(coords[0]) == cls:
            return coords[0]
        if len(coords) == 2:
            return cls.nodes[(coords[0], coords[1])]
        return cls.nodes[coords[0]]


class Grouping(object):
    SIZE = 40

    def __init__(self, *nodes, **kwargs):
        self.size = kwargs.get('size', self.SIZE)
        self.nodes = list(nodes)

    def mutate(self):
        new_nodes = sample(self.nodes, len(self.nodes) - 1)
        new = Grouping(*new_nodes, size=self.size)
        new.add_random_neighbor()
        return new

    def is_valid(self):
        visited = set([self.nodes[0].coords])
        neighbors = set(self.nodes[0].neighbors())
        to_visit = set([n.coords for n in self.nodes[1:]])
        while len(to_visit.intersection(neighbors)) > 0:
            visited |= to_visit.intersection(neighbors)
            to_visit -= visited
            neighbors_list = [Node.get_node(v).neighbors().keys() for v in list(visited)]
            neighbors = set([node for sub in neighbors_list for node in sub])
        if to_visit:
            return False
        return True

    def neighbors(self, banned=None):
        if banned is None:
            banned = set()
        output = set()

        for node in self.nodes:
            for neighbor in node.neighbors().keys():
                if neighbor not in banned and neighbor not in self:
                    output.add(neighbor)
        return [Node.get_node(coords) for coords in output]

    def add_random_neighbor(self):
        new_node = sample(self.neighbors(), 1)[0]
        self.nodes.append(new_node)

    @property
    def fitness(self):
        output = 1
        for node in self.nodes:
            output *= node.value
        return output

    @classmethod
    def generate(cls, size=None):
        if size is None:
            size=cls.SIZE
        x = randint(0, LEN_X - 1)
        y = randint(0, LEN_Y - 1)
        first_node = Node.get_node(x, y)
        new = cls(first_node, size=size)
        while len(new.nodes) < new.size:
            new.add_random_neighbor()
        return new

    def __eq__(self, other):
        return all(n1.coords == n2.coords for n1, n2 in zip(self.nodes, other.nodes))

    def __contains__(self, arg):
        if type(arg) is Node:
            return node in self.nodes
        return Node.get_node(arg) in self.nodes

    def __repr__(self):
        return '{} {}'.format(self.fitness, [(n.coords, n.value) for n in p.groupings[0].nodes])

    def __str__(self):
        output = ''
        for y, line in enumerate(GRID):
            for x, value in enumerate(GRID[y]):
                if (x, y) in self:
                    output += colorize(GRID[y][x])
                else:
                    output += colorize(GRID[y][x], 'blue')
            output += '\n'
        return output


class Population(object):
    best_score = 0
    best_group = tuple()

    def __init__(self, *groupings, **kwargs):
        self.size = kwargs.get('size', POP_SIZE)
        self.groupings = list(groupings)
        while len(self.groupings) < self.size:
            self.groupings.append(Grouping.generate())
        self.groupings = sorted(self.groupings, key=lambda x: -x.fitness)

    def next_generation(self):
        output = self.groupings[:len(self.groupings)/SURVIVABILITY]
        for node in output[:]:
            plus = len(output) + 2
            while len(output) < plus:
                new = node.mutate()
                if new.is_valid():
                    output.append(new)
        while len(output) < self.size:
            output.append(Grouping.generate())
        return Population(*output, size=self.size)


for y, line in enumerate(GRID):
    for x, value in enumerate(line):
        n = Node(x, y, int(value))
print 'Loaded Nodes\n'


if __name__ == '__main__':
    p = Population()
    max_v = 0
    no_change = 0
    generation = 0
    #while no_change < LIMIT:
    while p.groupings[0].fitness != p.groupings[len(p.groupings)/SURVIVABILITY].fitness or generation < 30:
        p = p.next_generation()
        generation += 1
        if max_v < p.groupings[len(p.groupings)/SURVIVABILITY].fitness:
            max_v = p.groupings[len(p.groupings)/10].fitness
            no_change = 0
        else:
            no_change += 1
        #print 'generation: {}  top fitness: {}  lowest pass: {}  no_change: {}/{}'.format(generation, p.groupings[0].fitness, p.groupings[len(p.groupings)/SURVIVABILITY].fitness, no_change, LIMIT)
        print 'generation: {}  top fitness: {}  lowest pass: {}'.format(generation, p.groupings[0].fitness, p.groupings[len(p.groupings)/SURVIVABILITY].fitness)
        print str(p.groupings[0])

    for i, grouping in enumerate(p.groupings[:9]):
        #print 'grouping\n', str(grouping)
        print 'grouping', repr(grouping)

    # g = Grouping.generate()
    # print g
    # print g.mutate()
