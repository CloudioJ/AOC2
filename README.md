# AOC2

Simulador de Cache

Este é um simulador para entender o funcionamento básico de uma cache, incluindo os processos de busca, escrita e substituição de blocos.
Políticas de Substituição Implementadas:

    Substituição Aleatória (Random - R): Esta política escolhe aleatoriamente um bloco para ser substituído na cache.
    Substituição de Least Recently Used (LRU): Esta política substitui o bloco que foi acessado menos recentemente.
    Substituição First In First Out (FIFO): Esta política substitui o bloco que foi acessado por ordem de entrada.

Como Usar

    Baixe o código-fonte do simulador.
    Execute o arquivo principal da seguinte maneira através do terminal:

php

python cache_simulator.py <nsets> <bsize> <assoc> <sub> <flag> <tracefile>

Onde:

    <nsets> é o número de conjuntos
    <bsize> é o tamanho dos blocos
    <assoc> representa a associatividade
    <sub> é a regra de substituição
    <flag> é o retorno no fim da execução
    <tracefile> é o arquivo de entrada com os dados

    Siga as instruções fornecidas para interagir com o simulador e visualizar o funcionamento da cache com as diferentes políticas de substituição implementadas.

Bibliotecas adicionais

    sys
    numpy
    random
    collections
