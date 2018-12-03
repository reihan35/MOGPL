#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 17:19:23 2018

@author: 3803008
"""

import re

from gurobipy import *
import numpy as np
import matplotlib.pyplot as plt
import optdistr
import timeit

start = timeit.default_timer()

def gini(x):
    # (Warning: This is a concise implementation, but it is O(n**2)
    # in time and memory, where n = len(x).  *Don't* pass in huge
    # samples!)

    # Mean absolute difference
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # Relative mean absolute difference
    rmad = mad/np.mean(x)
    # Gini coefficient
    g = 0.5 * rmad
    return g

PEv=[]
gin=[]
ginn=[]
def compare(s, t):
    return sorted(s) == sorted(t)

kek=12

citiesmemory=[]
for c1 in range(kek):
    for c2 in range(kek):
        if c2!=c1:
            for c3 in range(kek):
                if c1!=c3 and c2!=c3:
                
                    cities = (c1,c2,c3)
                    for i in range(0,len(citiesmemory),3):
                        if compare([citiesmemory[index] for index in range(3)],cities)==1:
                            break
                    citiesmemory.append(c1)
                    citiesmemory.append(c2)
                    citiesmemory.append(c3)
                    cities=sorted(cities)
                    k=len(cities)
                    
                    #recuperations des populations des villes 
                    f=open("populations92.txt", "r")
                    pop = []
                    while True:
                    	line = f.readline()
                    	if not line:
                    		break
                    	match = re.search('([0-9]+)',line)
                    	pop.append(float(match.group().rstrip("\n\r")))
                    	
                    f.close()
                    
                    n=len(pop)
                    #recuperation des distances entre villes
                    f = open("distances92.txt", "r")
                    dis = []
                    l1=[]
                    while True:
                        line = f.readline()
                        if re.match("([a-zA-Z]+)",line):
                            l1=[]
                            for i in range(n):
                                l1.append(float(f.readline().rstrip("\n\r")))
                            dis.append(l1)
                        if not line:
                            break
                    f.close()
                    
                    #recuperations des populations des villes 
                    f=open("populations92.txt", "r")
                    pop = []
                    while True:
                    	line = f.readline()
                    	if not line:
                    		break
                    	match = re.search('([0-9]+)',line)
                    	pop.append(float(match.group().rstrip("\n\r")))
                    	
                    f.close()
                    
                    
                    #print(dis)
                    # read all lines at once
                    #lines = list(f)
                    # Range of plants and warehouses
                    nbcont=k+n*2
                    nbvar=n*k+1
                    lignes = range(nbcont)
                    colonnes = range(nbvar)
                    
                    ########################LES CONTRAINTES#############################
                    
                    #Les contraintes conceranrt le fait qu'une ville n’appartient qu’a un unique secteur et les secteurs forment une partition des n ville
                    
                    l2=[]
                    matrice_contraintes=[]
                    for y in range(0,n*k,k):
                        l2=[]
                        for x in range(n*k+1):
                            if x >= y and x < y+k:
                                l2.insert(x,1)		
                            else:
                                l2.insert(x,0)
                    
                    
                        matrice_contraintes.append(l2)
                    
                    
                    #Les contraintes concernant la population des villes 
                    co_pop = []
                    l2=[]
                    
                    for i in range(k):
                        l2=[]
                        p=0
                        for j in pop:
                            l2 = l2 + np.zeros(k).tolist()
                            l2[i+k*p]=j
                            p=p+1
                        l2.append(0)
                        co_pop.append(l2)
                    
                    #Les contraintes de la question 2
                    ci = []
                    
                    for j in range(n):
                    	for i in cities:
                    		ci.append(dis[j][i])
                    
                    #print(len(c))
                    
                    m=[]
                    l2 =[]
                    
                    
                    for i in range (0,len(ci),k):
                    	l2 = []	
                    	for z in ci[0:i] :
                    		l2.append(0)
                    	for j in ci[i:i+k]:
                    		l2.append(j)
                    	for e in ci[i+k:len(ci)] :
                    		l2.append(0)
                    	l2.append(-1)
                    	m.append(l2)
                    
                    #print(m)
                    
                    
                    matrice_contraintes.extend(co_pop)
                    matrice_contraintes.extend(m)
                    
                    print(len(matrice_contraintes))
                    print(len(matrice_contraintes[0]))
                    
                    ###########################SECONDE MEMBRE###############################
                    alpha = 0.1
                    b = np.ones(n).tolist()
                    
                    #La somme des populations des villes 
                    s = 0
                    for i in pop:
                    	s = s + i
                    
                    landa = (1 + alpha) / k 
                    #print(landa)
                    
                    for i in range(k):
                        b.append(landa * s)
                    
                    for i in range(n):
                        b.append(0)
                    #print(len(b))
                    
                    ######################FONCTION OBJECTIVE################################
                    c = []
                    epsilon=1e-6
                     
                    for j in range(n):
                        for i in cities:
                            c.append(epsilon*dis[j][i])
                    c.append(1)
                    
                    #print(c)
                    
                    ###############################GUROBI####################################
                    
                    m1=Model()   
                    
                            
                    # declaration variables de decision
                    x = []
                    for i in range(n):
                        for j in cities:
                      #    for j in range(k):
                            x.append(m1.addVar(vtype=GRB.BINARY
                                              , lb=0, name="x%d_%d" % (i+1,j+1)))
                    x.append((m1.addVar(vtype=GRB.CONTINUOUS
                                              , lb=0, name="g")))
                    # maj du modele pour integrer les nouvelles variables
                    m1.update()
                    obj = LinExpr();
                    obj =0
                    for j in colonnes:
                        obj += c[j] * x[j]
                          
                    # definition de l'objectif
                    m1.setObjective(obj,GRB.MINIMIZE)
                    
                    # Definition des contraintes
                    for i in range(0,n):
                        m1.addConstr(quicksum(matrice_contraintes[i][j]*x[j] for j in colonnes) == b[i], "Contrainte%d" % i)
                        #print(i,j)
                    
                    for i in range(n,n+k):
                        m1.addConstr(quicksum(matrice_contraintes[i][j]*x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)
                        
                    for i in range(n+k,n*2+k):
                        m1.addConstr(quicksum(matrice_contraintes[i][j]*x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)
                        
                    # Resolution
                    m1.optimize()
                    
                    """
                    print("")                
                    print('Solution optimale:')
                    
                    
                    #for i in range(36*k):
                        #print('x%d'%(i+1), '=', x[i].x)
                    
                    k=0
                    for i in range(n):
                        for j in cities:
                            print('x%d_%d'%(i+1,j+1), '=', x[k].x)
                            k=k+1;
                    print('g', '=', x[k].x)
                            
                    print("")
                    print('Valeur de la fonction objectif :', m1.objVal) 
                    """
                    ###########################MATTHEWS' PARSING CODE###############################
                    def parseCoord():
                        f = open("coordvilles92.txt", "r")
                        my_text = f.readlines()
                        return map(lambda coords: map(lambda coord : int(coord), re.findall(r'\d+', coords)), my_text)
                    
                    
                    ###########################PE PART###############################
                    
                    Sat=0
                    Satv=[]
                    for j in range(nbvar-1):
                        Sat+= 1/epsilon*c[j] * x[j].x
                        Satv.append(round(1/epsilon*c[j] * x[j].x))
                    SatM=Sat/n
                    MinSat=max(Satv)
                    
                    
                    #exec(open("projet1(1).py").read())
                    (Sat1,Satv1)=optdistr1(cities)
                    #Sat=1e6*(m1.objVal-x[nbvar-1].x)
                    PEv.append(round(1-Sat1/Sat,6))
                    gin.append(round(gini(Satv1),6))
                    ginn.append(round(gini(Satv1),6))
                    #print("PE",'=',PE)
#gin=list(set(gin))
#PEv=list(set(PEv))
gina=np.array(gin)
PEva=np.array(PEv)
fit = np.polyfit(gina,PEva,1)
fit_fn = np.poly1d(fit)
plt.plot(gina,PEva, 'yo', gina, fit_fn(gina), '--k')
                    
#ma =m1.write("qa.lp")
stop = timeit.default_timer()

print('Time: ', stop - start)
print(kek*(kek-1)*(kek-2)*0.1)
