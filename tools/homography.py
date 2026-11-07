import numpy as np, json, sys
def fit(src, dst):
    A=[]
    for (x,y),(u,v) in zip(src,dst):
        A.append([-x,-y,-1,0,0,0,u*x,u*y,u]); A.append([0,0,0,-x,-y,-1,v*x,v*y,v])
    _,_,Vt=np.linalg.svd(np.array(A)); H=Vt[-1].reshape(3,3); return H/H[2,2]
def apply(H,pts):
    p=np.c_[np.array(pts,float),np.ones(len(pts))]@H.T; return p[:,:2]/p[:,2:3]
