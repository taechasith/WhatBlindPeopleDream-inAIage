# Blinded human-coder ingestion runbook v1.1

Use only after the applicable ethics determination permits coding and three
genuine independent coder returns exist. Distribute only the appropriate
`coder_a`, `coder_b`, or `coder_c` directory from the private v1.1 package.
Do not distribute the old v1 package.

Preserve each received original unchanged under `annotation/received/`, then
run:

```powershell
& .\.env_vlm\Scripts\python.exe code\17_lock_human_coder_files.py `
  --package-root annotation_public\private\human_validation_v1_1 `
  --coder-a annotation\received\coder_a.csv `
  --coder-b annotation\received\coder_b.csv `
  --coder-c annotation\received\coder_c.csv `
  --attestation-a annotation\received\coder_a_attestation.csv `
  --attestation-b annotation\received\coder_b_attestation.csv `
  --attestation-c annotation\received\coder_c_attestation.csv `
  --outdir annotation\locked\human_validation_v1_1_lock `
  --failure-report annotation\locked\human_validation_v1_1_lock_failure.json
```

Do not edit an original return after a failed validation. A successful lock must
create `LOCK_COMPLETE.json` before reliability, adjudication, Alt-Test, any
synthetic scaling, unblinding, or RQ2--RQ5.
