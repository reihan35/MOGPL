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

a=0;
zap=[]
for alpha in np.arange (0.02,0.8,0.02):
    cities = (5,21,25)
    k=len(cities)
    
    #recuperation des distances entre villes
    f = open("distances92.txt", "r")
    dis = []
    l1=[]
    while True:
        line = f.readline()
        if re.match("([a-zA-Z]+)",line):
            l1=[]
            for i in range(36):
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
    
    
    print(dis)
    # read all lines at once
    #lines = list(f)
    # Range of plants and warehouses
    nbcont=k+36
    nbvar=36*k
    lignes = range(nbcont)
    colonnes = range(nbvar)
    
    ########################LES CONTRAINTES#############################
    
    #Les contraintes conceranrt le fait qu'une ville n’appartient qu’a un unique secteur et les secteurs forment une partition des n ville
    
    l2=[]
    matrice_contraintes=[]
    for y in range(0,36*k,k):
        l2=[]
        for x in range(36*k):
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
    
        co_pop.append(l2)
    
    
    
    matrice_contraintes.extend(co_pop)
    
    print(matrice_contraintes)
    
    ###########################SECONDE MEMBRE###############################
    #alpha = 0.1
    b = np.ones(36).tolist()
    
    #La somme des populations des villes 
    s = 0
    for i in pop:
    	s = s + i
    
    landa = (1 + alpha) / k 
    print(landa)
    
    for i in range(k):
        b.append(landa * s)
    print(b)
    #print(b)
    
    ######################FONCTION OBJECTIVE################################
    c = []
     
    for j in range(36):
        for i in cities:
            c.append(dis[j][i])
    
    print(c)
    
    ###############################GUROBI####################################
    
    m=Model()   
    
            
    # declaration variables de decision
    x = []
    for i in range(36):
        for j in cities:
      #    for j in range(k):
            x.append(m.addVar(vtype=GRB.BINARY
                              , lb=0, name="x%d_%d" % (i+1,j+1)))
    
    # maj du modele pour integrer les nouvelles variables
    m.update()
    
    obj = LinExpr();
    obj =0
    for j in colonnes:
        #print(i,j)
        obj += c[j] * x[j]
          
    # definition de l'objectif
    m.setObjective(obj,GRB.MINIMIZE)
    
    # Definition des contraintes
    for i in range(0,36):
        print(i)
        m.addConstr(quicksum(matrice_contraintes[i][j]*x[j] for j in colonnes) == b[i], "Contrainte%d" % i)
    
    
    for i in range(36,36+k):
        print(b[i])
        m.addConstr(quicksum(matrice_contraintes[i][j]*x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)
        
        
    # Resolution
    m.optimize()
    
    
    print("")                
    print('Solution optimale:')
    
    
    #for i in range(36*k):
       # print('x%d'%(i+1), '=', x[i].x)
    """
    k=0;
    for i in range(36):
        for j in cities:
            print('x%d_%d'%(i+1,j+1), '=', x[k].x)
            #print(k)
            k=k+1;
    """  
            
    print("")
    print('Valeur de la fonction objectif :', m.objVal) 
    g =m.write("q.lp")
    zap.append(m.objVal)
plt.plot(zap)
plt.show()