"""Prepare an auditable, unexecuted request from a downloaded bundle. Never calls a provider."""

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from finsight.research.narrative import ModelConfig
from finsight.research.preparation import prepare_request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--verification",
        type=Path,
        required=True,
        help="Dated model/pricing verification record; never a credential file",
    )
    args = parser.parse_args()
    verification = json.loads(args.verification.read_text())
    config = ModelConfig.from_verification(verification)
    with zipfile.ZipFile(args.bundle) as archive:
        evidence = json.loads(archive.read("model-evidence.json"))
    original_bytes = len(json.dumps(evidence, ensure_ascii=False).encode())
    prepared = prepare_request(evidence, config)
    evidence, payload = prepared.evidence, prepared.payload
    encoded, planned = prepared.encoded, prepared.estimate
    manifest = {
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "state": "prepared_offline_not_authorized_for_execution",
        "company": evidence["company"],
        "research_cutoff": evidence["research_cutoff"],
        "model": config.model,
        "verification": verification,
        "estimated_maximum_charge": planned,
        "proposed_fixed_cap_usd": str(config.cap_usd),
        "original_evidence_bytes": original_bytes,
        "max_requests": config.max_requests,
        "automatic_retries": 0,
        "request_sha256": hashlib.sha256(encoded).hexdigest(),
        "request_file_bytes": len(encoded),
        "serialized_evidence_bytes": len(payload["input"].encode()),
        "bundle_sha256": hashlib.sha256(args.bundle.read_bytes()).hexdigest(),
        "model_calls": 0,
        "actual_spend_usd": "0",
        "provider_latency_seconds": None,
        "provider_usage": None,
        "application_generated_analysis": None,
        "required_before_execution": [
            "At the final API stage, recheck model availability, deprecation, supported settings and current pricing; this preparation does not inspect credentials.",
            "Configure secure provider access only when that final stage is authorized.",
            "Obtain explicit approval of this exact request, displayed estimate and one-request cap before paid execution.",
        ],
        "boundaries": [
            "Only supplied evidence; no web tools, annual substitution or invented causation.",
            "Quantitative claims must match full eligible records exactly, including metric, period, currency, unit and source.",
            "Structured and unsupported tables are not eligible model claim support.",
            "Prose support checks are mechanical; human review must assess relevance and causation.",
            "Reservation survives timeout, invalid output or HTTP failure. Single-request ledger prevents retries.",
        ],
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2))
    (args.output / "request.json").write_bytes(encoded)
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(
        json.dumps(
            {
                k: manifest[k]
                for k in [
                    "state",
                    "model",
                    "serialized_evidence_bytes",
                    "estimated_maximum_charge",
                    "proposed_fixed_cap_usd",
                    "model_calls",
                ]
            }
        )
    )


if __name__ == "__main__":
    main()
