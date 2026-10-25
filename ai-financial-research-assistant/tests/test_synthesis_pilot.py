"""No-cost provider boundary checks. Synthetic responses are not model quality evidence."""

import io
import json
import zipfile
from decimal import Decimal
from unittest.mock import Mock

import pytest
import requests

from finsight.research.narrative import ModelConfig, OpenAIProvider, estimate, request_payload
from finsight.research.report import report_bundle


def setup_provider(tmp_path, monkeypatch, output, status="completed"):
    monkeypatch.setenv("FINSIGHT_ENABLE_MODEL", "1")
    monkeypatch.setenv("FINSIGHT_OPENAI_API_KEY", "fictional-proxy-placeholder")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config = ModelConfig("candidate-model", Decimal("1"), Decimal("2"), Decimal("1"))
    evidence = {
        "citations": {
            "E1:B1": {
                "eligible_for_prose": True,
                "support_text": "Company reports operating costs increased during the quarter.",
            }
        }
    }
    session = Mock()
    session.post.return_value.status_code = 200
    session.post.return_value.json.return_value = {
        "id": "synthetic-response",
        "status": status,
        "usage": {"input_tokens": 150, "output_tokens": 80},
        "output": [{"content": [{"type": "output_text", "text": json.dumps(output)}]}],
    }
    return OpenAIProvider(config, tmp_path / "usage.jsonl", session), evidence, session


GOOD = {
    "paragraphs": [
        {
            "kind": "interpretation",
            "text": "The cost trend warrants investigation.",
            "citation_ids": ["E1:B1"],
            "support": [
                {
                    "citation_id": "E1:B1",
                    "quote": "Company reports operating costs increased during the quarter.",
                }
            ],
        }
    ]
}


def test_single_request_transport_and_audit_with_proxy_secret(tmp_path, monkeypatch):
    provider, evidence, session = setup_provider(tmp_path, monkeypatch, GOOD)
    result = provider.generate(evidence, approved=True)
    assert result["usage"]["origin"] == "application model provider"
    assert result["usage"]["latency_seconds"] >= 0
    assert result["usage"]["provider_usage"]["input_tokens"] == 150
    payload = session.post.call_args.kwargs
    assert payload["json"] == request_payload(provider.config, evidence)
    assert payload["json"]["text"]["format"]["type"] == "json_object"
    assert not payload["json"]["store"] and not payload["allow_redirects"]
    assert "fictional-proxy-placeholder" in payload["headers"]["Authorization"]
    with pytest.raises(ValueError, match="Single-request"):
        provider.generate(evidence, approved=True)
    assert session.post.call_count == 1
    assert "fictional-proxy-placeholder" not in provider.ledger.read_text()


@pytest.mark.parametrize("failure", ["timeout", "incomplete", "invalid_binding"])
def test_failure_is_audited_and_never_retried(tmp_path, monkeypatch, failure):
    output = (
        {"quantitative_claims": [{"evidence_id": "unsupported-table"}]}
        if failure == "invalid_binding"
        else GOOD
    )
    provider, evidence, session = setup_provider(
        tmp_path,
        monkeypatch,
        output,
        status="incomplete" if failure == "incomplete" else "completed",
    )
    if failure == "timeout":
        session.post.side_effect = requests.Timeout("synthetic timeout")
    with pytest.raises(ValueError):
        provider.generate(evidence, approved=True)
    rows = [json.loads(line) for line in provider.ledger.read_text().splitlines()]
    assert [r["status"] for r in rows] == ["reserved", "failure"]
    assert rows[1]["latency_seconds"] >= 0 and rows[1]["failure"]
    if failure != "timeout":
        assert rows[1]["provider_usage"] and rows[1]["provider_output_text"]
    with pytest.raises(ValueError, match="Single-request"):
        provider.generate(evidence, approved=True)
    assert session.post.call_count == 1


def test_exact_serialized_input_is_estimated_and_bundle_preserves_provider_identity(dataset):
    from test_research import report_fixture

    config = ModelConfig("candidate-model", Decimal("1"), Decimal("2"), Decimal("1"))
    evidence = {"text": "Türkiye — компания"}
    payload = request_payload(config, evidence)
    allowance = len((payload["instructions"] + payload["input"]).encode()) + 512
    assert estimate(config, evidence)["input_token_allowance"] == allowance
    output = {"origin": "application model provider", "narrative": GOOD}
    with zipfile.ZipFile(io.BytesIO(report_bundle(report_fixture(dataset), narrative=output))) as z:
        assert json.loads(z.read("application-model-output.json")) == output
        assert "model-evidence.json" in z.namelist()


def test_ui_requires_approval_and_exposes_generated_analysis_and_download(
    dataset, monkeypatch, tmp_path
):
    from pathlib import Path

    from streamlit.testing.v1 import AppTest
    from test_research import report_fixture

    research = report_fixture(dataset)
    monkeypatch.setattr("finsight.research.ui.find_companies", lambda *a: [research.company])
    monkeypatch.setattr("finsight.research.ui.run_research", lambda *a, **k: research)
    for key, value in {
        "SEC_USER_AGENT": "FinSight tests contact@example.org",
        "FINSIGHT_ENABLE_MODEL": "1",
        "FINSIGHT_OPENAI_API_KEY": "fictional-test-key",
        "FINSIGHT_MODEL": "synthetic-test-model",
        "FINSIGHT_MODEL_CAP_USD": "1",
        "FINSIGHT_INPUT_USD_PER_MILLION": "1",
        "FINSIGHT_OUTPUT_USD_PER_MILLION": "2",
        "FINSIGHT_CACHE_DIR": str(tmp_path),
    }.items():
        monkeypatch.setenv(key, value)
    calls = []

    def respond(_session, url, **kwargs):
        calls.append(url)
        evidence = json.loads(kwargs["json"]["input"])
        key, source = next(
            (k, s)
            for k, s in evidence["citations"].items()
            if s.get("kind") == "disclosure excerpt" and s.get("eligible_for_prose")
        )
        output = {
            "paragraphs": [
                {
                    "kind": "interpretation",
                    "text": "Source context warrants analyst review.",
                    "citation_ids": [key],
                    "support": [{"citation_id": key, "quote": source["support_text"]}],
                }
            ]
        }
        response = Mock(status_code=200)
        response.json.return_value = {
            "status": "completed",
            "usage": {"input_tokens": 20, "output_tokens": 30},
            "output": [{"content": [{"type": "output_text", "text": json.dumps(output)}]}],
        }
        return response

    monkeypatch.setattr(requests.Session, "post", respond)
    app = AppTest.from_file(
        str(Path(__file__).parents[1] / "app/main.py"), default_timeout=20
    ).run()
    app.text_input[0].set_value("Fixture")
    app.button[0].click().run()
    next(b for b in app.button if b.label == "Research selected company").click().run()
    assert not app.exception and not calls
    assert any("Table analytical evidence" in m.value for m in app.markdown)
    assert next(b for b in app.button if b.label == "Generate optional narrative").disabled
    next(
        c for c in app.checkbox if c.label.startswith("I approve this model request")
    ).check().run()
    next(b for b in app.button if b.label == "Generate optional narrative").click().run()
    assert not app.exception and len(calls) == 1
    assert any("Application-generated analysis" in h.value for h in app.subheader)
    assert any(
        b.label == "Download evidence and generated analysis" for b in app.get("download_button")
    )
