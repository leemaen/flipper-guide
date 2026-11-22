"""Normalisierte DLT-Homographie (numerisch stabil)."""
import numpy as np
def _norm(p):
    p=np.asarray(p,float); c=p.mean(0); s=np.sqrt(2)/np.sqrt(((p-c)**2).sum(1)).mean()
    T=np.array([[s,0,-s*c[0]],[0,s,-s*c[1]],[0,0,1]]); return T
def fitn(src,dst):
    Ts,Td=_norm(src),_norm(dst)
    s=np.c_[np.asarray(src,float),np.ones(len(src))]@Ts.T; d=np.c_[np.asarray(dst,float),np.ones(len(dst))]@Td.T
    A=[]
    for (x,y,_),(u,v,_) in zip(s,d):
        A.append([-x,-y,-1,0,0,0,u*x,u*y,u]); A.append([0,0,0,-x,-y,-1,v*x,v*y,v])
    _,_,Vt=np.linalg.svd(np.array(A)); Hn=Vt[-1].reshape(3,3)
    H=np.linalg.inv(Td)@Hn@Ts; return H/H[2,2]
