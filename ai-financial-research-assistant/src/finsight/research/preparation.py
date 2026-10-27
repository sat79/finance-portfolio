"""One offline preparation path for UI review, exports, pilot and eventual execution."""

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass

from finsight.research.model_evidence import compact_synthesis_evidence
from finsight.research.narrative import ModelConfig, estimate, request_payload


def prepare_evidence(evidence):
    # Small provider-contract fixtures already contain only their supplied claim register.
    return (
        compact_synthesis_evidence(evidence) if "key_findings" in evidence else deepcopy(evidence)
    )


@dataclass(frozen=True)
class PreparedRequest:
    evidence: dict
    payload: dict
    estimate: dict
    encoded: bytes
    request_sha256: str


def prepare_request(evidence, config: ModelConfig):
    selected = prepare_evidence(evidence)
    payload = request_payload(config, selected)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode()
    return PreparedRequest(
        selected, payload, estimate(config, selected), encoded, hashlib.sha256(encoded).hexdigest()
    )
