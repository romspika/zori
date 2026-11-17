# Служебный: контур content/old/*.md (секции, якоря, слова, картинки) -> work/outline.txt
import re, glob, os, sys
out=[]
for f in sorted(glob.glob('content/old/*.md')):
    slug=os.path.basename(f)[:-3]
    t=open(f,encoding='utf-8').read()
    parts=re.split(r'\n(?=## )',t)
    out.append(f'=== {slug}  ({len(parts)-1} секций)')
    for p in parts[1:]:
        head=p.split('\n',1)[0]
        body=p.split('\n',1)[1] if '\n' in p else ''
        imgs=len(re.findall(r'^- new:',body,re.M))
        txt=re.sub(r'\*\*Картинки секции:\*\*.*','',body,flags=re.S)
        words=len(re.findall(r'\w+',txt))
        out.append(f'  {head[:90]} | w={words} img={imgs}')
open('work/outline.txt','w',encoding='utf-8').write('\n'.join(out))
print(len(out))
