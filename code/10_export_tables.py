import csv
from pathlib import Path

dist=list(csv.DictReader(open('results/automated_candidate_distribution.csv',encoding='utf-8')))
for source,name in [('BLV_USER_QUESTION','blv_intent_distribution.csv'),('AI_DESCRIPTION','ai_output_distribution.csv')]:
    rows=[r for r in dist if r['source_type']==source]
    with open(Path('results')/name,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
dreams=list(csv.DictReader(open('data/dreambank/processed/dream_reports.csv',encoding='utf-8')))
summary=[]
for group in sorted({r['blindness_group'] for r in dreams}):
    x=[r for r in dreams if r['blindness_group']==group]
    summary.append({'blindness_group':group,'n_dream_reports':len(x),'n_pseudonymous_dreamers':len({r['dreamer_id_pseudonymous'] for r in x}),'analysis_status':'CORPUS_METADATA'})
with open('results/dream_meta_summary.csv','w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=summary[0].keys());w.writeheader();w.writerows(summary)
flow=[{'stage':'DreamBank candidate series','n':400,'unit':'dream reports','note':'Blind F, Blind M, Edna queried.'},{'stage':'Primary free-recall corpus','n':381,'unit':'dream reports','note':'Blind F/M only; Edna interview material not treated as comparable free recall.'},{'stage':'VizWiz text corpus','n':24842,'unit':'questions','note':'Train + validation annotations only.'},{'stage':'Released AI text corpus','n':28,'unit':'descriptions','note':'chi25_lmm released examples; exploratory only.'}]
with open('results/sample_flow.csv','w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=flow[0].keys());w.writeheader();w.writerows(flow)
