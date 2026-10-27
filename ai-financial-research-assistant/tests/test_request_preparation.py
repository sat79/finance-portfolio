import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from finsight.research.model_evidence import build_model_evidence
from finsight.research.models import from_snapshot
from finsight.research.narrative import ModelConfig, OpenAIProvider
from finsight.research.preparation import prepare_request
from finsight.research.report import manual_synthesis_bundle, report_bundle

ROOT = Path(__file__).parents[1]


def setup(monkeypatch):
    verification = json.loads(
        (ROOT / "docs/review-artifacts/2026-10-26-provider/model-verification.json").read_text()
    )
    for name, value in {
        "FINSIGHT_MODEL": verification["model"],
        "FINSIGHT_INPUT_USD_PER_MILLION": verification["reservation_input_usd_per_million"],
        "FINSIGHT_OUTPUT_USD_PER_MILLION": verification["output_usd_per_million"],
        "FINSIGHT_MODEL_CAP_USD": verification["cap_usd"],
    }.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("FINSIGHT_MAX_OUTPUT_TOKENS", raising=False)
    monkeypatch.delenv("FINSIGHT_REASONING_EFFORT", raising=False)
    with zipfile.ZipFile(
        ROOT / "docs/review-artifacts/2026-10-26-no-api/KSPI-research.zip"
    ) as archive:
        research = from_snapshot(json.loads(archive.read("research-evidence.json")))
    return verification, research


def test_ui_manual_pilot_and_transport_share_preparation(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    verification, research = setup(monkeypatch)
    config = ModelConfig.from_environment()
    assert config == ModelConfig.from_verification(verification)
    prepared = prepare_request(build_model_evidence(research), config)
    assert prepare_request(prepared.evidence, config) == prepared
    assert config.max_output_tokens == 2400 and config.reasoning_effort == "none"
    with zipfile.ZipFile(io.BytesIO(manual_synthesis_bundle(research, config=config))) as archive:
        assert archive.read("request.json") == prepared.encoded
        assert json.loads(archive.read("evidence.json")) == prepared.evidence
    bundle = tmp_path / "research.zip"
    bundle.write_bytes(report_bundle(research))
    record = tmp_path / "verification.json"
    record.write_text(json.dumps(verification))
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/prepare_synthesis_pilot.py"),
            "--bundle",
            str(bundle),
            "--verification",
            str(record),
            "--output",
            str(tmp_path / "pilot"),
        ],
        check=True,
        capture_output=True,
    )
    assert (tmp_path / "pilot/request.json").read_bytes() == prepared.encoded
    # Real UI preparation, no key or enabled provider.
    monkeypatch.setenv("FINSIGHT_ENABLE_MODEL", "0")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("FINSIGHT_OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("finsight.research.ui.find_companies", lambda *a: [research.company])
    monkeypatch.setattr("finsight.research.ui.run_research", lambda *a, **k: research)
    monkeypatch.setenv("SEC_USER_AGENT", "FinSight tests contact@example.org")
    app = AppTest.from_file(str(ROOT / "app/main.py"), default_timeout=30).run()
    app.text_input[0].set_value("Kaspi.kz")
    app.button[0].click().run()
    next(b for b in app.button if b.label == "Research selected company").click().run()
    assert not app.exception
    displayed = [json.loads(j.value) for j in app.get("json")]
    assert any(
        j.get("request_sha256") == prepared.request_sha256
        and j.get("reserved_cost_usd") == prepared.estimate["reserved_cost_usd"]
        for j in displayed
    )
    assert not any(b.label == "Generate optional narrative" for b in app.button)
    # Transport is stubbed; there is no external request or real credential.
    monkeypatch.setenv("FINSIGHT_ENABLE_MODEL", "1")
    monkeypatch.setenv("FINSIGHT_OPENAI_API_KEY", "fictional-test-placeholder")
    session = Mock()
    session.post.return_value.status_code = 200
    claim = next(iter(prepared.evidence["quantitative_evidence"].values()))
    session.post.return_value.json.return_value = {
        "status": "completed",
        "output": [
            {
                "content": [
                    {"type": "output_text", "text": json.dumps({"quantitative_claims": [claim]})}
                ]
            }
        ],
    }
    provider = OpenAIProvider(config, tmp_path / "ledger.jsonl", session)
    result = provider.generate(
        build_model_evidence(research),
        approved=True,
        expected_request_sha256=prepared.request_sha256,
    )
    assert session.post.call_args.kwargs["json"] == prepared.payload
    assert result["supplied_evidence"] == prepared.evidence
    assert result["estimate"] == prepared.estimate
    with pytest.raises(ValueError, match="Single-request|cap"):
        provider.generate(prepared.evidence, approved=True)
    assert session.post.call_count == 1
    # Approval belongs to the exact request, not to a reused checkbox after settings change.
    app.run()
    approval = next(c for c in app.checkbox if c.label.startswith("I approve"))
    original_key = approval.key
    approval.check().run()
    monkeypatch.setenv("FINSIGHT_MAX_OUTPUT_TOKENS", "2300")
    app.run()
    changed = next(c for c in app.checkbox if c.label.startswith("I approve"))
    assert changed.key != original_key and not changed.value


def test_changed_request_hash_fails_before_reservation(tmp_path, monkeypatch):
    _, research = setup(monkeypatch)
    session = Mock()
    provider = OpenAIProvider(ModelConfig.from_environment(), tmp_path / "ledger", session)
    with pytest.raises(ValueError, match="changed after review"):
        provider.generate(
            build_model_evidence(research), approved=True, expected_request_sha256="wrong"
        )
    assert not provider.ledger.exists()
    session.post.assert_not_called()
