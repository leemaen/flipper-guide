import sys,json,glob,os; sys.path.insert(0,'tools')
from homography import apply
import numpy as np
from PIL import Image,ImageDraw,ImageFont
H=np.array(json.load(open('tools/rct/H_vpw.json')))
G='_quellen/rct/vpx/rct/gameitems/'
im=Image.open('_quellen/rct/vpw24_screenshot.png').convert('RGB')
im=Image.blend(im,Image.new('RGB',im.size,(0,0,0)),0.55); d=ImageDraw.Draw(im); f=ImageFont.truetype('arial.ttf',15)
for fn in glob.glob(G+'Wall.*.json'):
    w=json.load(open(fn))['Wall']
    if not w.get('is_collidable',True): continue
    pts=[(p['x'],p['y']) for p in w['drag_points']]
    if len(pts)<2: continue
    q=[tuple(p) for p in apply(H,pts)]
    top=w.get('height_top',50); bot=w.get('height_bottom',0)
    col=(255,80,80) if bot>5 else ((80,200,255) if top>30 else (120,120,120))
    d.line(q+[q[0]],fill=col,width=2)
    if bot>5: d.text(q[0],f"{w['name']} {bot:.0f}-{top:.0f}",fill=col,font=f)
it=json.load(open('tools/rct/vpx_items.json'))
for (n,p),q in zip(it.items(),apply(H,list(it.values()))):
    x,y=q; d.ellipse([x-5,y-5,x+5,y+5],outline=(0,255,0),width=2); d.text((x+7,y-8),n,fill=(0,255,0),font=f)
im.save('_quellen/rct/pages/walls.png')
im.crop((0,0,1275,1350)).save('_quellen/rct/pages/walls_top.png')
im.crop((0,1150,1275,2559)).save('_quellen/rct/pages/walls_bot.png')
