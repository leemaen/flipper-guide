import json,glob,os
from PIL import Image,ImageDraw,ImageFont
G='_quellen/vpx/lotr-reference/gameitems/'
S=1.0
im=Image.new('RGB',(952,2203),(20,20,20)); d=ImageDraw.Draw(im); f=ImageFont.truetype('arial.ttf',13)
for fn in glob.glob(G+'*.json'):
  t=os.path.basename(fn).split('.')[0]
  if t not in ('Wall','Ramp','Rubber'): continue
  dd=json.load(open(fn))[t]; pts=dd.get('drag_points') or []
  if len(pts)<2: continue
  xy=[(p['x'],p['y']) for p in pts]
  if t=='Wall':
    top=dd.get('height_top',50); col=(90,90,90) if top>0 else (50,50,50)
    if dd.get('is_collidable',True) is False: continue
    d.line(xy+[xy[0]],fill=col,width=2)
  elif t=='Ramp':
    d.line(xy,fill=(200,120,40),width=3); d.text(xy[0],dd['name'],fill=(200,120,40),font=f)
  else:
    d.line(xy+[xy[0]],fill=(60,60,160),width=2)
it=json.load(open('tools/vpx_items.json'))
for n,(x,y) in it.items():
  d.ellipse([x-6,y-6,x+6,y+6],outline=(0,255,0),width=2); d.text((x+8,y-6),n,fill=(0,255,0),font=f)
for y in range(0,2203,100):
  d.line([(0,y),(8,y)],fill=(255,255,0)); d.text((10,y-6),str(y),fill=(255,255,0),font=f)
for x in range(0,952,100):
  d.line([(x,0),(x,8)],fill=(255,255,0)); d.text((x+2,10),str(x),fill=(255,255,0),font=f)
im.save('_quellen/pages/vpx_map.png')
im.crop((0,0,952,1100)).save('_quellen/pages/vpx_map_top.png')
