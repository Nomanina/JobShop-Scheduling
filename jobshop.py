# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 10:40:27 2022

@author: Nomanina
"""
from os import walk
from graph import Graph
from collections import defaultdict
from itertools import combinations
import time

for i in combinations([5, 16, 23, 29],2):
    print(i)

def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() 
                            if len(locs)>1)

################### functions used to read different instances #####################
f = []
mypath = "C:/Users/Nomanina/Downloads/JSPLIB-master/JSPLIB-master/myInstances/AllVariables"
print(mypath)
for (dirpath, dirnames, filenames) in walk(mypath):
    f.extend(filenames)
    break

def readInstances(path):
    for i in range (len(f)):
        f1 = open(path + "/" + f[i],'r')
        contents = f1.read()
        print(contents)


def spreadData(strArr):
    durees_i = []
    machines_i = []
    for j in range(len(strArr)):
        if(j%2 == 0):
            machines_i.append(int(strArr[j]))
        else:
            durees_i.append(int(strArr[j]))
    return machines_i,durees_i
            
def readInstance(n):
    durees = []
    machines = []
    f1 = open(mypath + "/" + f[n],'r')
    for i in range (5):
        print(f1.readline())
    while(True):
        line = f1.readline()
        if(not line):
            break
        line = ' '.join(line.split())
        print(line)
        lines = line.split(" ")
        durees_i, machines_i = spreadData(lines)
        durees += durees_i
        machines.append(machines_i) 
    return machines, durees

def initTfin(n):
    machines, durees = readInstance(n)
    s = 0
    for i in range(len(machines)):
        s += sum(machines[i]) 
    return(s)

def makeGraph(n):
    machines, durees = readInstance(n)       
    V = len(machines) * len(machines[0]) + 2
    g = Graph(V)
    n = len(machines[0])
    for i in range(len(machines)):
        for j in range(len(machines[i])):
            if(j == 0):
                g.addEdge(0, n*i + j + 1, 0)
            if(j != len(machines[i]) - 1):
                g.addEdge(n*i + j + 1, n*i + j + 2, machines[i][j])
            else:
                g.addEdge(n*i + j + 1, V - 1 , machines[i][j])
    g1 = Graph(g.V)
    g.copyGraph(g1)
    return g1

def makeListArcs(n):
    machines, durees = readInstance(n)
    listArcs = []
    for dup in sorted(list_duplicates(durees)):
        for c in combinations(dup[1],2):    
            listArcs.append((c[0] + 1, c[1] + 1))
    return listArcs

########################### branch and bound ####################################     
def TestsSondabilite_relaxlin(g, BestTfin, Bestsol, res, status,listArcs):
    TA, TO, TR = False, False, False
    if(status == float("Inf")):
        TA = True
        #print("TA")
    elif(res >= BestTfin): #Test d'optimalite
        TO=True
        #print("TO")
    elif( listArcs == []): #Test de resolution
        TR=True
        #print("TR")
        if (res <= BestTfin):
            Bestsol = status
            BestTfin = res        
    else:
        print("non sondable")
    
    return TA, TO, TR, Bestsol, BestTfin

def ExplorerAutreNoeud_relaxlin(listgraphs, listvals, listedges,listArcs):
    #this node is sondable, go back to parent node then right child if possible    

    stop = False

    #go back to parent node
    graph = listgraphs.pop()
    theval = listvals.pop()
        
    #go to right child if possible, otherwise go back to parent
    while((theval == 0.0) and (len(listgraphs)>= 1)):
        
        graph = listgraphs.pop()
        theval = listvals.pop()
        edge = listedges.pop() 
        edge1 = edge[0]
        edge2 = edge[1]
        graph.remEdge(edge1,edge2)
        listArcs.append((edge2,edge1))
    
    if theval==1.0:
        if(len(listedges) > 0):
            edge = listedges.pop() 
            edge1 = edge[0]
            edge2 = edge[1]
            graph.remEdge(edge1,edge2)
        weightArc = graph.getWeight(edge2, edge2 + 1)
        if(weightArc == -1):
            weightArc = graph.getWeight(edge2, graph.V - 1)
        graph.addEdge(edge2,edge1, weightArc)

        listgraphs.append(graph)
        listedges.append((edge2,edge1))
        listvals.append(0.0)

    else:
        stop = True
    
    return graph,listvals, listedges, stop, listArcs 


def SeparerNoeud_relaxlin(g, listArcs, listgraphs, listvals, listedges):
    # le noeud est non-sondable. Appliquer le critère de séparation pour le séparer en sous-noeuds 
    # et choisir un noeud-fils le plus à gauche   
    
    #choisir un sens
    edge = listArcs.pop()
    e1 = edge[0]
    e2 = edge[1]
    
    
    weightArc = g.getWeight(e1, e1 + 1)
    if(weightArc == -1):
        weightArc = g.getWeight(e1, g.V - 1)
    g.addEdge(e1,e2, weightArc)

    listgraphs.append(g) #stocker l'identite de la variable choisie pour la séparation
    listvals.append(1.0) #stocker la branche choisie, identifiee par la valeur de la variable choisie
    listedges.append((e1,e2))
    return g,listgraphs, listvals, listedges,listArcs

    


def solveInstance(n):
    listedges=[]
    listvals=[]
    listgraphs=[]
    listArcs = []   
    listArcs = makeListArcs(n)   
    g = makeGraph(n)   
    g.printEdges()   
    g.BellmanFord(0)   
    Bestsol=[]   
    BestTfin = initTfin(n)   
    current_node_number=0
    stop = False   
    while(not stop):
    
    
        print("\nNode number ", current_node_number, ": \n-----\n")   
        print("Solve : start ... ")
        #g.printEdges()
        status = g.BellmanFord(0)
        res = status[len(status) - 1]
        print("tfin: ",res)
        print("... end")
        print(" "); print("\nSolution precedemment memorisee ", Bestsol, " avec date de fin ", BestTfin, "\n")
    
        TA, TO, TR, Bestsol, BestTfin = TestsSondabilite_relaxlin(g, BestTfin, Bestsol,res, status, listArcs)
    
        is_node_sondable = TA or TO or TR
        
        if(not is_node_sondable):
            print("--start separation--")
            g,listgraphs, listvals, listedges, listArcs = SeparerNoeud_relaxlin(g, listArcs, listgraphs, listvals, listedges)
        else:
            #listArcs = [2 4;3 6]
            print("--start exploration--")
            g,listvals, listedges, stop, listArcs = ExplorerAutreNoeud_relaxlin(listgraphs, listvals, listedges, listArcs)
            print("--end--")   
        current_node_number = current_node_number + 1
           
    print("\n******\n\nOptimal value = ", BestTfin,"\n\nOptimal t=", Bestsol)
    return BestTfin

############################ tests ##################################
def test1():
    tfins = []
    times = []
    for i in range(10,-2,-1):    
        start = time.time()
        tfins.append(solveInstance(i))
        end = time.time()
        times.append(end - start)
    nbJobs = [job for job in range (20,10,-1)]
    print(nbJobs)
    print(tfins)
    print(times)
    

def main():
    #test1()
    tfins = []
    times = []
    for i in range(len(f)):
        start = time.time()
        tfins.append(solveInstance(i))
        end = time.time()
        times.append(end - start)
    print(times)
    print(tfins)
    
   
        
if __name__ == '__main__':
    main()
