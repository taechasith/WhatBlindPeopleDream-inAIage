"""Apply the 2026-10-08 verified literature-audit corrections reproducibly."""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path: Path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f)), csv.DictReader

def write(path: Path, rows: list[dict], fields: list[str]):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def append_once(rows, row):
    if not any(r['paper_id'] == row['paper_id'] for r in rows): rows.append(row)

def main():
    novelty = ROOT/'NOVELTY_MATRIX.csv'; rows, _ = read(novelty); fields = list(rows[0])
    for r in rows:
        if r['paper_id'] == 'ILIC2023':
            old = {k:r[k] for k in ('reciprocal_model','our_overlap','our_difference','novelty_threat')}
            r.update(privacy='no', cognition='imagery', crossmodal='yes', longitudinal='no', reciprocal_model='no', our_overlap=old['reciprocal_model'], our_difference=old['our_overlap'], novelty_threat=old['our_difference'], notes=old['novelty_threat'])
        elif r['paper_id'] in {'KREISS2022','MOHANBABU2024','KAPUR2024','XIE2025','KARMOLEGKOU2025','SCENESCOUT2025','GUIDEDOG2026'}:
            old = {k:r[k] for k in ('reciprocal_model','our_overlap','our_difference','novelty_threat')}
            r.update(reciprocal_model='no', our_overlap=old['reciprocal_model'], our_difference=old['our_overlap'], novelty_threat=old['our_difference'], notes=old['novelty_threat'])
        if r['paper_id'] == 'KARMOLEGKOU2025': r['ai_system'] = '12_MLLMs'
        if r['paper_id'] == 'GONZALEZ2025':
            r.update(venue='arXiv; CV4A11y presentation', peer_review_status='preprint', our_difference='Uses retrieved visually similar prior-image questions, not target paired questions; no accessibility-policy condition or DreamSpace. DataCite classifies the DOI as a preprint; no archival proceedings article was verified.')
        if r['paper_id'] == 'SCENESCOUT2025':
            r.update(paper_id='SCENESCOUT2026', year='2026', venue='CHI', peer_review_status='peer_reviewed', notes='Published CHI 2026 revision; corrects earlier preprint classification; street-level navigation task.')
    def matrix_row(pid, citation, year, venue, peer, pop, ai, gen, multi, intent, overlap, difference, threat, notes):
        r={k:'NOT_REPORTED' for k in fields}; r.update(paper_id=pid,citation=citation,year=year,venue=venue,peer_review_status=peer,blind_or_blv_population=pop,dream_data='none',ai_system=ai,generative_ai=gen,multimodal_ai=multi,user_intent=intent,reciprocal_model='no',our_overlap=overlap,our_difference=difference,novelty_threat=threat,notes=notes); return r
    append_once(rows, matrix_row('GONZALEZ2025','Gonzalez Penuela et al., Guiding MLLMs with BLV Questions', '2025','arXiv; CV4A11y presentation','preprint','BLV','MLLM','yes','yes','yes','BLV-question-guided MLLM descriptions','Uses retrieved visually similar prior-image questions, not target paired questions; no accessibility-policy condition or DreamSpace. DataCite classifies the DOI as a preprint; no archival proceedings article was verified.','high','Do not claim first use of BLV questions to guide MLLMs.'))
    append_once(rows, matrix_row('GONZALEZ2026','Gonzalez Penuela et al., How MLLMs Support Access to Visual Information','2026','CHI','peer_reviewed','BLV','MLLM','yes','yes','yes','Real-world BLV MLLM-use diary','No DreamSpace, shared ontology, or same-item prompt intervention.','high','Twenty-participant two-week diary study.'))
    append_once(rows, matrix_row('GARG2026','Garg et al., Image Quality and Product Captioning with VLMs','2026','CHI','peer_reviewed','BLV','VLM','yes','yes','yes','BLV-captured image-quality accessibility evaluation','No question steering or DreamSpace comparison.','medium','Image quality is a primary-study limitation comparator.'))
    write(novelty, rows, fields)

    evidence=ROOT/'NEW_EVIDENCE_2023_2027.csv'; rows,_=read(evidence); fields=list(rows[0])
    for r in rows:
        if r['paper_id']=='ILIC2023': r['doi']='10.3389/fnint.2023.1204129'
        if r['paper_id']=='KARMOLEGKOU2025': r.update(n_reports_or_examples='12_MLLMs',doi='10.18653/v1/2025.acl-long.1260')
        if r['paper_id']=='GONZALEZ2025': r.update(method='preprint',data_type='preprint',limitations='Not target paired question; DataCite classifies this DOI as a preprint. An official CV4A11y presentation is documented but archival proceedings status was not verified.')
        if r['paper_id']=='GARG2026': r['citation']='Garg et al. “It\'s trained by non-disabled people”: Evaluating How Image Quality Affects Product Captioning with Vision-Language Models'
    def ev(pid,citation,year,pop,n,method,result,dream,ai,strength,lim,doi,url):
        return dict(zip(fields,[pid,citation,year,pop,'NOT_REPORTED',n,method,'published_study',result,dream,ai,strength,lim,doi,url]))
    append_once(rows,ev('GONZALEZ2025','Gonzalez Penuela et al. Guiding Multimodal Large Language Models with Blind and Low Vision People Visual Questions for Proactive Visual Interpretations','2025','BLV','NOT_REPORTED','preprint','Retrieved prior VizWiz-LF questions guide target-image MLLM descriptions','none','direct','comparative_evaluation','Not target paired question; DataCite classifies this DOI as a preprint. An official CV4A11y presentation is documented but archival proceedings status was not verified.','10.48550/arXiv.2510.01576','https://arxiv.org/abs/2510.01576'))
    append_once(rows,ev('GONZALEZ2026','Gonzalez Penuela et al. How Multimodal Large Language Models Support Access to Visual Information','2026','BLV','20_participants','diary_study','Two-week diary of real-world MLLM use','none','direct','observational','No dream or causal cognition outcome','10.1145/3772318.3793266','https://doi.org/10.1145/3772318.3793266'))
    append_once(rows,ev('GARG2026','Garg et al. “It\'s trained by non-disabled people”: Evaluating How Image Quality Affects Product Captioning with Vision-Language Models','2026','BLV','86_survey_participants_1859_images','survey_and_evaluation','BLV-captured image quality affects captioning evaluation','none','direct','comparative_evaluation','No question steering or dream evidence','10.1145/3772318.3791309','https://doi.org/10.1145/3772318.3791309'))
    append_once(rows,ev('DOORE2024','Doore et al. Images, Words, and Imagination','2024','BLV','NOT_REPORTED','qualitative_study','Spatial and contextual descriptions support mental models','mechanism_context','accessibility_context','observational','Not AI-induced cognition or dream evidence','10.3390/jimaging10010026','https://doi.org/10.3390/jimaging10010026'))
    write(evidence,rows,fields)

    library=ROOT/'literature/candidate_library.csv'; rows,_=read(library); fields=list(rows[0])
    for r in rows:
        if r['paper_id']=='ILIC2023': r['doi_or_url']='https://doi.org/10.3389/fnint.2023.1204129'
        if r['paper_id']=='SCENESCOUT2025': r.update(venue='arXiv',doi_or_url='https://arxiv.org/abs/2504.09227',peer_review_status='preprint',screening_decision='superseded',reason='Preprint superseded by published CHI 2026 revision.')
        if r['paper_id']=='EYE4B2025': r.update(peer_review_status='withdrawn_preprint',screening_decision='exclude_withdrawn',reason='arXiv record withdrawn; do not use as current evidence.')
        if r['paper_id']=='GONZALEZ2025': r.update(venue='arXiv; CV4A11y presentation',peer_review_status='preprint',reason='DataCite registers the DOI as a preprint; an official CV4A11y presentation is documented, but no archival proceedings article was verified.')
        if r['paper_id']=='GARG2026': r['citation']='Garg, et al. “It\'s trained by non-disabled people”: Evaluating How Image Quality Affects Product Captioning with Vision-Language Models.'
    for row in [
        ['SCENESCOUT2026','Jain, G.; Findlater, L.; Gleason, C. SceneScout: Towards AI-Driven Access to Street Level Imagery for Blind Users.','2026','CHI','https://doi.org/10.1145/3772318.3790449','peer_reviewed','include','Published CHI revision of earlier preprint.'],
        ['GONZALEZ2025','Gonzalez Penuela, A.; Arias-Russi, A.; Capriles, F. Guiding Multimodal Large Language Models with Blind and Low Vision People Visual Questions for Proactive Visual Interpretations.','2025','arXiv; CV4A11y presentation','https://doi.org/10.48550/arXiv.2510.01576','preprint','include','DataCite registers the DOI as a preprint; an official CV4A11y presentation is documented, but no archival proceedings article was verified.'],
        ['GONZALEZ2026','Gonzalez Penuela, A.; et al. How Multimodal Large Language Models Support Access to Visual Information.','2026','CHI','https://doi.org/10.1145/3772318.3793266','peer_reviewed','include','Real-world BLV MLLM-use diary.'],
        ['GARG2026','Garg, et al. “It\'s trained by non-disabled people”: Evaluating How Image Quality Affects Product Captioning with Vision-Language Models.','2026','CHI','https://doi.org/10.1145/3772318.3791309','peer_reviewed','include','Image-quality accessibility comparator.'],
        ['DOORE2024','Doore, et al. Images, Words, and Imagination.','2024','J. Imaging','https://doi.org/10.3390/jimaging10010026','peer_reviewed','include','Mental-model framing only; no causal AI/dream evidence.']]: append_once(rows,dict(zip(fields,row)))
    write(library,rows,fields)

    audit=ROOT/'refs/doi_audit.csv'; rows,_=read(audit); fields=list(rows[0])
    for r in rows:
        if r['paper_id'] == 'ORTIZ2011':
            r.update(doi='10.1371/journal.pone.0023264', doi_resolution_source='PLOS_and_PubMed', verification_date='2026-10-10', notes='Corrected DOI: the previous .0023275 DOI resolves to an unrelated rat-neuroscience paper. Ortiz et al. is a mechanistic sensory-substitution precedent only; heterogeneous sample and post-hoc subgroup result.')
        elif r['paper_id'] == 'NEUROIMAGE2025':
            r.update(doi_resolution_source='PubMed_and_ScienceDirect', verification_date='2026-10-10', notes='Published in NeuroImage volume 325 (2026); DOI/online date is 2025. Long-term tactile intervention in blind children; mechanistic plausibility only.')
        elif r['paper_id'] == 'PALMIERI2026':
            r.update(doi_resolution_source='PubMed_and_Oxford_Academic', verification_date='2026-10-10', notes='Published in SLEEP 49(2) (2026); Crossref carries a 2025 online date. Presleep audiobook dream-incorporation method precedent; not AI-specific or BLV-specific.')
        elif r['paper_id'] == 'GONZALEZ2025':
            r.update(doi_resolution_source='DataCite_arXiv_and_ICCV_CV4A11y_program', peer_review_status='preprint', classification='preprint', verification_date='2026-10-10', notes='DataCite registers this DOI as a preprint. The official CV4A11y program lists a presentation, but no archival proceedings record was verified; do not call it peer-reviewed or a workshop article.')
    additions=[
      ('ILIC2023','10.3389/fnint.2023.1204129','PubMed_and_publisher','peer_reviewed','systematic_review','Systematic review; not primary completed AI or dream outcome evidence.'),('KREISS2022','10.18653/v1/2022.emnlp-main.309','ACL_Anthology','peer_reviewed','conference_article','BLV context-aware description evaluation; not dream evidence.'),('KARMOLEGKOU2025','10.18653/v1/2025.acl-long.1260','ACL_Anthology','peer_reviewed','conference_article','Official abstract reports twelve MLLMs.'),('GONZALEZ2025','10.48550/arXiv.2510.01576','DataCite_arXiv_and_ICCV_CV4A11y_program','preprint','preprint','DataCite registers this DOI as a preprint. The official CV4A11y program lists a presentation, but no archival proceedings record was verified; do not call it peer-reviewed or a workshop article.'),('GONZALEZ2026','10.1145/3772318.3793266','Crossref_and_author_manuscript','peer_reviewed','conference_article','CHI diary study; no dream or cognitive causal evidence.'),('GARG2026','10.1145/3772318.3791309','Crossref_and_author_manuscript','peer_reviewed','conference_article','CHI image-quality/product-captioning study.'),('SCENESCOUT2026','10.1145/3772318.3790449','Crossref_and_publisher_research_page','peer_reviewed','conference_article','Published CHI 2026 revision; corrects prior preprint classification.'),('DOORE2024','10.3390/jimaging10010026','publisher_and_Crossref','peer_reviewed','journal_article','Art-description mental-model context; not causal cognitive evidence.'),('ZUR2024','10.18653/v1/2024.emnlp-main.1125','ACL_Anthology','peer_reviewed','conference_article','Description-versus-caption metric study; does not validate this ontology.'),('CALDERON2025','10.18653/v1/2025.acl-long.782','ACL_Anthology','peer_reviewed','conference_article','Alt-Test methodological source; does not validate project judges automatically.'),('PATARANUTAPORN2025','10.1073/pnas.2519394122','publisher_PDF_and_Crossref','peer_reviewed','journal_article','Methodological validation caution; not BLV evidence.'),('ENVISAGE2026','10.1016/j.patcog.2026.114298','Crossref_and_publisher','peer_reviewed','journal_article','Pattern Recognition article. Bibliographic verification does not establish that its dataset is locally available or licensed for this study; consult the source gate.'),('NEUROIMAGE2024','10.1016/j.neuroimage.2024.120621','Crossref_and_PubMed','peer_reviewed','journal_article','Blindfolded-sighted sensory-substitution neural-dynamics study. Mechanistic context only; not blind-participant dream or AI-description outcome evidence.')]
    for pid,doi,source,peer,kind,note in additions:
        append_once(rows,dict(zip(fields,[pid,doi,source,'yes','yes','yes',peer,kind,'2026-10-08','PASS',note])))
    for r in rows:
        if r['paper_id'] in {'ENVISAGE2026', 'NEUROIMAGE2024'}:
            r['verification_date'] = '2026-10-10'
    write(audit,rows,fields)

if __name__ == '__main__': main()
