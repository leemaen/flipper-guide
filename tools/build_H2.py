import sys,json; sys.path.insert(0,'tools')
from homography import fit,apply
import numpy as np
pairs={
 'l33':((180,702),(223,798)),'l34':((198,780),(242,871)),'l35':((216,858),(261.5,940)),'l36':((235,937),(274.6,1009)),
 'l37':((273,573),(315,678)),'l38':((278,654),(321,763)),'l39':((283,737),(323,835)),'l40':((289,817),(327,905)),
 'l50':((618,1079),(634.6,1136)),'l51':((591,1155),(611.5,1201.5)),'l52':((563,1230),(580.8,1271)),
 'l46':((766,986),(765,1051.5)),'l47':((739,1061),(746,1121)),'l48':((711,1139),(723,1186)),
 'LF':((275,1873),(300,1853)),'RF':((591,1873),(627,1853)),'l8':((433,1890),(460,1895)),'l6':((435,1724),(457,1730)),
}
src=[v[0] for v in pairs.values()]; dst=[v[1] for v in pairs.values()]
H=fit(src,dst); res=apply(H,src)-np.array(dst)
for k,r in zip(pairs,res): print(k,np.round(r,1))
print('rms',np.sqrt((res**2).sum(1).mean()))
json.dump(H.tolist(),open('tools/H_vpw.json','w'))
from PIL import Image,ImageDraw,ImageFont
it=json.load(open('tools/vpx_items.json'))
im=Image.open('_quellen/vpx/vpw16_screenshot.png').convert('RGB'); d=ImageDraw.Draw(im); f=ImageFont.truetype('arial.ttf',14)
for (n,p),q in zip(it.items(),apply(H,list(it.values()))):
  x,y=q; d.ellipse([x-5,y-5,x+5,y+5],outline=(0,255,0),width=2); d.text((x+7,y-7),n,fill=(0,255,0),font=f)
im.save('_quellen/pages/overlay_vpw.png')
