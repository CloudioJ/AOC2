import sys
import numpy as np
import random as rd
from collections import deque

# Começa uma classe para os atributos de entrada
class Attributes:
    def __init__(self, nsets, bsize, assoc, sub, flag, file):
        self.nsets = nsets
        self.bsize = bsize
        self.assoc = assoc
        self.sub = sub
        self.flag = flag
        self.file = file
        self.hits = 0
        self.counter = 0

    def addHits(self):
        self.hits += 1
    
    def addCounter(self):
        self.counter += 1

# Cria um objeto da classe Attributes com os atributos de entrada
att = Attributes(
    int(sys.argv[1]), 
    int(sys.argv[2]), 
    int(sys.argv[3]), 
    sys.argv[4], 
    int(sys.argv[5]), 
    sys.argv[6]
)

# Começa uma classe para os misses
class Misses:
    def __init__(self):
        self.compulsory = 0
        self.conflict = 0
        self.capacity = 0
        self.total = 0

    def addCompulsory(self):
        self.compulsory += 1
        self.total += 1

    def addConflict(self):
        self.conflict += 1
        self.total += 1

    def addCapacity(self):
        self.capacity += 1
        self.total += 1

# Cria um objeto da classe Misses
misses = Misses()
full = 0

def main():

    # Verifica se o número de argumentos está correto
    if (len(sys.argv) != 7):
        print("Usage: python cache_simulator.py <nsets> <bsize> <assoc> <sub> <flag> <tracefile>")
        return

    # Inicializa os vetores de valores e tags da cache com o tamanho da associatividade vezes o número de conjuntos
    cache_val = [[0] * att.assoc for _ in range(att.nsets)]
    cache_tag = [[0] * att.assoc for _ in range(att.nsets)]
    
    # Calcula o número de bits de offset, index e tag
    offset_bits = int(np.log2(att.bsize))
    index_bits = int(np.log2(att.nsets))
    tag_bits = 32 - offset_bits - index_bits

    # Abre o arquivo de entrada e lê os dados em formato big endian
    file = open(att.file, "rb")
    data = np.fromfile(file, dtype=">u2")

    # Itera sobre os dados do arquivo de entrada
    for i in range(0, data.size):   

        # Se for um endereço de memória ímpar, é um dado, se não vai ser um 0, foi a forma que achei de funcionar hehe
        if i % 2 != 0:
            # print(data[i])

            # Calcula o tag e o index do endereço de memória
            tag = data[i] >> (offset_bits + index_bits)
            index = (data[i] >> offset_bits) & ((1 << index_bits) - 1)

            # Vê onde vai ser colocado o dado na cache
            cache_val, cache_tag = cache_placement(index, tag, cache_val, cache_tag)
            att.addCounter()

    # print(f"Counter: {att.counter}")

def split_list(a_list, index):
    return a_list[:index], a_list[index:]

def rotate_list(a_list):
    a_list = deque(a_list)
    a_list.rotate(-1)
    return list(a_list)

def cache_placement(index, tag, cache_val, cache_tag):

    # Flag serve para não colocar o mesmo dado na cache mais de uma vez
    flag = 0

    # Checa toda a cache pra ver se esta cheia
    full = all(cache_val[index])

    # Itera baseado no numero de associatividade
    for i in range(att.assoc):
        # Para cada item checa para se esta vazio e faz um miss compulsório, adicionando o dado
        if cache_val[index][i] == 0 and flag == 0:
            misses.addCompulsory()
            cache_val[index][i] = 1
            cache_tag[index][i] = tag
            flag = 1

        # Se ja existir o dado então é hit, transformando o flag em 1 pra ele não passar no resto do código
        else:
            if cache_tag[index][i] == tag and flag != 1:
                att.addHits()
                flag = 1
                # Se for LRU então divide a lista em duas e rotaciona a segunda parte, tornando o hit o último da lista
                if att.sub == 'L' and full:
                    part1, part2 = split_list(cache_tag[index], i - 1)
                    part2 = deque(part2)
                    part2.rotate(-1)
                    cache_tag[index] = part1 + list(part2)

    # Se não tiver sido hit e também não foi um miss compulsório então foi miss de conflito ou de capacidade
    if flag == 0:

        # Se ela estiver realmente cheia então é um miss de capacidade senão é um miss de conflito
        if full and att.sub == 'R':
            misses.addCapacity()
            aux = rd.randint(0, 20) % att.assoc
            cache_tag[index][aux] = tag
        
        elif full and att.sub == 'L' or att.sub == 'F':  # Miss de capacidade pro LRU e FIFO
            misses.addCapacity()
            cache_tag[index][0] = tag
            cache_tag[index] = rotate_list(cache_tag[index])

        else:  # Miss de conflito LRU e FIFO
            misses.addConflict()
            if att.sub == 'R':
                aux = rd.randint(0, 20) % att.assoc
                cache_tag[index][aux] = tag

            elif att.sub == 'L' or att.sub == 'F':
                cache_tag[index][0] = tag
                cache_tag[index] = rotate_list(cache_tag[index])

    return cache_val, cache_tag


if __name__ == "__main__":
    main()

    if att.flag == 1:
        print(f"{att.counter} {att.hits/att.counter:.4f} {misses.total/att.counter:.4f} {misses.compulsory/misses.total:.2f} {misses.capacity/misses.total:.2f} {misses.conflict/misses.total:.2f}")
    else:
        print(f"Quantidade de acessos: {att.counter}\nTaxa de acertos: {att.hits/att.counter:.4f}\nTaxa de misses: {misses.total/att.counter:.4f}\nMisses compulsórios: {misses.compulsory/misses.total:.2f}\nMisses de capacidade: {misses.capacity/misses.total:.2f}\nMisses de conflito: {misses.conflict/misses.total:.2f}")