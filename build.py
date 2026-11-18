"""Scan courses/<slug>/ folders (as produced by dl_coursera) and write
.generated/courses.json plus .generated/<slug>.json manifests."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
COURSES = os.path.join(HERE, 'courses')
GEN = os.path.join(HERE, '.generated')


def find(parent, i):
    pre = f'{i:02d}@'
    for n in sorted(os.listdir(parent)):
        if n.startswith(pre) and os.path.isdir(os.path.join(parent, n)):
            return n
    return None


def build_course(slug):
    cdir = os.path.join(COURSES, slug)
    crawl = os.path.join(cdir, '.cache', 'crawl.json')
    if not os.path.isfile(crawl):
        return None
    d = json.load(open(crawl, encoding='utf8'))
    out = {'slug': slug, 'title': d.get('name', slug), 'modules': []}
    lectures = quizzes = 0
    for mi, m in enumerate(d.get('modules', []), 1):
        mn = find(cdir, mi)
        if not mn:
            continue
        mod = {'name': m['name'], 'lessons': []}
        for li, l in enumerate(m.get('lessons', []), 1):
            ln = find(os.path.join(cdir, mn), li)
            if not ln:
                continue
            les = {'name': l['name'], 'items': []}
            for ii, it in enumerate(l.get('items', []), 1):
                idir = find(os.path.join(cdir, mn, ln), ii)
                if not idir:
                    continue
                files = os.listdir(os.path.join(cdir, mn, ln, idir))
                r = '/'.join((mn, ln, idir))
                e = {'name': it['name'], 'type': it['type'], 'id': it['id']}
                if it['type'] == 'Lecture':
                    mp4 = [f for f in files if f.endswith('.mp4')]
                    if not mp4:
                        continue
                    e['video'] = r + '/' + mp4[0]
                    srt = [f for f in files if f.endswith('.srt')]
                    if srt:
                        e['srt'] = r + '/' + srt[0]
                    lectures += 1
                else:
                    h = [f for f in files if f.endswith('.html')]
                    if not h:
                        continue
                    e['html'] = r + '/' + h[0]
                    quizzes += 1
                les['items'].append(e)
            if les['items']:
                mod['lessons'].append(les)
        if mod['lessons']:
            out['modules'].append(mod)
    ref = os.path.join(cdir, 'references')
    if os.path.isdir(ref):
        out['references'] = ['references/' + f for f in sorted(os.listdir(ref))]
    out['lectures'], out['quizzes'] = lectures, quizzes
    return out


def build():
    os.makedirs(GEN, exist_ok=True)
    index = []
    if os.path.isdir(COURSES):
        for slug in sorted(os.listdir(COURSES)):
            if not os.path.isdir(os.path.join(COURSES, slug)):
                continue
            c = build_course(slug)
            if not c:
                continue
            json.dump(c, open(os.path.join(GEN, slug + '.json'), 'w', encoding='utf8'))
            index.append({'slug': slug, 'title': c['title'], 'modules': len(c['modules']),
                          'lectures': c['lectures'], 'quizzes': c['quizzes']})
    json.dump(index, open(os.path.join(GEN, 'courses.json'), 'w', encoding='utf8'), indent=1)
    return index


if __name__ == '__main__':
    for c in build():
        print(f"{c['slug']}: {c['modules']} modules, {c['lectures']} lectures, {c['quizzes']} quizzes")
