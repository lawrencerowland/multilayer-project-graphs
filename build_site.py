"""Assemble only the public reading copy of Foray 342 (no repository dump)."""
from pathlib import Path
import html
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '_site'
ORIGIN = 'https://experimentsin.ai/multilayer-project-graphs/'
TITLE = 'What do project layers reveal?'
CSS = '''
:root{--ink:#173637;--muted:#526665;--paper:#f8f5ec;--line:#d7ded4;--teal:#286a60;--sand:#b17d38}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:18px/1.65 system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:32px 24px 65px}a{color:var(--teal);text-underline-offset:4px}a:focus-visible,summary:focus-visible{outline:3px solid #b55b43;outline-offset:4px}nav,footer{display:flex;gap:20px;flex-wrap:wrap;font-size:14px}header{padding:48px 0 25px}.eyebrow{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--teal);font-weight:750}h1{font-size:clamp(37px,6vw,64px);line-height:1.06;letter-spacing:-.04em;max-width:800px;margin:16px 0 25px;font-weight:650}h2{font-size:26px;line-height:1.2;margin-top:40px}h3{font-size:20px}.lead{font-size:21px;max-width:740px}.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin:25px 0 50px}.tile{display:block;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#fffdf7;text-decoration:none;transition:transform .2s}.tile:hover{transform:translateY(-3px)}.tile svg{width:100%;height:auto;display:block}.tile span{display:block;padding:20px 22px;font-size:20px;font-weight:650}.tile small{display:block;font-size:14px;font-weight:400;margin-top:6px;color:var(--muted)}article{max-width:780px}p,li{max-width:80ch}code{font-size:.88em;background:#eaece4;padding:.1em .3em;border-radius:3px}pre{overflow:auto;background:#eaece4;padding:20px;border-radius:10px;font-size:14px}pre code{padding:0}.note{border-left:3px solid #b17d38;padding:5px 20px;margin:30px 0;color:var(--muted)}.status{display:inline-block;padding:6px 12px;border:1px solid var(--line);border-radius:30px;font-size:13px}.skip{position:absolute;left:-9999px}.skip:focus{left:15px;top:10px}footer{border-top:1px solid var(--line);padding-top:22px;margin-top:40px}figure{margin:26px 0}figure img{max-width:100%;height:auto}figcaption{font-size:14px;color:var(--muted)}table{border-collapse:collapse;width:100%;font-size:15px}td,th{text-align:left;border-bottom:1px solid var(--line);padding:10px}@media(max-width:650px){.tiles{grid-template-columns:1fr}header{padding-top:25px}main{padding:25px 18px}h1{font-size:42px}}
'''

def inline(text):
    text = html.escape(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\[([^]]+)\]\((https?://[^\s)]+|[A-Za-z0-9_./% -]+)\)', r'<a href="\2">\1</a>', text)
    return text

def markdown(text):
    blocks, paragraph, items, fenced = [], [], [], None
    list_tag = "ul"
    def flush():
        if paragraph:
            blocks.append('<p>'+inline(' '.join(paragraph))+'</p>'); paragraph.clear()
        if items:
            blocks.append('<'+list_tag+'>'+''.join('<li>'+inline(x)+'</li>' for x in items)+'</'+list_tag+'>'); items.clear()
    for line in text.splitlines():
        if line.startswith('```'):
            if fenced is None: flush(); fenced=[]
            else: blocks.append('<pre><code>'+html.escape('\n'.join(fenced))+'</code></pre>'); fenced=None
            continue
        if fenced is not None: fenced.append(line); continue
        if not line.strip(): flush(); continue
        heading=re.match(r'^(#{1,4}) (.+)$',line)
        if heading:
            flush(); level=min(4,len(heading[1])+1); blocks.append(f'<h{level}>'+inline(heading[2])+f'</h{level}>')
        elif re.match(r'^([-*]|[0-9]+\.) ',line):
            new_tag = 'ol' if re.match(r'^[0-9]+\.',line) else 'ul'
            if paragraph or (items and new_tag != list_tag): flush()
            list_tag = new_tag
            items.append(re.sub(r'^([-*]|[0-9]+\.) ', '', line))
        else:
            if items: flush()
            paragraph.append(line)
    flush()
    return '\n'.join(blocks)

def shell(title, route, body, nested=False):
    prefix='../' if nested else ''
    layer_assets = '<link rel="stylesheet" href="https://experimentsin.ai/assets/site-layer.css"><script defer data-experiment-layer src="https://experimentsin.ai/assets/site-layer.js"></script>' if not route else ''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · Foray 342</title><meta name="description" content="A project in connected layers: a public enquiry into stakeholders, objectives and scope, with a reproducible Py3Plex essai."><link rel="canonical" href="{ORIGIN+route}"><style>{CSS}</style>{layer_assets}</head><body><a class="skip" href="#main">Skip to content</a><main id="main"><nav aria-label="Breadcrumb"><a href="https://experimentsin.ai/experiments/graphs-and-representations/">Graphs and representations</a><a href="https://experimentsin.ai/side-projects.html">All experiments</a><a href="{prefix}index.html">Foray 342</a></nav>{body}<footer><a href="{prefix}index.html">Foray entrance</a><a href="{prefix}prompt.html">Full foray prompt</a><a href="https://github.com/lawrencerowland/multilayer-project-graphs">Source and reproduction</a><span>21 November 2026 · an open enquiry</span></footer></main></body></html>'''

def art(kind):
    if kind == 'rail':
        shapes='<path d="M0 236Q160 160 340 220T640 210V400H0Z" fill="#cbd9c5"/><path d="M-10 340L650 160M-10 368L650 188" stroke="#66756e" stroke-width="8"/><path d="M140 283l20 42m60-68 20 42m60-68 20 42m60-68 20 42m60-68 20 42" stroke="#66756e" stroke-width="6"/><rect x="290" y="120" width="180" height="85" rx="20" fill="#286a60"/><path d="M320 135h100v30H320z" fill="#f5ecd5"/><circle cx="330" cy="208" r="14" fill="#173637"/><circle cx="435" cy="208" r="14" fill="#173637"/><path d="M110 190v-80l65-40 65 40v80z" fill="#dca983"/><path d="M100 110l75-50 75 50" fill="none" stroke="#a96b4d" stroke-width="8"/>'
    elif kind == 'purpose':
        shapes='<g fill="none" stroke="#a5b9aa" stroke-width="5"><path d="M150 115L320 190L490 100M150 115L155 290L320 190L490 295M155 290L490 295"/></g><g fill="#286a60"><circle cx="150" cy="115" r="32"/><circle cx="155" cy="290" r="32"/></g><g fill="#b17d38"><circle cx="320" cy="190" r="45"/></g><g fill="#b46c53"><circle cx="490" cy="100" r="32"/><circle cx="490" cy="295" r="32"/></g><path d="M300 190l15 15 30-35" fill="none" stroke="#fffaf0" stroke-width="7"/>'
    else:
        shapes='<g fill="#e3e9de" stroke="#b5c9be" stroke-width="2"><path d="M65 95h150v230H65z"/><path d="M245 65h150v230H245z"/><path d="M425 95h150v230H425z"/></g><g stroke="#7c9b8e" stroke-width="4"><path d="M140 140l180 10 180-10M140 240l180-90 180 100M140 140l180 110 180-110"/></g><g fill="#b17d38"><circle cx="140" cy="140" r="18"/><circle cx="140" cy="240" r="18"/></g><g fill="#b46c53"><circle cx="320" cy="150" r="18"/><circle cx="320" cy="250" r="18"/></g><g fill="#286a60"><circle cx="500" cy="140" r="18"/><circle cx="500" cy="250" r="18"/></g>'
    return '<svg viewBox="0 0 640 400" role="img" aria-label="'+{'rail':'A small railway project','purpose':'Distinct things connected around a question','layers':'Three distinct connected layers'}[kind]+'"><rect width="640" height="400" fill="#edf0e5"/>'+shapes+'</svg>'

def build():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(); (OUT/'essai-01').mkdir(); (OUT/'web').mkdir(); (OUT/'assets').mkdir()
    (OUT/'assets/emblem.svg').write_text(art('layers'))
    tiles=''.join(f'<a class="tile" href="{url}">{art(kind)}<span>{label}<small>{desc}</small></span></a>' for url,kind,label,desc in [
        ('scenario.html','rail','Scenario','A rail scheme, still deliberately small.'),('purpose.html','purpose','Purpose','Keep useful distinctions without losing connections.'),('essai-01/','layers','1. A project in connected layers','Revisit the 2022 example with current Py3Plex.')])
    body=f'<header id="foray"><p class="eyebrow">Foray 342 · Graphs and representations</p><h1>{TITLE}</h1><p class="lead">Who cares about an objective, which parts of the work touch it, and what changes when we redraw or simplify the network?</p></header><section class="tiles" aria-label="Choose a foray entrance">{tiles}</section><p class="note">A running enquiry, beginning with Lawrence’s small 2022 railway model. The first essai tests the representation. It does not establish a railway design, stakeholder agreement or carbon benefit.</p>'
    (OUT/'index.html').write_text(shell(TITLE,'',body))
    scenario='''<header><p class="eyebrow">Foray 342 · Scenario</p><h1>A small railway.<br>Several kinds of concern.</h1><p class="lead">A station, faster trains and a carbon ambition sit alongside track, trains, signalling and the organisations that care about them.</p></header><article>'''+art('rail')+'''<p>Lawrence sketched this deliberately simple rail scheme in October 2022. The three layers are objectives, stakeholders and scope. The hand-entered connections are prompts for enquiry, not certified requirements or measured effects.</p><h2>Keep the first attempt recognisable</h2><p>The first essai brings across the original names, edge records and commentary. A separate curated model corrects the manufacturer spelling and identifies repeated records. Ambiguous weights remain visible. New station and construction method stay in the original objectives layer, even though they might later be better described as options or means.</p><h2>Make it harder when there is a reason</h2><p>A later rail scenario could add competing objectives, alternative interventions, phases, resource limits, disputed evidence or stakeholders who disagree. Introduce a complication when it can expose a limitation or improve a decision—not simply to make a larger picture.</p><p><a href="essai-01/">Open Essai 01 →</a></p></article>'''
    (OUT/'scenario.html').write_text(shell('The small railway','scenario.html',scenario))
    purpose='''<header><p class="eyebrow">Foray 342 · Purpose</p><h1>Distinct things.<br>Inspectable connections.</h1></header><article><h2>End</h2><p>Find when explicit project layers help someone understand a situation, ask a better question or choose what to examine next. The test is what becomes visible and reliable, not how many nodes fit on the screen.</p><h2>Ways</h2><p>Make the node and relationship grammar explicit. Compare layer-aware views with a flattened view of the same information. Trace short paths, inspect exclusions and compare interpretations. Test both the model’s invariants and the claims made from it.</p><h2>Means</h2><p>Begin with the 2022 stakeholder–objective–scope example, a fresh run of current Py3Plex, the original commentary, a transparent correction ledger and an interactive reader. Keep methods and later scenarios open to revision.</p><h2>The first result is a beginning</h2><p>Essai 01 proves a bounded reconstruction and makes the choices behind a layered representation inspectable. It has not measured a real project benefit, resolved the meaning of the original weights or supplied missing project evidence.</p><p><a href="prompt.html">Read the full foray prompt →</a> · <a href="essai-01/">Try the first essai →</a></p></article>'''
    (OUT/'purpose.html').write_text(shell('End, ways and means','purpose.html',purpose))
    prompt=(ROOT/'FORAY_PROMPT.md').read_text()
    (OUT/'prompt.html').write_text(shell('Foray prompt','prompt.html','<header><p class="eyebrow">PW-342 · Working prompt</p><h1>'+TITLE+'</h1></header><article>'+markdown(prompt)+'</article>'))
    (OUT/'foray-prompt.txt').write_text(prompt)
    for folder, allowed in [('data',{'.json','.csv'}),('outputs',{'.json','.svg','.png','.csv'}),('sources',{'.json','.md','.txt','.ipynb'})]:
        for src in (ROOT/folder).rglob('*'):
            if src.is_file() and src.suffix in allowed:
                dest=OUT/src.relative_to(ROOT); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dest)
    for src in (ROOT/'web').iterdir():
        if src.suffix in {'.css','.js','.svg'}: shutil.copyfile(src,OUT/'web'/src.name)
    network=json.loads((ROOT/'outputs/network.json').read_text())
    run_path=next((p for p in [ROOT/'outputs/runtime-receipt.json',ROOT/'outputs/run.json',ROOT/'outputs/metrics.json'] if p.exists()),None)
    run=json.loads(run_path.read_text()) if run_path else network.get('metrics',{})
    template=(ROOT/'web/essai-template.html').read_text()
    template=template.replace('__GRAPH_DATA__',json.dumps(network,ensure_ascii=False).replace('</','<\\/')).replace('__RUN_DATA__',json.dumps(run,ensure_ascii=False).replace('</','<\\/'))
    (OUT/'essai-01/index.html').write_text(template)
    comment_files=[p for p in (ROOT/'sources').rglob('*.md') if 'comment' in p.name.lower()]
    commentary='\n\n'.join(p.read_text() for p in comment_files)
    checkpoint=ROOT/'sources/checkpoint-note.md'
    if checkpoint.exists(): commentary+='\n\n'+checkpoint.read_text()
    if not commentary: raise RuntimeError('Original commentary reader is required before publication')
    body='<header><p class="eyebrow">Essai 01 · Source commentary</p><h1>The original voice and data</h1><p><a href="./">Back to the interactive essai</a></p></header><article>'+markdown(commentary)+'</article>'
    (OUT/'essai-01/commentary.html').write_text(shell('Original commentary','essai-01/commentary.html',body,True))
    results=ROOT/'METHOD-AND-RESULTS.md'
    if not results.is_file(): raise RuntimeError('Computed findings and method are required before publication')
    if results.exists():
        result_html=re.sub(r'href="(outputs|sources|data)/', r'href="../\1/', markdown(results.read_text()))
        result_body='<header><p class="eyebrow">Essai 01 · Findings and method</p><h1>What this run establishes</h1><p><a href="./">Back to the interactive essai</a></p></header><article>'+result_html+'</article>'
        result_body+='<figure><img src="../outputs/railway-three-layers.svg" alt="Computed layout of the railway graph across three explicit layers"><figcaption>The fresh Python run: three layers with recorded directions. The interactive explorer provides source rows and an accessible connection index.</figcaption></figure>'
        (OUT/'essai-01/findings.html').write_text(shell('Findings and method','essai-01/findings.html',result_body,True))
    (OUT/'.nojekyll').write_text('')
    urls=['','scenario.html','purpose.html','prompt.html','essai-01/','essai-01/commentary.html','essai-01/findings.html']
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+ORIGIN+x+'</loc></url>' for x in urls)+'</urlset>')
    print(json.dumps({'public_files':len([p for p in OUT.rglob('*') if p.is_file()]),'output':'_site','foray':342}))

if __name__=='__main__': build()
