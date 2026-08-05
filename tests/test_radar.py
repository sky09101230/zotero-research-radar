from datetime import datetime

from omegaconf import OmegaConf

from zotero_arxiv_daily.protocol import CorpusPaper, Paper
from zotero_arxiv_daily.radar import RadarPipeline
from zotero_arxiv_daily.state import StateStore


def test_pipeline_ranks_and_deduplicates(tmp_path, monkeypatch):
    first = Paper("arxiv", "First", ["A"], "first abstract", "https://example.test/1")
    second = Paper("arxiv", "Second", ["B"], "second abstract", "https://example.test/2")

    class Retriever:
        def retrieve_papers(self):
            return [first, second]

    class Reranker:
        def rerank(self, candidates, corpus):
            first.score = 0.9
            second.score = 0.8
            return [first, second]

    class FakeExecutor:
        retrievers = {"arxiv": Retriever()}
        reranker = Reranker()
        openai_client = object()

        def __init__(self, config):
            self.config = config

        def fetch_zotero_corpus(self):
            return [CorpusPaper("Corpus", "abstract", datetime(2026, 1, 1), [])]

        def filter_corpus(self, corpus):
            return corpus

    monkeypatch.setattr("zotero_arxiv_daily.radar.Executor", FakeExecutor)
    config = OmegaConf.create({"executor": {"max_paper_num": 10}, "llm": {}})
    state_path = tmp_path / "history.sqlite"
    pipeline = RadarPipeline(config, state_path)

    assert [paper.title for paper in pipeline.recommend()] == ["First", "Second"]
    assert pipeline.recommend() == []
    assert StateStore(state_path).has_recommendation(first)
