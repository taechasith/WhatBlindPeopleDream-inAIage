# Blinded human-coder ingestion runbook v1

Use this runbook only after the applicable institutional ethics determination
permits the independent annotation workflow and three genuine human coders have
returned completed files. It does not authorize recruitment or substitute an AI
for a missing coder.

## Before running

- Preserve each received original file unchanged under ignored
  `annotation/received/`.
- Obtain a separate completed attestation from each coder using
  `HUMAN_CODER_INDEPENDENCE_ATTESTATION_TEMPLATE.csv`.
- Confirm that no coder has received a condition map, synthetic-panel output,
  another coder's labels, or an LLM co-coder.
- Do not open the private condition mapping or inspect RQ2--RQ5.

## Lock three returns

Run from the repository root, replacing only the received-file paths. The
private package root is the already frozen 600-row package; this command does
not make its contents public.

```powershell
& .\.env_vlm\Scripts\python.exe code\17_lock_human_coder_files.py `
  --package-root annotation_public\private\human_validation_v1 `
  --coder-a annotation\received\coder_a.csv `
  --coder-b annotation\received\coder_b.csv `
  --coder-c annotation\received\coder_c.csv `
  --attestation-a annotation\received\coder_a_attestation.csv `
  --attestation-b annotation\received\coder_b_attestation.csv `
  --attestation-c annotation\received\coder_c_attestation.csv `
  --outdir annotation\locked\human_validation_v1_lock `
  --failure-report annotation\locked\human_validation_v1_lock_failure.json
```

If validation fails, do not edit an original return. Read the failure report,
preserve the original, and create a separately named corrected derivative with a
clerical-correction log. If it succeeds, require `LOCK_COMPLETE.json` before
any reliability work.

## Run pre-adjudication reliability

```powershell
& .\.env_vlm\Scripts\python.exe code\14_public_coding_reliability.py `
  --lock-dir annotation\locked\human_validation_v1_lock `
  --cluster-map annotation\locked\reliability_cluster_map_v1.csv `
  --applicability-precheck annotation_public\CONSTRUCT_APPLICABILITY_PRECHECK_v1.csv `
  --bootstrap-policy annotation_public\RELIABILITY_BOOTSTRAP_POLICY_v1.md `
  --outdir results\human_reliability_pre_adjudication_v1
```

Archive the four result files, manifest, and checksums before any adjudication.
The current protocol deliberately emits `THRESHOLD_NOT_PREDEFINED` for
text-packet-applicable constructs because no numerical reliability threshold was
precommitted. It does not permit a post-hoc PASS/BORDERLINE judgment, full-scale
synthetic scaling, unblinding, or RQ2--RQ5.
