import sys
import numpy as np
import random as rd

class Attributes:
    def __init__(self, nsets, bsize, assoc, sub, flag, file):
        self.nsets = nsets
        self.bsize = bsize
        self.assoc = assoc
        self.sub = sub
        self.flag = flag
        self.file = file

att = Attributes(
    int(sys.argv[1]), 
    int(sys.argv[2]), 
    int(sys.argv[3]), 
    sys.argv[4], 
    int(sys.argv[5]), 
    sys.argv[6]
)

class Misses:
    def __init__(self):
        self.compulsory = 0
        self.conflict = 0
        self.capacity = 0
        self.total = self.compulsory + self.conflict + self.capacity

    def addCompulsory(self):
        self.compulsory += 1

    def addConflict(self):
        self.conflict += 1

    def addCapacity(self):
        self.capacity += 1

misses = Misses()
hits = 0

def main():
    if (len(sys.argv) != 7):
        print("Usage: python cache_simulator.py <nsets> <bsize> <assoc> <sub> <flag> <tracefile>")
        return

    cache_value = [] * (att.assoc * att.nsets)
    cache_tag = [] * (att.assoc * att.nsets)

    offset_bits = int(np.log2(att.bsize))
    index_bits = int(np.log2(att.nsets))
    tag_bits = 32 - offset_bits - index_bits

    print(offset_bits)  
    print(index_bits)
    print(tag_bits)

    file = open(att.file, "rb")
    data = np.fromfile(file, dtype=np.int32)
    
    while (data.size > 0):
        print(data)
        cache_placement(data, tag_bits, index_bits, offset_bits, cache_value, cache_tag)
        data = np.fromfile(file, dtype=np.int32)

def cache_placement(address, tag_bits, index_bits, offset_bits, cache_value, cache_tag):
    vector = np.vectorize(int(address))
    tag = int(address >> (offset_bits + index_bits))
    index = int((address >> offset_bits) & ((1 << index_bits) - 1))

    if cache_value[index] == 0:

        misses.addCompulsory()
        cache_value[index] = 1
        cache_tag[index] = tag

    else:
        if cache_tag[index] == tag:
            hits += 1
        else:
            misses.addConflict()
            cache_tag[index] = tag


if __name__ == "__main__":
    main()
    