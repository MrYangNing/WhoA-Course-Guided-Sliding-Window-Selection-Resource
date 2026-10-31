"""Transcript-guided sliding-window retrieval on public SPIRAL annotations.
No ASR/audio model is executed. Scoring never uses answers or key labels.
Run fetch_data.py once, then python experiment.py.
"""
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'results'/'.matplotlib'))
import csv, json, math, re, hashlib, time, platform, statistics
from collections import Counter
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

STOP=set('a an the and or but if of to in on at for from with by as is are was were be been being do does did has have had it its this that these those i you he she they we me my your their our what which who whom whose when where why how can could would should will shall may might about into than then there here'.split())

def words(text):
    return [w for w in re.findall(r"[a-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?",text.lower()) if w not in STOP]

def score_sentences(sentences,question):
    """Within-record TF-IDF cosine, without access to target annotations."""
    docs=[Counter(words(s)) for s in sentences]
    df=Counter(t for doc in docs for t in doc)
    n=len(docs)
    idf={t:1+math.log((n+1)/(f+1)) for t,f in df.items()}
    def vector(counts):
        raw={t:(1+math.log(c))*idf[t] for t,c in counts.items() if t in idf}
        norm=math.sqrt(sum(x*x for x in raw.values()))
        return {t:x/norm for t,x in raw.items()} if norm else {}
    q=vector(Counter(words(question)))
    return [sum(x*q.get(t,0.) for t,x in vector(doc).items()) for doc in docs]

def sliding_window(scores,k):
    """Earliest maximum-sum contiguous window; O(N) time, O(1) workspace."""
    n=len(scores)
    if not 1<=k<=n: raise ValueError('k must be in [1, N]')
    current=sum(scores[i] for i in range(k)); best=current; start=0
    for right in range(k,n):
        current+=scores[right]-scores[right-k]
        if current>best:
            best=current; start=right-k+1
    return start,best

def naive_window(scores,k):
    best=-math.inf; start=0
    for t in range(len(scores)-k+1):
        total=sum(scores[t:t+k])
        if total>best: best=total; start=t
    return start,best

def test_algorithm():
    rng=np.random.default_rng(20261031)
    for _ in range(2000):
        n=int(rng.integers(1,61)); k=int(rng.integers(1,n+1))
        x=rng.integers(-10,11,size=n).tolist()
        assert sliding_window(x,k)==naive_window(x,k)
    assert sliding_window([1,2,8,9,7,1],3)==(2,24)
    assert sliding_window([0,0,0],2)==(0,0)
    for x,k in [([],1),([1],0),([1],2)]:
        try: sliding_window(x,k)
        except ValueError: pass
        else: raise AssertionError('invalid input accepted')
    return {'integer_exhaustive_scan_comparisons':2000,'worked_example':True,'edge_cases_passed':True}

def metric(selected,gold,scores):
    selected=set(selected)
    overlap=len(selected & gold)
    return {'full_hit':float(gold<=selected),'any_hit':float(overlap>0),
            'gold_recall':overlap/len(gold),'score_sum':sum(scores[i] for i in selected),
            'runs':sum(i-1 not in selected for i in selected)}

def save_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def benchmark():
    rng=np.random.default_rng(12); rows=[]
    for n in [1000,3000,10000]:
        k=n//10; scores=rng.random(n).tolist()
        values={}
        for name,fn in [('naive',naive_window),('sliding',sliding_window)]:
            fn(scores,k)
            samples=[]
            for _ in range(7):
                t=time.perf_counter_ns(); result=fn(scores,k);samples.append((time.perf_counter_ns()-t)/1e6)
            values[name]=result
            rows.append({'N':n,'k':k,'method':name,'median_ms':statistics.median(samples),'repetitions':7})
        assert values['naive'][0]==values['sliding'][0]
        assert math.isclose(values['naive'][1],values['sliding'][1],abs_tol=1e-8)
    return rows

def main():
    for f in ['results','figures']:(ROOT/f).mkdir(exist_ok=True)
    checks=test_algorithm()
    source=ROOT/'data/spiral_data.jsonl'
    data=[json.loads(x) for x in source.read_text(encoding='utf-8').splitlines() if x.strip()]
    rows=[]; audits=[]; examples=[];n_sizes=[];g_sizes=[]
    for sample in data:
        sid=sample['metadata']['id']; genre=sample['metadata']['transcript_type']
        sentences=sample['audio_data']['combined']['sentences']
        a,b=sample['audio_data']['key_sentences']['indices']; n=len(sentences)
        if not (0<=a<b<=n):raise ValueError(('invalid annotation',sid,a,b,n))
        gold=set(range(a,b)); scores=score_sentences(sentences,sample['test_question']['question'])
        # Targets first enter the computation here, after feature scoring.
        norm=lambda s:re.sub('[^a-z0-9]','',s.lower())
        label_text=norm(sample['original_key_sentence']); slice_text=norm(' '.join(sentences[a:b]))
        relation='exact' if label_text==slice_text else ('contained' if label_text in slice_text else 'other')
        audits.append({'id':sid,'genre':genre,'N':n,'gold_start':a,'gold_end':b,'text_relation':relation})
        n_sizes.append(n);g_sizes.append(b-a)
        for fraction in [.1,.2,.3,.5]:
            k=max(1,math.ceil(n*fraction));start,window_score=sliding_window(scores,k)
            # Independent scan verification on every real sample and budget.
            brute,brute_score=naive_window(scores,k)
            assert math.isclose(window_score,brute_score,abs_tol=1e-10)
            top=sorted(range(n),key=lambda i:(-scores[i],i))[:k]
            selections={'first':list(range(k)),'topk':top,'sliding':list(range(start,start+k))}
            for method,selection in selections.items():
                rr=dict(id=sid,genre=genre,N=n,fraction=fraction,k=k,method=method,
                        retained_fraction=k/n,word_fraction=sum(len(words(sentences[i])) for i in selection)/sum(len(words(s)) for s in sentences))
                rr.update(metric(selection,gold,scores));rr['selected_indices']=json.dumps(sorted(selection))
                rows.append(rr)
            # Exact expectation under a uniform random contiguous start.
            possible=[metric(range(t,t+k),gold,scores) for t in range(n-k+1)]
            r=dict(id=sid,genre=genre,N=n,fraction=fraction,k=k,method='random',retained_fraction=k/n)
            r['word_fraction']=sum(sum(len(words(sentences[i])) for i in range(t,t+k)) for t in range(n-k+1))/(n-k+1)/sum(len(words(s)) for s in sentences)
            for field in possible[0]:r[field]=sum(x[field] for x in possible)/len(possible)
            r['selected_indices']='exact expectation';rows.append(r)
            if sid=='lecture_0' and fraction==.2:
                examples.append({'id':sid,'scores':scores,'gold':[a,b],'window':[start,start+k],'k':k})
    summary=[]
    for genre in ['all','lecture','meeting','conversation']:
        for fraction in [.1,.2,.3,.5]:
            for method in ['first','random','topk','sliding']:
                selected=[r for r in rows if r['fraction']==fraction and r['method']==method and (genre=='all' or r['genre']==genre)]
                rr=dict(genre=genre,fraction=fraction,method=method,n=len(selected))
                for field in ['full_hit','any_hit','gold_recall','score_sum','runs','retained_fraction','word_fraction']:
                    rr[field]=float(np.mean([r[field] for r in selected]))
                summary.append(rr)
    save_csv(ROOT/'results/raw.csv',rows);save_csv(ROOT/'results/summary.csv',summary);save_csv(ROOT/'results/annotation_audit.csv',audits)
    bench=benchmark();save_csv(ROOT/'results/timing.csv',bench)
    timing_names={('naive',1000):'NaiveSmall',('naive',3000):'NaiveMedium',('naive',10000):'NaiveLarge',('sliding',1000):'SlideSmall',('sliding',3000):'SlideMedium',('sliding',10000):'SlideLarge'}
    (ROOT/'results/timing_values.tex').write_text('\n'.join('\\newcommand{\\'+timing_names[(r['method'],r['N'])]+'}{'+f"{r['median_ms']:.4f}"+'}' for r in bench)+'\n',encoding='utf-8')
    counts=Counter(x['text_relation'] for x in audits)
    checks.update({'records':len(data),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                   'source_bytes':source.stat().st_size,'unique_ids':len({x['metadata']['id'] for x in data}),
                   'sentence_min':min(n_sizes),'sentence_max':max(n_sizes),'sentence_mean':float(np.mean(n_sizes)),
                   'gold_size_counts':dict(Counter(g_sizes)),'text_relation_counts':dict(counts),
                   'real_window_checks':len(data)*4,'raw_rows':len(rows),
                   'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__,
                   'platform':platform.platform(),'cpu':platform.processor()})
    # Annotation robustness: report recall on exact-text matches without tuning.
    exact={x['id'] for x in audits if x['text_relation']=='exact'}
    checks['exact_subset_20pct']={m:float(np.mean([r['full_hit'] for r in rows if r['id'] in exact and r['fraction']==.2 and r['method']==m])) for m in ['first','random','topk','sliding']}
    (ROOT/'results/verification.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    # Main table: generate independent language-specific tables from identical numbers.
    for lang in ['zh','en']:
        labels={'first':'开头裁剪','random':'随机窗口','topk':'分数 Top-k','sliding':'滑动窗口'} if lang=='zh' else {'first':'First','random':'Random window','topk':'Score top-$k$','sliding':'Sliding window'}
        header=('方法 & 10\\% & 20\\% & 30\\% & 50\\%' if lang=='zh' else 'Method & 10\\% & 20\\% & 30\\% & 50\\%')+'\\\\\n'
        lines=['\\begin{tabular}{lrrrr}','\\toprule',header,'\\midrule']
        for method in labels:
            values=[next(r['full_hit'] for r in summary if r['genre']=='all' and r['fraction']==fraction and r['method']==method) for fraction in [.1,.2,.3,.5]]
            lines.append(labels[method]+' & '+' & '.join(f'{v*100:.2f}' for v in values)+'\\\\')
        lines+=['\\bottomrule','\\end{tabular}']
        (ROOT/f'results/main_table_{lang}.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    plt.rcParams.update({'font.size':9,'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axs=plt.subplots(1,2,figsize=(7.6,2.8))
    for method,label,c,mk in [('first','First','#666666','o'),('random','Random window','#E69F00','^'),('topk','Score top-k','#009E73','D'),('sliding','Sliding window','#0072B2','s')]:
        rr=[r for r in summary if r['genre']=='all' and r['method']==method]
        axs[0].plot([r['fraction']*100 for r in rr],[r['full_hit']*100 for r in rr],label=label,color=c,marker=mk,ms=4)
        rr=[r for r in summary if r['genre'] in ['lecture','meeting','conversation'] and r['method']==method and r['fraction']==.2]
        axs[1].plot(range(3),[r['full_hit']*100 for r in rr],label=label,color=c,marker=mk,ms=4)
    axs[0].set_xlabel('Nominal sentence budget (%)');axs[0].set_ylabel('Full key-span hit rate (%)');axs[0].set_xticks([10,20,30,50]);axs[0].legend(fontsize=7)
    axs[1].set_xticks(range(3),['Lecture','Meeting','Conversation']);axs[1].set_ylabel('Full key-span hit rate (%)');axs[1].set_title('20% nominal budget')
    for ax in axs:ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(ROOT/'figures/retrieval.pdf',bbox_inches='tight');fig.savefig(ROOT/'figures/retrieval.png',dpi=150,bbox_inches='tight');plt.close(fig)
    e=examples[0];fig,ax=plt.subplots(figsize=(4.8,2.6));x=np.arange(len(e['scores']))
    ax.bar(x+1,e['scores'],color='#999999');a,b=e['window'];ax.axvspan(a+.5,b+.5,color='#0072B2',alpha=.15,label='Selected window')
    a,b=e['gold'];ax.axvspan(a+.5,b+.5,color='#D55E00',alpha=.3,label='Annotated key span')
    ax.set_xlabel('Sentence index');ax.set_ylabel('TF-IDF cosine');ax.legend(fontsize=7);fig.tight_layout();fig.savefig(ROOT/'figures/example.pdf',bbox_inches='tight');fig.savefig(ROOT/'figures/example.png',dpi=150,bbox_inches='tight');plt.close(fig)
    print(json.dumps(checks,indent=2));print('MAIN',json.dumps([r for r in summary if r['genre']=='all'],indent=2));print('TIMING',json.dumps(bench))

if __name__=='__main__':main()
