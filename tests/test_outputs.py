import json

from zotero_arxiv_daily.outputs import report_document, write_report
from zotero_arxiv_daily.protocol import Paper


def test_json_report_is_machine_readable(tmp_path):
    paper = Paper("arxiv", "Example", ["Author"], "Abstract", "https://example.test")
    paper.score = 0.8
    output = tmp_path / "report.json"

    write_report(report_document([paper], {"mode": "recommend", "sources": ["arxiv"]}), output, "json")

    document = json.loads(output.read_text(encoding="utf-8"))
    assert document["papers"][0]["title"] == "Example"
    assert document["papers"][0]["id"] == "arxiv:https://example.test"
