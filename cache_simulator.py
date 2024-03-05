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

#cria uma lista duplamente encadeada, por causa dos blocos, pra armazenar os indices e os blocos
class Node:
    def __init__(self, index):
        self.index = index
        self.next = None
        self.prev = None

cache_list = [[None] * att.assoc for _ in range(att.nsets)]

class Sub:
    def __init__(self):
        self.head = None
        self.tail = None

    def add(self, index):
        new_node = Node(index)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node

    def move(self, node):
        if node == self.tail:
            return
        if node == self.head:
            self.head = node.next
            self.head.prev = None
        else:
            node.prev.next = node.next
            node.next.prev = node.prev
        node.next = None
        node.prev = self.tail
        self.tail.next = node
        self.tail = node

    def remove(self):
        if self.head is None:
            return None
        removed = self.head.index
        self.head = self.head.next
        if self.head is not None:
            self.head.prev = None
        else:
            self.tail = None
        return removed

def main():
    
    sub_cache = Sub()
    full = 0
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

    # print(offset_bits)  
    # print(index_bits)
    # print(tag_bits)

    # Abre o arquivo de entrada e lê os dados em formato big endian
    file = open(att.file, "rb")
    data = np.fromfile(file, dtype=">u2")
    
    # print(data.size)
    # print(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])

    sub_cache = Sub()
    # Itera sobre os dados do arquivo de entrada
    for i in range(0, data.size):   

        # Se for um endereço de memória ímpar, é um dado, se não vai ser um 0, foi a forma que achei de funcionar hehe
        if i % 2 != 0:
            # print(data[i])

            # Calcula o tag e o index do endereço de memória
            tag = data[i] >> (offset_bits + index_bits)
            index = (data[i] >> offset_bits) & ((1 << index_bits) - 1)

            # Vê onde vai ser colocado o dado na cache
            cache_val, cache_tag = cache_placement(index, tag, cache_val, cache_tag, sub_cache)
            att.addCounter()

    # print(f"Counter: {att.counter}")

def cache_placement(index, tag, cache_val, cache_tag, sub_cache):

    # Flag serve para não colocar o mesmo dado na cache mais de uma vez
    flag = 0

    # Checa toda a cache pra ver se esta cheia
    full = all(cache_val)

    # Itera baseado no numero de associatividade
    for i in range(att.assoc):
        # Para cada item checa para se esta vazio e faz um miss compulsório, adicionando o dado
        if cache_val[index][i] == 0 and flag == 0:
            misses.addCompulsory()
            cache_val[index][i] = 1
            cache_tag[index][i] = tag
            flag = 1
            sub_cache.add(index)

        # Se ja existir o dado então é hit, transformando o flag em 1 pra ele não passar no resto do código
        else:
            if cache_tag[index][i] == tag and flag != 1:
                att.addHits()
                flag = 1
                if att.sub == 'L':
                    sub_cache.move(sub_cache.head)

    # Se não tiver sido hit e também não foi um miss compulsório então foi miss de conflito ou de capacidade
    if flag == 0:

        # Se ela estiver realmente cheia então é um miss de capacidade senão é um miss de conflito
        if full and att.sub == 'R':
            misses.addCapacity()
            aux = rd.randint(0, 20) % att.assoc
            cache_tag[index][aux] = tag
        
        elif full and att.sub == 'L':  # Miss de capacidade pro LRU
            misses.addCapacity()
            removed_index = sub_cache.head.index
            sub_cache.remove()  # Remove o primeiro bloco
            cache_val[index][removed_index] = 1  # Deixa um bit válido pro novo bloco
            cache_tag[index][removed_index] = tag  # Deixa o tag pro novo bloco
            sub_cache.add(index)  # Adiciona o novo bloco no final da lista

        elif full and att.sub == 'F':  # Miss de capacidade pro FIFO
            misses.addCapacity()
            removed_index = sub_cache.head.index
            sub_cache.remove() 
            cache_val[index][removed_index] = 1 
            cache_tag[index][removed_index] = tag 
            sub_cache.add(index)

        else:  # Miss de conflito
            misses.addConflict()
            if att.sub == 'R':
                aux = rd.randint(0, 20) % att.assoc
                cache_tag[index][aux] = tag

            elif att.sub == 'L':
                sub_cache.add(index)  # Adiciona o novo bloco no final da lista

            elif att.sub == 'F':
                removed_index = sub_cache.head.index
                sub_cache.remove() 
                cache_val[index][removed_index] = 1  
                cache_tag[index][removed_index] = tag  
                sub_cache.add(index) 

    return cache_val, cache_tag


if __name__ == "__main__":
    main()

    if att.flag == 1:
        print(f"{att.counter} {att.hits/att.counter:.4f} {misses.total/att.counter:.4f} {misses.compulsory/misses.total:.2f} {misses.capacity/misses.total:.2f} {misses.conflict/misses.total:.2f}")
    else:
        print(f"Quantidade de acessos: {att.counter}\nTaxa de acertos: {att.hits/att.counter:.4f}\nTaxa de misses: {misses.total/att.counter:.4f}\nMisses compulsórios: {misses.compulsory/misses.total:.2f}\nMisses de capacidade: {misses.capacity/misses.total:.2f}\nMisses de conflito: {misses.conflict/misses.total:.2f}")