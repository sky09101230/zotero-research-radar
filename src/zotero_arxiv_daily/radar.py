"""Local-first recommendation pipeline without delivery side effects."""

from __future__ import annotations

from pathlib import Path

from omegaconf import DictConfig

from .executor import Executor
from .protocol import Paper
from .state import StateStore


class RadarPipeline:
    """Reuse upstream retrieval and ranking while keeping delivery outside the pipeline."""

    def __init__(self, config: DictConfig, state_path: str | Path = ".radar/history.sqlite"):
        self.config = config
        self.executor = Executor(config)
        self.state = StateStore(state_path)

    def recommend(
        self,
        *,
        include_seen: bool = False,
        summarize: bool = False,
        max_papers: int | None = None,
    ) -> list[Paper]:
        corpus = self.executor.filter_corpus(self.executor.fetch_zotero_corpus())
        if not corpus:
            raise ValueError("No Zotero papers with abstracts matched the configured collections.")

        candidates: list[Paper] = []
        for retriever in self.executor.retrievers.values():
            candidates.extend(retriever.retrieve_papers())

        if not include_seen:
            candidates = [paper for paper in candidates if not self.state.has_recommendation(paper)]
        if not candidates:
            return []

        ranked = self.executor.reranker.rerank(candidates, corpus)
        limit = max_papers if max_papers is not None else self.config.executor.max_paper_num
        selected = ranked[:limit]
        if summarize:
            for paper in selected:
                paper.generate_tldr(self.executor.openai_client, self.config.llm)
                paper.generate_affiliations(self.executor.openai_client, self.config.llm)

        self.state.record_recommendations(selected)
        return selected
