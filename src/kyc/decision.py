from __future__ import annotations

from pathlib import Path

import yaml

from kyc.domain import Decision, ReasonCode, SignalBundle, Verdict


class DecisionEngine:
    def __init__(self, rules_path: Path) -> None:
        self.rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))

    def decide(self, signals: SignalBundle) -> Decision:
        policy = self.rules["policy"]
        reasons = list(dict.fromkeys(signals.hard_failures + signals.quality_failures))
        contributions: dict[str, str] = {}
        if signals.hard_failures or signals.duplicate_identifier:
            if signals.duplicate_identifier:
                reasons.append(ReasonCode.DUPLICATE_IDENTIFIER)
            return Decision(verdict=Verdict.REJECT, reasons=reasons, rule_set_version=self.rules["version"], contributions={"validation": "hard failure"})
        if signals.ocr_confidence is None or signals.ocr_confidence < policy["min_ocr_confidence"]:
            reasons.append(ReasonCode.LOW_OCR_CONFIDENCE)
            contributions["ocr"] = "critical field uncertain"
        if signals.liveness == "SPOOF":
            reasons.append(ReasonCode.LIVENESS_SPOOF)
            return Decision(verdict=Verdict.REJECT, reasons=reasons, rule_set_version=self.rules["version"], contributions={"liveness": "spoof"})
        if signals.liveness not in {"LIVE"}:
            reasons.append(ReasonCode.LIVENESS_UNAVAILABLE)
            contributions["liveness"] = "not a pass"
        if signals.face_similarity is None or signals.face_similarity < policy["review_min"]:
            reasons.append(ReasonCode.FACE_MATCH_FAILED)
            return Decision(verdict=Verdict.REJECT, reasons=reasons, rule_set_version=self.rules["version"], contributions={**contributions, "face": "below review threshold"})
        if signals.face_similarity < policy["approve_min"]:
            reasons.append(ReasonCode.FACE_MATCH_REVIEW)
            contributions["face"] = "review band"
        verdict = Verdict.APPROVE if not reasons else Verdict.REVIEW
        return Decision(verdict=verdict, reasons=list(dict.fromkeys(reasons)), rule_set_version=self.rules["version"], contributions=contributions)
