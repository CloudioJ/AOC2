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

def main():

    # Verifica se o número de argumentos está correto
    if (len(sys.argv) != 7):
        print("Usage: python cache_simulator.py <nsets> <bsize> <assoc> <sub> <flag> <tracefile>")
        return

    # Inicializa os vetores de valores e tags da cache com o tamanho da associatividade vezes o número de conjuntos
    cache_value = [0] * (att.assoc * att.nsets)
    cache_tag = [0] * (att.assoc * att.nsets)

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
            print(data[i])

            # Calcula o tag e o index do endereço de memória
            tag = data[i] >> (offset_bits + index_bits)
            index = (data[i] >> offset_bits) & ((1 << index_bits) - 1)

            print(f"Tag: {tag}")
            print(f"Index: {index}")

            # Vê onde vai ser colocado o dado na cache
            cache_value, cache_tag = cache_placement(data[i], index, tag, cache_value, cache_tag)
            att.addCounter()

    print(f"Counter: {att.counter}")

def cache_placement(data, index, tag, cache_value, cache_tag):

    # Se for mapeamento direto, só precisa ver se o valor na cache é 0 ou 1
    if cache_value[index] == 0:

        misses.addCompulsory()
        cache_value[index] = data
        cache_tag[index] = tag

    else:
        if cache_tag[index] == tag:
            att.addHits()
            print(f"HITS = {att.hits}")
        else:
            misses.addConflict()
            cache_tag[index] = tag

    return cache_value, cache_tag


if __name__ == "__main__":
    main()

    print(f"{att.counter} {att.hits/att.counter:.2f} {misses.total/att.counter:.2f} {misses.compulsory/misses.total:.2f} {misses.capacity/misses.total:.2f} {misses.conflict/misses.total:.2f}")
    