"""Prepare an auditable, unexecuted request from a downloaded bundle. Never calls a provider."""

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from finsight.research.narrative import ModelConfig, estimate, request_payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Planning scenario only. Live current pricing/model access must be checked before approval.
    config = ModelConfig("gpt-4.1-mini", Decimal("0.40"), Decimal("1.60"), Decimal("0.25"))
    with zipfile.ZipFile(args.bundle) as archive:
        evidence = json.loads(archive.read("model-evidence.json"))
    payload = request_payload(config, evidence)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode()
    planned = estimate(config, evidence)
    manifest = {
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "state": "blocked_before_spending_authorization",
        "company": evidence["company"],
        "research_cutoff": evidence["research_cutoff"],
        "candidate_model": config.model,
        "compatibility": "Responses API with JSON-object output; candidate based on known interface, current official documentation and account access not yet verified",
        "pricing_status": "UNVERIFIED planning scenario only; official pricing request denied by runtime proxy",
        "pricing_sources_to_verify": [
            "https://openai.com/api/pricing/",
            "https://developers.openai.com/api/docs/models/gpt-4.1-mini",
        ],
        "scenario_input_usd_per_million": str(config.input_per_million),
        "scenario_output_usd_per_million": str(config.output_per_million),
        "scenario_estimate": planned,
        "proposed_fixed_cap_usd": str(config.cap_usd),
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
            "Publish reviewed narrow OpenAI host and FINSIGHT_OPENAI_API_KEY binding configuration; retest actual access.",
            "Verify current official model compatibility, rates and account availability using no-cost requests.",
            "Recompute this exact request estimate at verified rates, keep within fixed cap and obtain explicit approval for one request.",
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
    (args.output / "request.json").write_bytes(encoded)
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(
        json.dumps(
            {
                k: manifest[k]
                for k in [
                    "state",
                    "candidate_model",
                    "serialized_evidence_bytes",
                    "scenario_estimate",
                    "proposed_fixed_cap_usd",
                    "model_calls",
                ]
            }
        )
    )


if __name__ == "__main__":
    main()
