import sys
import numpy as np
import random as rd

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

    print(offset_bits)  
    print(index_bits)
    print(tag_bits)

    # Abre o arquivo de entrada e lê os dados em formato big endian
    file = open(att.file, "rb")
    data = np.fromfile(file, dtype=">u2")
    
    print(data.size)
    print(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])

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


    print(f"Counter: {att.counter}")

def cache_placement(index, tag, cache_val, cache_tag):

    flag = 0

    for i in range(att.assoc):
        if cache_val[index][i] == 0 and flag == 0:
            misses.addCompulsory()
            cache_val[index][i] = 1
            cache_tag[index][i] = tag
            flag = 1
        else:
            if cache_tag[index][i] == tag and flag != 1:
                att.addHits()
                flag = 1
        
    if flag == 0:
        for k in range(att.nsets):
            for j in range(att.assoc):
                if cache_val[k][j] == 0:
                    full = 0
                else:
                    full = 1


        if full == 1 and att.sub == 'R':
            misses.addCapacity()
            aux = rd.randint(0, 10) % att.assoc
            cache_tag[index][aux] = tag
        elif full == 0 and att.sub == 'R':
            misses.addConflict() 
            aux = rd.randint(0, 10) % att.assoc
            cache_tag[index][aux] = tag

    return cache_val, cache_tag


if __name__ == "__main__":
    main()

    print(f"{att.counter} {att.hits/att.counter:.4f} {misses.total/att.counter:.4f} {misses.compulsory/misses.total:.4f} {misses.capacity/misses.total:.4f} {misses.conflict/misses.total:.4f}")