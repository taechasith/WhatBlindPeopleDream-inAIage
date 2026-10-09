"""Historical future-only Study 0 human-validation packet builder.

The active CHI public-data study collects zero new human labels. This retained
script is archived under ``future_human_validation/`` and must not be invoked by
the current computational measurement pipeline.
"""
import argparse
import csv, random
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="data/study0/annotation")
args = parser.parse_args()
random.seed(20261005)
categories = [
 "visual","auditory","tactile","olfactory","gustatory","proprioceptive","vestibular","interoceptive","thermal","pain","spatial_layout","distance_depth","direction_orientation","motion","social_context","identity_inference","emotion","threat","safety","uncertainty","privacy","agency","task_relevance","text_reading","navigation","unsupported_information","ambiguity","intent_match","nightmare"
]
sources = [("DREAM", Path("data/dreambank/processed/dream_reports.csv"), "dream_text", None), ("BLV_QUESTION", Path("data/ai_sensory/processed/corpus_items.csv"), "input_text", "BLV_USER_QUESTION"), ("AI_DESCRIPTION", Path("data/ai_sensory/processed/corpus_items.csv"), "output_text", "AI_DESCRIPTION")]
items=[]
for kind,path,text_col,source_filter in sources:
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if source_filter and r.get("source_type") != source_filter: continue
            if r.get(text_col): items.append({"source_stratum":kind,"item_id":r.get("dream_id",r.get("item_id")),"text":r[text_col]})
sample=[]
for kind in sorted({x["source_stratum"] for x in items}):
    group=[x for x in items if x["source_stratum"]==kind]
    sample += random.sample(group, round(len(group)*.20))
random.shuffle(sample)
out=Path(args.output); out.mkdir(parents=True, exist_ok=True)
for coder in ("coder_a","coder_b"):
    with (out/f"{coder}.csv").open("w",newline="",encoding="utf-8") as f:
        fields=["source_stratum","item_id","text"]+categories
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(sample)
with (out/"README.md").open("w",encoding="utf-8") as f:
    f.write("FUTURE MATCHED-HUMAN VALIDATION ONLY. Use 0=not expressed, 1=expressed, NA=cannot determine. Do not share completed labels between coders before first reliability calculation. Do not commit or include raw text in anonymous/public supplements.\n")
print(len(sample))
