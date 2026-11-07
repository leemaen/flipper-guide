import sys,json,glob,os; sys.path.insert(0,'tools')
from homography import apply
import numpy as np
from PIL import Image,ImageDraw,ImageFont
H=np.array(json.load(open('tools/rct/H_vpw.json')))
G='_quellen/rct/vpx/rct/gameitems/'
items={}
for f in glob.glob(G+'*.json'):
    t=os.path.basename(f).split('.')[0]
    if t not in ('Trigger','Kicker','HitTarget','Spinner','Gate','Bumper','Flipper'): continue
    d=json.load(open(f))[t]; c=d.get('center') or d.get('position')
    if c: items[d['name']]=(c['x'],c['y'])
json.dump(items,open('tools/rct/vpx_items.json','w'),indent=0)
im=Image.open('_quellen/rct/vpw24_screenshot.png').convert('RGB'); d=ImageDraw.Draw(im); f=ImageFont.truetype('arial.ttf',17)
for (n,p),q in zip(items.items(),apply(H,list(items.values()))):
    x,y=q; d.ellipse([x-6,y-6,x+6,y+6],outline=(0,255,0),width=3); d.text((x+8,y-9),n,fill=(0,255,0),font=f,stroke_width=2,stroke_fill=(0,0,0))
im.save('_quellen/rct/pages/overlay.png')
im.crop((0,0,1275,1300)).save('_quellen/rct/pages/ov_top.png')
im.crop((0,1100,1275,2559)).save('_quellen/rct/pages/ov_bot.png')
