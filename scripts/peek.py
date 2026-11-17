# Служебный: показать секции md без списков картинок, каждая обрезана до N символов
import sys,re
sys.stdout.reconfigure(encoding='utf-8')
f,n=sys.argv[1],int(sys.argv[2]) if len(sys.argv)>2 else 350
t=open(f'content/old/{f}.md',encoding='utf-8').read()
for p in re.split(r'\n(?=## )',t)[1:]:
    head,_,body=p.partition('\n')
    srcs=re.findall(r'^- new: (\S+)',body,re.M)
    body=re.sub(r'\*\*Картинки секции:\*\*.*','',body,flags=re.S).strip()
    print(head,'| img:',len(srcs),srcs[:2]); print('   ',re.sub(r'\s+',' ',body)[:n]); print()
