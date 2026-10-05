"""Pre-specified diagnostics: dream subgroup and lexical-rule sensitivity."""
import csv
from pathlib import Path

labels={r['item_id']:r for r in csv.DictReader(open('results/automated_candidate_labels.csv',encoding='utf-8'))}
dreams=list(csv.DictReader(open('data/dreambank/processed/dream_reports.csv',encoding='utf-8')))
cats=[x for x in next(iter(labels.values())) if x not in ('item_id','source_type')]
out=[]
for group in ('CONGENITAL','ACQUIRED_UNSPECIFIED'):
 d=[labels[x['dream_id']] for x in dreams if x['blindness_group']==group]
 for c in cats:
  applicable=[x for x in d if x[c] != '']
  out.append({'test':'dream_group_candidate_prevalence','subset':group,'category':c,'n':len(d),'n_applicable':len(applicable),'proportion':sum(int(x[c]) for x in applicable)/len(applicable) if applicable else '','status':'EXPLORATORY_AUTOMATED_CANDIDATE' if applicable else 'NOT_ESTIMABLE_NO_VALIDATION_BASIS'})
with open('results/robustness.csv','w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
