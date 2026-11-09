"""Check the published assessment's values against the native scanner."""
import hashlib
import json
import re
from pathlib import Path

from proficiency_comment import cell, is_context


root = Path("evidence")
comment = (root / "assessment-comment.md").read_bytes()
body = comment.decode("utf-8")
report = json.loads((root / "proficiency-report.json").read_bytes())
changes = json.loads((root / "pr-changes.json").read_bytes())
scores = report["level_scores"]
level = report["overall_level"]
score = f"{report['overall_score']:.1f}"
files = sum(value["file_count"] for value in scores.values())
assert body.startswith("## AI Proficiency Assessment")
level_name = re.escape(scores[str(level)]["name"])
assert re.search(rf"Overall Level[^|]*\|\s*(?:Level {level}:\s*)?{level_name}\s*\|", body)
assert re.search(rf"Overall Score[^|]*\|\s*{re.escape(score)}\s*/\s*100\s*\|", body)
assert re.search(rf"Files Detected[^|]*\|\s*{files}\s+(?:context )?files\s*\|", body)
assert "### Level Breakdown" in body and "### Top Recommendations" in body
for key, value in scores.items():
    assert re.search(rf"\|\s*Level {key}:[^|]+\|\s*{value['file_count']}\s*\|", body)
context = [change["filename"] for change in changes if is_context(change["filename"])]
impact = body.split("### This PR's Impact", 1)[1].split("### Top Recommendations", 1)[0]
assert all(cell(name) in impact for name in context)
recommendations = [line for line in report["recommendations"] if not line.startswith("🔍 Detected AI tools:")][:3]
recommendation_section = body.split("### Top Recommendations", 1)[1]
offsets = [recommendation_section.index(cell(line)) for line in recommendations]
assert offsets == sorted(offsets)
assert not re.search(r"(?<![\w])@[A-Za-z0-9]", body), "Unexpected mention in assessment"
assert len(comment) <= 20000
summary = {"level": level, "score": score, "files": files, "context": context, "recommendations": recommendations}
(root / "normalized.json").write_text(json.dumps(summary, ensure_ascii=False) + "\n", encoding="utf-8")
(root / "validated.sha256").write_text(hashlib.sha256(comment).hexdigest() + "\n")
