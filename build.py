import json, os, sys, re
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
slug = 'packt-data-governance-ai-governance-the-complete-guide-i0wqi'
cdir = os.path.join(root, slug)
d = json.load(open(os.path.join(cdir, '.cache', 'crawl.json'), encoding='utf8'))

def find(parent, i):
    pre = f'{i:02d}@'
    for n in sorted(os.listdir(parent)):
        if n.startswith(pre) and os.path.isdir(os.path.join(parent, n)):
            return n
    return None

def rel(*p): return '/'.join(p)

out = {'title': d['name'], 'modules': []}
miss = 0
vid = 0
for mi, m in enumerate(d['modules'], 1):
    mn = find(cdir, mi)
    mod = {'name': m['name'], 'lessons': []}
    for li, l in enumerate(m['lessons'], 1):
        ln = find(os.path.join(cdir, mn), li)
        les = {'name': l['name'], 'items': []}
        for ii, it in enumerate(l['items'], 1):
            idir = find(os.path.join(cdir, mn, ln), ii)
            base = os.path.join(cdir, mn, ln, idir)
            r = rel(mn, ln, idir)
            files = os.listdir(base)
            e = {'name': it['name'], 'type': it['type'], 'id': it['id']}
            if it['type'] == 'Lecture':
                mp4 = [f for f in files if f.endswith('.mp4')]
                srt = [f for f in files if f.endswith('.srt')]
                if not mp4: miss += 1; continue
                e['video'] = rel(r, mp4[0]); vid += 1
                if srt: e['srt'] = rel(r, srt[0])
                e['other'] = [rel(r, f) for f in files if not f.endswith(('.mp4', '.srt'))]
            else:
                h = [f for f in files if f.endswith('.html')]
                if not h: miss += 1; continue
                e['html'] = rel(r, h[0])
            les['items'].append(e)
        mod['lessons'].append(les)
    out['modules'].append(mod)
if os.path.exists(os.path.join(cdir, 'references')):
    out['references'] = ['references/' + f for f in os.listdir(os.path.join(cdir, 'references'))]
json.dump(out, open(os.path.join(root, 'site', 'manifest.json'), 'w', encoding='utf8'), indent=1)
print('videos', vid, 'missing', miss)
