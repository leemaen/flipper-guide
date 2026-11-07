import sys,json,glob,os; sys.path.insert(0,'tools')
from homography import fit,apply
import numpy as np
pairs = {
 'l33':((180,702),(852.5,710)),'l34':((198,780),(860,744)),'l35':((216,858),(867.5,777.5)),'l36':((235,937),(876,812)),
 'l37':((273,573),(915,664)),'l38':((278,654),(915,696)),'l39':((283,737),(917.5,727.5)),'l40':((289,817),(919,759)),
 'l49':((645,1006),(1159.7,837.8)),'l50':((618,1079),(1147,880)),'l51':((591,1155),(1128.4,920.6)),'l52':((563,1230),(1112.8,964.4)),
 'l45':((795,906),(1253,803)),'l46':((766,986),(1245.6,834.7)),'l47':((739,1061),(1233,870.6)),'l48':((711,1139),(1220.6,911)),
 'LF':((275,1873),(843,1460)),'RF':((591,1873),(1183,1463)),'K':((52,1562),(670,1190)),'P':((813,1568),(1360,1197)),
}
src=[v[0] for v in pairs.values()]; dst=[v[1] for v in pairs.values()]
H=fit(src,dst); json.dump(H.tolist(),open('tools/H_photo.json','w'))
G='_quellen/vpx/lotr-reference/gameitems/'
items={}
for f in glob.glob(G+'*.json'):
  t=os.path.basename(f).split('.')[0]
  if t not in ('Trigger','Kicker','HitTarget','Spinner','Gate','Bumper','Flipper'): continue
  d=json.load(open(f))[t]; c=d.get('center') or d.get('position')
  if c: items[d['name']]=(c['x'],c['y'])
json.dump(items,open('tools/vpx_items.json','w'),indent=0)
from PIL import Image,ImageDraw,ImageFont
im=Image.open('_quellen/fotos/gorilla-top-down.jpg').convert('RGB'); d=ImageDraw.Draw(im)
f=ImageFont.truetype('arial.ttf',15)
for (n,p),q in zip(items.items(),apply(H,list(items.values()))):
  x,y=q; d.ellipse([x-5,y-5,x+5,y+5],outline=(0,255,0),width=2); d.text((x+7,y-7),n,fill=(0,255,0),font=f)
im.save('_quellen/pages/overlay_switches.png')
