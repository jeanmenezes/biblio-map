# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

import os
import sys
import re
import glob
import collections
import itertools
import random
import pygraphviz as pgv

CORPUS = glob.glob('./txt/*.txt')

def conta_e_associa(autores, palavras, textos):
    autores_e_textos, autores_e_palavras, textos_e_autores, textos_e_palavras, palavras_e_autores, palavras_e_textos \
        = (collections.defaultdict(list) for i in range(6))
    rco = re.compile
    for a, p in itertools.izip_longest(autores, palavras, fillvalue=""):
        au = rco(r'(^|\b)' + a + r'\b', flags=re.I|re.M)
        pa = rco(r'(^|\b)' + p + r'\b', flags=re.I|re.M)
        for t in CORPUS:
            txt = str(textos[t])
            if a and a not in autores_e_textos[a]:
                if au.findall(txt):
                    autores_e_textos[a].append(t[6:-4])
                    textos_e_autores[t].append(a)
            if p and p not in textos_e_palavras[t]:
                if pa.findall(txt):
                    textos_e_palavras[t].append(p)
                    palavras_e_textos[p].append(t[6:-4])
    for tx in CORPUS:
        for au in autores:
            if tx[6:-4] in autores_e_textos[au]:
                autores_e_palavras[au] = textos_e_palavras[tx]
                for pa in autores_e_palavras[au]:
                    palavras_e_autores[pa].append(au)
    return [autores_e_textos, autores_e_palavras, textos_e_autores, textos_e_palavras, palavras_e_autores, palavras_e_textos]

def cria_assocs():
    textos = le_textos()
    palavras = palavras_chave()
    print "\tcriando autores..."
    with open('authors.txt') as aut:
        autores = [x.strip() for x in aut.readlines()]
    print "\tcontando e associando..."
    return conta_e_associa(autores, palavras, textos)


def palavras_chave():
    print "\tlistando palavras-chave..."
    with open('keywords.txt') as chaves:
        return [x.strip() for x in chaves.readlines()]

def le_textos():
    textos = collections.defaultdict(list)
    print "\tlendo textos..."
    for item in CORPUS:
        with open(item) as txt:
            textos[item] = '\n'.join(str(x) for x in txt.readlines())
    return textos


def gera_graficos():
    dics = cria_assocs()
    autores_e_textos, autores_e_palavras, textos_e_autores, textos_e_palavras, palavras_e_autores, palavras_e_textos \
        = (dic for dic in dics)
    print "criando graficos..."
    for a in autores_e_textos.iteritems():
        graf = pgv.AGraph(overlap=False, directed=True, size="36,36", splines=True, pad=1.0)
        graf.node_attr.update(fontsize="8.0", fixedsize=True, style="filled")
        graf.edge_attr.update(arrowsize="0.7")
        graf.add_edges_from([(repr(a[0]), repr(re.sub(r' - ', r'\n', x)[0:50] + "...")) for x in a[1]])
        for p in palavras_e_textos.keys():
            for t in a[1]:
                if t in palavras_e_textos[p]:
                    graf.add_edge(repr(re.sub(r' - ', r'\n', t)[0:50] + "..."), repr(p))
        for n in graf.nodes():
            if not graf.predecessors(n):
                n.attr["root"] = True
                n.attr["style"] = "bold, filled"
                n.attr["shape"] = "doublecircle"
                n.attr["width"] = 1.0
                n.attr["fillcolor"] = "red"
                n.attr["fontcolor"] = "orange"
                for e in graf.out_edges(n):
                    e.attr["style"] = "bold"
                    e.attr["color"] = "red"
            elif not graf.successors(n):
                if len(n.name) > 20:
                    n.attr["shape"] = "square"
                    n.attr["width"] = 0.4
                    n.attr["fillcolor"] = "blue"
                    n.attr["fontcolor"] = "gold2"
                else:
                    n.attr["shape"] = "circle"
                    n.attr["width"] = 0.1
                    n.attr["fillcolor"] = "green"
                    n.attr["fontcolor"] = "black"
            else:
                n.attr["shape"] = "square"
                n.attr["width"] = 0.4
                n.attr["fillcolor"] = "blue"
                n.attr["fontcolor"] = "gold3"
                col = random.randint(1, 8)
                for e in graf.out_edges(n):
                    e.attr["style"] = "solid"
                    e.attr["colorscheme"] = "dark28"
                    e.attr["color"] = col
        graf.draw(repr(a[0]).strip('\'\"') + ".gif", prog="circo")
        graf.clear()


gera_graficos()
