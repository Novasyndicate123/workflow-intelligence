from __future__ import annotations
from html import escape


from .funnel_store import FunnelStore
from .funnel_analytics import FunnelAnalytics


def build_report(path="results/commercial_funnel.jsonl") -> dict:
    events = FunnelStore(path).events()
    return FunnelAnalytics().analyze(events)


def render_dashboard(report: dict, review_batch=None) -> str:
    counts = report.get("counts", {})
    rates = report.get("transition_rates", {})
    segments = report.get("segments", {})
    bottleneck = report.get("bottleneck") or "No measured bottleneck"
    cards = "".join(
        f"<section><strong>{escape(str(stage))}</strong><div>{counts.get(stage, 0)}</div></section>"
        for stage in ("discovered", "qualified", "assessed", "engaged", "replied", "pilot_candidate", "converted")
    )
    transitions = "".join(
        f"<li>{escape(key)}: {value * 100:.1f}%</li>"
        for key, value in rates.items()
        if value is not None
    ) or "<li>No measured transitions yet.</li>"
    segment_rows = "".join(
        f"<tr><th>{escape(str(region))}</th>"
        f"<td>{escape(str(data.get('discovered', 0)))}</td>"
        f"<td>{escape(str(data.get('qualified', 0)))}</td>"
        f"<td>{escape(str(data.get('assessed', 0)))}</td></tr>"
        for region, data in sorted(segments.items())
    ) or "<tr><td colspan='4'>No segmented data yet.</td></tr>"
    review_rows = "".join(
        "<tr>"
        f"<td>{escape(str(item.get('business_name', '')))}</td>"
        f"<td>{escape(str(item.get('location', '')))}</td>"
        f"<td>{float(item.get('qualification_score', 0)) * 100:.1f}%</td>"
        f"<td>{escape(str(item.get('review_status', '')))}</td>"
        f"<td>{escape(str(item.get('source', '')))}</td>"
        "</tr>"
        for item in (review_batch or [])
    )
    review_section = ""
    if review_batch is not None:
        review_section = (
            "<h2>Human Review Queue</h2>"
            "<p>Public-source prospects awaiting human review. No external action is enabled.</p>"
            "<table><thead><tr>"
            "<th>Business</th><th>Location</th><th>Qualification</th>"
            "<th>Status</th><th>Source</th>"
            f"</tr></thead><tbody>{review_rows}</tbody></table>"
        )
    return (
        "<main><h1>Workflow Intelligence — Acquisition Intelligence</h1>"
        f"<p>Measured bottleneck: <strong>{escape(str(bottleneck))}</strong></p>"
        f"<div class='cards'>{cards}</div><h2>Transitions</h2><ul>{transitions}</ul>"
        "<h2>Regional segments</h2><table><thead><tr>"
        "<th>Region</th><th>Discovered</th><th>Qualified</th><th>Assessed</th>"
        f"</tr></thead><tbody>{segment_rows}</tbody></table>"
        f"{review_section}</main>"
    )
