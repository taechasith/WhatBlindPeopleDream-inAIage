"""Exploratory distribution alignment and bootstrap uncertainty for candidate labels."""
import csv, math, random
from collections import defaultdict
from pathlib import Path

random.seed(20261005)
src=Path('results/automated_candidate_labels.csv')
rows=list(csv.DictReader(src.open(encoding='utf-8')))
cats=[x for x in rows[0] if x not in ('item_id','source_type')]
groups=defaultdict(list)
for r in rows: groups[r['source_type']].append(r)

def prof(items): return [sum(int(x[c]) for x in items)/len(items) for c in cats]
def cosine(a,b):
    return sum(x*y for x,y in zip(a,b))/(math.sqrt(sum(x*x for x in a))*math.sqrt(sum(y*y for y in b)))
def hellinger(a,b):
    sa=sum(a); sb=sum(b); a=[x/sa for x in a]; b=[x/sb for x in b]
    return math.sqrt(sum((math.sqrt(x)-math.sqrt(y))**2 for x,y in zip(a,b)))/math.sqrt(2)
def js(a,b):
    sa=sum(a); sb=sum(b); a=[x/sa for x in a]; b=[x/sb for x in b]; m=[(x+y)/2 for x,y in zip(a,b)]
    def kl(p,q): return sum(x*math.log2(x/y) for x,y in zip(p,q) if x)
    return (kl(a,m)+kl(b,m))/2

out=[]
names=sorted(groups)
for i,a in enumerate(names):
 for b in names[i+1:]:
    pa,pb=prof(groups[a]),prof(groups[b]); boot=[]
    # 100 resamples: deliberately modest because the 24k-question corpus makes
    # this diagnostic expensive; intervals remain exploratory.
    for _ in range(100):
      aa=random.choices(groups[a],k=len(groups[a])); bb=random.choices(groups[b],k=len(groups[b]))
      boot.append(js(prof(aa),prof(bb)))
    boot.sort()
    out.append({'comparison':f'{a}__vs__{b}','n_a':len(groups[a]),'n_b':len(groups[b]),'js_divergence':js(pa,pb),'js_ci_low':boot[2],'js_ci_high':boot[97],'cosine_similarity':cosine(pa,pb),'hellinger_distance':hellinger(pa,pb),'analysis_status':'EXPLORATORY_AUTOMATED_CANDIDATE'})
Path('results').mkdir(exist_ok=True)
with Path('results/alignment_metrics.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)

# Largest signed AI-minus-BLV candidate-label proportions.
a=prof(groups['AI_DESCRIPTION']); b=prof(groups['BLV_USER_QUESTION'])
mis=sorted(zip(cats,a,b),key=lambda x:abs(x[1]-x[2]),reverse=True)
with Path('results/human_ai_mismatch.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['category','ai_proportion','blv_question_proportion','difference_ai_minus_blv','analysis_status']);w.writeheader()
 for c,x,y in mis:w.writerow({'category':c,'ai_proportion':x,'blv_question_proportion':y,'difference_ai_minus_blv':x-y,'analysis_status':'EXPLORATORY_AUTOMATED_CANDIDATE'})
