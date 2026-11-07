import sys,json; sys.path.insert(0,'tools')
from homography import fit, apply
import numpy as np
pairs = {
 'l33':((180,702),(852.5,710)),'l34':((198,780),(860,744)),'l35':((216,858),(867.5,777.5)),'l36':((235,937),(876,812)),
 'l37':((273,573),(915,664)),'l38':((278,654),(915,696)),'l39':((283,737),(917.5,727.5)),'l40':((289,817),(919,759)),
 'l49':((645,1006),(1159.7,837.8)),'l50':((618,1079),(1147,880)),'l51':((591,1155),(1128.4,920.6)),'l52':((563,1230),(1112.8,964.4)),
 'l45':((795,906),(1253,803)),'l46':((766,986),(1245.6,834.7)),'l47':((739,1061),(1233,870.6)),'l48':((711,1139),(1220.6,911)),
}
src=[v[0] for v in pairs.values()]; dst=[v[1] for v in pairs.values()]
H=fit(src,dst); res=apply(H,src)-np.array(dst)
for k,r in zip(pairs,res): print(k, np.round(r,1))
print('rms',np.sqrt((res**2).sum(1).mean()))
json.dump(H.tolist(),open('tools/H_photo.json','w'))
test={'LeftFlipper':(275,1873),'RightFlipper':(591,1873),'Bumper1':(551,524),'Bumper2':(776,513),'Bumper3':(689,664),'sw29 Palantir':(512,847),'sw53 SpotRing':(767,1232),'corner TL':(0,0),'corner TR':(952,0),'corner BL':(0,2203),'corner BR':(952,2203)}
for k,p in zip(test,apply(H,list(test.values()))): print(k,np.round(p,0))
