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
import pandas as pd

cities =(2,4,15,24,32)
cities=sorted(cities)
k=len(cities)
alpha = 0.1

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

#nombre des villes
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




# Nombre des variables et des contraintes
nbcont=k+n
nbvar=n*k
lignes = range(nbcont)
colonnes = range(nbvar)

########################LES CONTRAINTES#############################

#Les contraintes concernant le fait qu'une ville n’appartient qu’a un unique secteur et les secteurs forment une partition des n villes

l2=[]
matrice_contraintes=[]
for y in range(0,n*k,k):
    l2=[]
    for x in range(n*k):
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


###########################SECONDE MEMBRE###############################
b = np.ones(n).tolist()

#La somme des populations des villes 
s = 0
for i in pop:
	s = s + i

gamma = (1 + alpha) / k 

for i in range(k):
    b.append(gamma * s)

######################FONCTION OBJECTIVE################################
c = []
 
for j in range(n):
    for i in cities:
        c.append(dis[j][i])


###############################GUROBI####################################

m=Model()   

        
# declaration variables de decision
x = []
for i in range(n):
    for j in cities:
        x.append(m.addVar(vtype=GRB.BINARY
                          , lb=0, name="x%d_%d" % (i,j)))

# Mise a jour du modele pour integrer les nouvelles variables
m.update()

obj = LinExpr();
obj =0
for j in colonnes:
    obj += c[j] * x[j]
      
# Definition de l'objectif
m.setObjective(obj,GRB.MINIMIZE)

# Definition des contraintes
for i in range(n):
    m.addConstr(quicksum(matrice_contraintes[i][j]*x[j] for j in colonnes) == b[i], "Contrainte%d" % i)


for i in range(n,n+k):
    m.addConstr(quicksum(matrice_contraintes[i][j]*x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)
    
    
# Resolution
m.optimize()

# Affichage
print("")                
print('Solution optimale:')

k=0;
for i in range(n):
    for j in cities:
        print('x%d_%d'%(i,j), '=', x[k].x)
        k=k+1;
        
print("")
print('Valeur de la fonction objectif :', m.objVal) 


#Satisfaction
Sat1=0 
Satv1=[] 
for j in colonnes:
    Sat1+= c[j] * x[j].x
    if x[j].x==1:
        Satv1.append(c[j] * x[j].x)
SatM1=Sat1/n #Satsfaction moyenne
print("Medium Satisfaction","=",SatM1)
MinSat1=max(Satv1) #Satisfaction minimum
print("Minimum Satisfaction","=",MinSat1)
ind=[i for i, j in enumerate(Satv1) if j == MinSat1]




#Recuperation des coordonnees des villes
data = pd.read_csv('coordvilles92.txt', header=None)
data.columns = ["Villes", "x", "y"]


#Plot

HdS=plt.imread("92.png")
fig, ax = plt.subplots()
ax.imshow(HdS)

def connectpoints(x,y,p1,p2):
    x1, x2 = x[p1], x[p2]
    y1, y2 = y[p1], y[p2]
    plt.plot([x1,x2],[y1,y2],'k-')

plt.plot(data["x"][ind], data["y"][ind], 'bo')
k=0
for i in range(n):
    for j in cities:
        plt.plot(data["x"][j], data["y"][j], 'ro-') 
        if x[k].x==1:
            connectpoints(data["x"],data["y"],i,j)
        k=k+1

print("Worst off:",data["Villes"][ind])
print("Hubs:")
for i in cities:
    print(i,data["Villes"][i])
#Ecriture dans un model LP
m =m.write("projet1.lp")
