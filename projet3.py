#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from gurobipy import *
import numpy as np
import timeit
import optdistr

start = timeit.default_timer()


k=5
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

#print(dis)
# read all lines at once
#lines = list(f)
# Range of plants and warehouses
nbcont=n**2+3*n+1
nbvar=n**2+n+1
lignes = range(nbcont)
colonnes = range(nbvar)

########################LES CONTRAINTES#############################

#Les contraintes concernant le fait qu'une ville n’appartient qu’a un unique secteur et les secteurs forment une partition des n ville

l2=[]
matrice_contraintes=[]
for y in range(0,n**2,n):
    l2=[]
    for x in range(nbvar):
        if x >= y and x < y+n:
            l2.insert(x,1)        
        else:
            l2.insert(x,0)


    matrice_contraintes.append(l2)

#Les contraintes concernant la population des villes 
co_pop = []
l2=[]

for i in range(n):
    l2=[]
    p=0
    for j in pop:
        l2 = l2 + np.zeros(n,dtype=np.int).tolist()
        l2[i+n*p]=j
        p=p+1
    l2.extend(np.zeros(n+1).tolist())
    co_pop.append(l2)

#print(co_pop)

#La contrainte concernant le nombre des secteurs j1 + j2 + ... jn = k
su = np.ones(n,).tolist()
su2 = np.zeros(nbvar - n).tolist()
su2.extend(su)
 

#Les contraintes concernant le fait que xij <= ja
l3 = []
l2 = []
for y in range(0,n**2):
    l2=[]
    for x in range(nbvar):
        if x == y :
            l2.insert(x,1)
        else:
            if x == n**2 + 1 + y%36 :
                l2.insert(x,-1)
            else:
                 l2.insert(x,0)
    l3.append(l2)

#print(l3)
   


#Les contraintes de la question 2

'''
ci = []
for j in range(n):
    for i in cities:
        ci.append(dis[j][i])
#print(len(c))
'''
m=[]
l5 =[]

for i in range (len(dis)):
    for j in range(len(dis)):
        l5.append(dis[i][j])



l2 = []
for i in range (0,len(l5),n):
    l2 = []    
    for z in l5[0:i] :
        l2.append(0)
    for j in l5[i:i+n]:
        l2.append(j)
    for e in l5[i+n:len(l5)] :
        l2.append(0)
    l2.append(-1)
    l2.extend(np.zeros(n).tolist())
    m.append(l2)

 #print(m)


matrice_contraintes.extend(co_pop)
matrice_contraintes.append(su2)
matrice_contraintes.extend(l3)
matrice_contraintes.extend(m)

#print(matrice_contraintes)
#print(len(matrice_contraintes[0]))

###########################SECONDE MEMBRE###############################
alpha = 0.1
b = np.ones(n).tolist()

#La somme des populations des villes 
s = 0
for i in pop:
    s = s + i

landa = (1 + alpha) / k 
#print(landa)

for i in range(n):
    b.append(landa * s)
  
b.append(k)

b2 = np.zeros(n**2+n).tolist() #contrainte 4 et 5

b.extend(b2)



#b.append(1) #contrainte de nombres de villes 

#print(b)


######################FONCTION OBJECTIVE################################

c = []
epsilon=1e-6
 
for j in range(n):
    for i in range(n):
        c.append(epsilon*dis[j][i])
c.append(1)
for i in range(n):
        c.append(0)
cici=c
#print(c)




###############################GUROBI####################################

m3=Model()   

        
# declaration variables de decision
x = []
for i in range(n):
    for j in range(n):
        x.append(m3.addVar(vtype=GRB.BINARY
                          , lb=0, name="x%d_%d" % (i+1,j+1)))
x.append((m3.addVar(vtype=GRB.CONTINUOUS
                          , lb=0, name="g")))
for j in range(n):
        x.append(m3.addVar(vtype=GRB.BINARY
                          , lb=0, name="j%d" % (j+1)))
        
# maj du modele pour integrer les nouvelles variables
m3.update()
obj = LinExpr();
obj =0
for j in colonnes:
    obj += c[j] * x[j]
      
# definition de l'objectif
m3.setObjective(obj,GRB.MINIMIZE)

# Definition des contraintes
for i in range(0,n):
    m3.addConstr(quicksum(matrice_contraintes[i][j]*x[j] for j in colonnes) == b[i], "Contrainte%d" % i)

for i in range(n,2*n):
    m3.addConstr(quicksum(matrice_contraintes[i][j]*x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)

  
for i in range(2*n,2*n + 1):
    m3.addConstr(quicksum(matrice_contraintes[i][j]*x[j] for j in colonnes) == b[i], "Contrainte%d" % i)

for i in range(2*n + 1,2*n + 1+n**2):
    m3.addConstr(quicksum(matrice_contraintes[i][j]*x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)
    
for i in range(2*n + 1+n**2,3*n + 1+n**2):
    m3.addConstr(quicksum(matrice_contraintes[i][j]*x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)
    
# Resolution
m3.optimize()


print("")                
print('Solution optimale:')


#for i in range(36*k):
    #print('x%d'%(i+1), '=', x[i].x)

k=0
for i in range(n):
    for j in range(n):
        print('x%d_%d'%(i+1,j+1), '=', x[k].x)
        k=k+1
print('g', '=', x[k].x)
k=k+1
for j in range(n):
        print('j%d'%(j+1), '=', x[k].x)
        k=k+1
        
print("")
print('Valeur de la fonction objectif :', m3.objVal) 

m5 =m3.write("qopt.mps")

"""
###########################MATTHEWS' PARSING CODE###############################
def parseCoord():
    f = open("coordvilles92.txt", "r")
    my_text = f.readlines()
    return map(lambda coords: map(lambda coord : int(coord), re.findall(r'\d+', coords)), my_text)
    """
###########################PE PART###############################
Sat=0
Satv=[]
for j in range(n**2):
    Sat+= 1/epsilon*c[j] * x[j].x
    Satv.append(1/epsilon*c[j] * x[j].x)
SatM=Sat/n
MinSat=max(Satv)

activehubs=[]
for j in range(nbvar-n,nbvar):
    if x[j].x==1:
        activehubs.append(j-nbvar+n)
print(activehubs)        
        

#exec(open("projet1(1).py").read())
(Sat1,Satv1)=optdistr1(activehubs)
PE=1-Sat1/Sat
print("PE",'=',PE)
#Sat=1e6*(m1.objVal-x[nbvar-1].x)
#PEv.append(round(1-Sat1/Sat,6))
#gin.append(round(gini(Satv1),6))
#ginn.append(round(gini(Satv1),6))


stop = timeit.default_timer()

print('Time: ', stop - start) 
