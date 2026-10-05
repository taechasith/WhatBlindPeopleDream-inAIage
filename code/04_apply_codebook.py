"""Transparent lexical candidate coding; exploratory only, never human labels."""
import csv, re
from pathlib import Path

RULES={
"visual":r"\b(see|saw|look|color|colour|bright|dark|light|picture|image|shape|visual)\b","auditory":r"\b(hear|heard|sound|noise|voice|said|music|quiet|loud)\b","tactile":r"\b(touch|felt|feel|soft|rough|smooth|hold|held|pressure)\b","olfactory":r"\b(smell|smelled|scent|odor)\b","gustatory":r"\b(taste|tasted|flavor|eat|eating)\b","proprioceptive":r"\b(walk|walking|leg|arm|body|wheelchair|stand|standing)\b","vestibular":r"\b(fall|falling|dizzy|spin|sway)\b","interoceptive":r"\b(heart|breathe|breathing|hungry|nausea)\b","thermal":r"\b(hot|cold|warm|heat)\b","pain":r"\b(pain|hurt|aching|ache)\b","spatial_layout":r"\b(room|house|table|door|inside|outside|beside|behind|between)\b","distance_depth":r"\b(near|far|distance|deep|close|ahead)\b","direction_orientation":r"\b(left|right|behind|front|upstairs|downstairs|north|south)\b","motion":r"\b(moving|moved|walk|run|going|approach|flight)\b","social_context":r"\b(friend|mother|father|people|person|family|talking|with)\b","identity_inference":r"\b(looks like|appears to|seems to|young|old|woman|man|beautiful)\b","emotion":r"\b(afraid|scared|anxious|happy|sad|angry|upset|feel)\b","threat":r"\b(threat|danger|fire|attack|gun|afraid|scared|risk)\b","safety":r"\b(safe|danger|risk|careful|avoid|warning|emergency)\b","uncertainty":r"\b(maybe|perhaps|might|seems|appears|not sure|can't tell|unclear)\b","privacy":r"\b(private|medical|bloodsugar|address|phone|mail|credit)\b","agency":r"\b(i want|choose|decide|should i|can i|help me)\b","task_relevance":r"\b(what|which|where|how|can you|tell me|is this)\b","text_reading":r"\b(read|say|label|text|number|name|captcha)\b","navigation":r"\b(where|direction|walk|door|stairs|navigate|route|guide)\b","unsupported_information":r"\b(i apologize|not 100%|confusion|actually)\b","ambiguity":r"\b(unclear|not sure|can't tell|could be|might be)\b","intent_match":r"\b(what|which|where|how|can you|tell me)\b","nightmare":r"\b(nightmare|terrifying|chased)\b"}

UNAVAILABLE = {
    "DREAM": {"task_relevance", "intent_match", "unsupported_information"},
    "BLV_USER_QUESTION": {"intent_match", "unsupported_information"},
    "AI_DESCRIPTION": {"task_relevance", "intent_match", "unsupported_information"},
}

def label(text, source_type):
    text=text.lower()
    return {k:("" if k in UNAVAILABLE[source_type] else int(bool(re.search(v,text)))) for k,v in RULES.items()}

def load(path,textcol,kind):
    with Path(path).open(encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if kind and r.get('source_type')!=kind: continue
            t=r.get(textcol,'')
            if t: yield r.get('dream_id') or r.get('item_id'),kind or 'DREAM',t

def main():
    rows=[]
    for item,kind,text in load('data/dreambank/processed/dream_reports.csv','dream_text',None): rows.append({'item_id':item,'source_type':'DREAM',**label(text,'DREAM')})
    for item,kind,text in load('data/ai_sensory/processed/corpus_items.csv','input_text','BLV_USER_QUESTION'): rows.append({'item_id':item,'source_type':kind,**label(text,kind)})
    for item,kind,text in load('data/ai_sensory/processed/corpus_items.csv','output_text','AI_DESCRIPTION'): rows.append({'item_id':item,'source_type':kind,**label(text,kind)})
    out=Path('results');out.mkdir(exist_ok=True)
    with (out/'automated_candidate_labels.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    summary=[]
    for kind in sorted({r['source_type'] for r in rows}):
        group=[r for r in rows if r['source_type']==kind]
        for c in RULES:
            applicable=[r for r in group if r[c] != ""]
            summary.append({'source_type':kind,'category':c,'n_items':len(group),'n_applicable':len(applicable),'n_expressed':sum(int(r[c]) for r in applicable) if applicable else '', 'proportion':sum(int(r[c]) for r in applicable)/len(applicable) if applicable else '', 'analysis_status':'EXPLORATORY_AUTOMATED_CANDIDATE' if applicable else 'NOT_ESTIMABLE_NO_VALIDATION_BASIS'})
    with (out/'automated_candidate_distribution.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=summary[0].keys());w.writeheader();w.writerows(summary)

if __name__=='__main__': main()
