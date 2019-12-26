import numpy as np
import os

path = './HW3/hw3dataset'
entries = os.scandir(path)
files = []


def graphMatrix(graph):
    with open(graph,'r') as fp:
        nodes = set()# 建立空的集合
        lines = fp.readlines()
        for line in lines:
            #第二個參數為1，返回兩個參數
            node = line.split(',',1)
            nodes.add(int(node[0]))
            nodes.add(int(node[1]))

        num = max(nodes)
        mtx = np.zeros((num, num))

        for line in lines:
            node = line.split(',',1)
            mtx[int(node[0])-1,int(node[1])-1] += 1

        mtx[0,2] += 1
        mtx[1,0] += 1
        return mtx

def graphMatrixIBM(graph,biconnect):
    with open(graph,'r') as fp:
        nodes = set()# 建立空的集合
        lines = fp.readlines()
    
        for line in lines:
            a, b, c = line.split()
            nodes.add(int(b))
            nodes.add(int(c)+1)

        num = max(nodes)
        mtx = np.zeros((num, num))

        for line in lines:
            a, b, c = line.split()
            mtx[int(b)-1,int(c)] += 1
            if biconnect:
                mtx[int(c),int(b)-1] += 1

        return mtx

    





def Hits(mtx):
    hub = np.ones((len(mtx),1))
    auth = np.ones((len(mtx),1))

    for i in range(100):
        authNew = np.dot(mtx.T,hub)
        hubNew = np.dot(mtx,auth)
        count = np.sum(authNew, axis = 0)
        auth = authNew/count
        count = np.sum(hubNew, axis = 0)
        hub = hubNew/count

    return hub,auth

def PageRank(mtx,damping):
    count = np.sum(mtx, axis = 1, keepdims = True)
    mtx = mtx / count
    mtx[np.isnan(mtx)] = 0
    damping = np.full((len(mtx),1), damping)
    PR=PR0 = np.ones((len(mtx),1))/len(mtx)
    
    for i in range(100):
        PR = np.dot(mtx.T,PR)*damping +(1 - damping)*PR0
    
    return PR


def SimRank(mtx,c=0.9):
    s=I = np.identity(len(mtx))
    count = np.sum(mtx, axis = 0, keepdims = True)
    mtx = mtx / count
    where_are_NaNs = np.isnan(mtx)
    mtx[where_are_NaNs] = 0
    for i in range(100):

        # A = c * (mtx.T).dot(s).dot(mtx)
        # x = np.identity(len(mtx))
        # np.fill_diagonal(x,A.diagonal().tolist())
        # s = A + I - x
        #np.dot(np.dot(mtx.T,s),mtx)
        s = c * (mtx.T).dot(s).dot(mtx)
        np.fill_diagonal(s,1)
    
    print(s)



for entry in entries:
    filename = entry.name
    if filename.startswith('g'):
        files.append(filename)

files.sort()
#IBM dataset
files.append('data.ntrans_0.1.nitems_0.01.txt')
files.append('data.ntrans_0.1.nitems_0.01.txt')
print(files)


for filename in files:
    
    graph = path+'/'+filename
    biconnect = False
    #IBM dataset
    if filename.startswith('d'):
        graph = './HW1/'+filename
        mtx = graphMatrixIBM(graph,biconnect)
        biconnect = True
    else:
        mtx = graphMatrix(graph)

    hub,auth = Hits(mtx)
    print(hub.tolist())
    print(auth.tolist())
    print(PageRank(mtx,0.85).tolist())

files = files[:5]
print(files)
for filename in files:
    graph = path+'/'+filename
    mtx = graphMatrix(graph)
    SimRank(mtx,0.8)