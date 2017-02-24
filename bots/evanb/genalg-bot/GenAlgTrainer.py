import random
import os
import sys
import numpy as np
import subprocess
import multiprocessing
import itertools
import collections
from GenAlgPlayer import N_GENOME_BITS

mutation_rate = 0.003
population = 15 // 3 * 3  # multiple of 3
field_sizes = (15, 15, 15, 24)
match_save_rate = 25

halite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'halite'))
player_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'GenAlgPlayer.py'))
best_genome_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '%d.genome' % N_GENOME_BITS)
)
log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'logs'))


def mate(vec1, vec2):
    i = random.randrange(1, len(vec1) - 1)
    return vec1[:i] + vec2[i:]


def mutate(vec):
    indices = sorted(i for i in range(len(vec)) if random.random() < mutation_rate)
    # print("mutation indices" + str(indices))
    if not indices:
        return vec
    out = vec[:indices[0]]
    for i in indices[1:]:
        out += '1' if random.getrandbits(1) else '0'
        out += vec[len(out): i]
    out += vec[len(out):]
    # print(len(vec))
    # print(len(out))
    return out


def rand_vec():
    return bin(random.getrandbits(N_GENOME_BITS)).replace('0b', '').rjust(N_GENOME_BITS, '0')


def save_genome(path, genome_str):
    with open(path, 'w') as f:
        f.write(genome_str)


def genome_name(vec):
    return ''.join(vec[int(i)] for i in np.linspace(0, len(vec), 16+2)[1:-1])


def run_test(vec1, vec2, vec3, counter=0):
    programs = ['python3 %s %s %s' % (player_path, genome_name(vec), vec)
                for vec in (vec1, vec2, vec3)]
    os.chdir(log_path)
    # print(programs[0].split()[:3])
    field_size = random.choice(field_sizes)
    response = subprocess.run([halite_path, '-q', '-d', '%d %d' % (field_size, field_size)]
                              + programs,
                              stdout=subprocess.PIPE)
    lines = response.stdout.decode('utf-8').split(os.linesep)
    if lines[9] != ' ':
        print('ran bad game')
        return vec1, vec2, vec3
    if counter % match_save_rate != 0:
        logfile = lines[4].split()[0]
        if logfile in os.listdir():
            os.remove(logfile)

    positions = tuple(int(line.split()[1]) for line in lines[5:8])
    vecs_positions = zip((vec1, vec2, vec3), positions)
    ordered = [vec for vec, pos in sorted(vecs_positions, key=lambda vp: vp[1])]
    return ordered


class GenAlgTrainer:
    def __init__(self):
        self.vecs = []
        if os.path.exists(best_genome_path):
            with open(best_genome_path, 'r') as f:
                prev_best = f.read()
                if len(prev_best) == N_GENOME_BITS:
                    self.vecs = [prev_best] * (population // 2)
                    print("loaded previous best genome")
        while len(self.vecs) < population:
            self.vecs.append(rand_vec())

        self.pool = multiprocessing.Pool(processes=3)

    def save_best_fitnesses(self):
        random.shuffle(self.vecs)
        win_counter = collections.Counter()
        games_counter = collections.Counter()
        for a, b in itertools.combinations(self.vecs, 2):
            ordered = run_test(a, b, rand_vec())
            win_counter.update((ordered[0],))
            games_counter.update(ordered[:3])
        vec, wins = win_counter.most_common(1)[0]
        print("most wins at end is", wins, "/", games_counter.get(vec))

        with open(best_genome_path, 'w') as f:
            f.write(vec)
        print("wrote best genome to", best_genome_path)

    def train(self, n_generations):
        counter = 0
        for gen in range(n_generations+1):
            sys.stdout.writelines("\rGeneration %d / %d" % (gen, n_generations))
            random.shuffle(self.vecs)
            inputs = []
            for i in range(0, population-2, 3):
                vecs = self.vecs[i:i+3]
                inputs.append(vecs + [counter])
                counter += 1

            results = self.pool.starmap(run_test, inputs)
            for ordered_list in results:
                self.process_test(ordered_list)
        print()  # send newline

    def process_test(self, ordered_vecs):
        parents = [ordered_vecs[0], ordered_vecs[1]]
        random.shuffle(parents)
        child = mutate(mate(parents[0], parents[1]))
        self.vecs.remove(ordered_vecs[2])
        self.vecs.append(child)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Pass in a number of training iterations")
        exit()

    train_iterations = int(sys.argv[1])

    print("number of genome bits =", N_GENOME_BITS)
    print("average mutations =", N_GENOME_BITS*mutation_rate)

    # train strategies
    trainer = GenAlgTrainer()
    trainer.train(train_iterations)

    print("final ranking of strategies...")
    trainer.save_best_fitnesses()
