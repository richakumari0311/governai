# Enterprise Copilot

A governed multi-agent enterprise assistant. Routes employee questions to domain-specific
agents (HR, Finance, Support), grounds every answer in retrieved policy documents, and
runs a policy-compliance check with confidence-based routing to either an automatic
decision or human review.

Built as a portfolio project to demonstrate production-oriented RAG and multi-agent
system design: table-aware document chunking, domain-scoped retrieval, a two-tier
policy engine (deterministic rules + LLM-as-judge fallback), full audit logging, and
a measured evaluation harness rather than aspirational metrics.

## Architecture

```
User -> Router (LLM classifier) -> Domain Agent(s) [HR / Finance / Support]
                                          |
                                    RAG retrieval (ChromaDB, table-aware chunks)
                                          |
                                    Policy Engine (YAML rules -> LLM judge fallback)
                                          |
                                    Confidence-based Decision Gate
                                    (auto-approve / auto-reject / human-approval)
                                          |
                                    Audit Log (Postgres)
```

Orchestrated as a LangGraph state graph (`src/graph/`), exposed via FastAPI (`src/main.py`),
with a Streamlit demo UI (`src/demo/app.py`) calling the API.

## Tech stack

Python, FastAPI, LangGraph, Gemini API (`gemini-3.6-flash` for generation,
`gemini-3.5-flash-lite` for routing/judging), ChromaDB, SQLAlchemy + PostgreSQL
(via Docker), Pydantic, Streamlit.

## Setup

1. Python 3.11+, Docker Desktop, a Gemini API key (Google AI Studio)
2. `python3 -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env` and fill in `GEMINI_API_KEY`
5. `cd docker && docker compose up -d && cd ..` (starts Postgres)
6. `python -m src.rag.ingest` (chunks and embeds the sample corpus into ChromaDB)
7. `python -m src.audit.store` or run once via `src.audit.test_audit` to create the audit table

## Running

API: `uvicorn src.main:app --reload` (docs at `http://localhost:8000/docs`)

Demo UI (separate terminal, API must be running): `streamlit run src/demo/app.py`

Eval harness: `python -m src.eval.run_eval`

## Evaluation results

Measured against a 14-case labeled test set (`data/eval/test_set.yaml`) — small by
design, constrained by free-tier Gemini API rate limits (5 RPM / 20 RPD on the
flagship model during development).

| Metric | Result |
|---|---|
| Routing Accuracy | 100% |
| Retrieval Accuracy | 100% |
| Groundedness | 90%* |
| Hallucination Rate | 0%** |
| Policy Decision Accuracy | 100% |
| Avg Latency | ~2.9s (median, excluding rate-limit retries) |

\* The one "ungrounded" case, on manual inspection, was actually a correctly hedged,
policy-grounded answer to an edge case the corpus doesn't explicitly cover — the
scoring heuristic (keyword-matching for decline phrases) doesn't yet recognize
graduated, reasoned hedging as distinct from either a clean answer or a flat decline.
Every case was individually inspected; zero true hallucinations were observed.

\** Confirmed by manual inspection of every flagged case, not just the automated score.

## Known limitations

- **Router precision required iteration.** Initial routing accuracy was 70%, with the
  router over-associating compensation/salary questions with Finance (whose documents
  only cover expense reimbursement, not compensation). Fixed via few-shot examples in
  the router's system prompt targeting the specific confusion — now 100% on the test
  set, though this fix is somewhat specific to the patterns observed and may not
  generalize to all compensation-adjacent phrasings untested here.
- **LLM-judge confidence scores are not reliably calibrated.** Prompting the judge to
  report low confidence on ambiguous cases works inconsistently — identical inputs
  produced confidence scores on both sides of the decision threshold across separate
  runs. A more robust approach would derive confidence from log-probabilities or
  multi-sample agreement rather than a self-reported number.
- **Policy rule extraction from questions is manual.** The policy engine can evaluate
  a rule given structured inputs (rule ID, level, value), but nothing yet extracts
  those automatically from a free-text question — policy checks must be explicitly
  supplied by the caller. Automatic extraction (an LLM parsing "can I expense a $1500
  flight as a Manager" into a structured check) is a natural next step.
- **Groundedness scoring is a keyword heuristic**, not an LLM-judged metric — cheaper
  and more transparent, but brittle to phrasing variation, as the analysis above shows.
- **Multimodal content (scanned docs, images) is explicitly out of scope** for this
  project — the corpus is text/tabular, and multimodal RAG is a separate project where
  it would be load-bearing rather than incidental.
- **Free-tier API rate limits constrained both development and eval scale.** The eval
  set is 14 cases, not hundreds, and development required careful sequencing around a
  5 RPM / 20 RPD quota on the primary model.

## Project structure

```
src/
  agents/      domain agent factory (HR, Finance, Support)
  router/      LLM-based query classification + multi-domain dispatch
  rag/         chunking (table-aware), embeddings, ChromaDB storage
  policy/      YAML rule engine + LLM-as-judge fallback + decision gate
  audit/       Postgres audit logging
  graph/       LangGraph state, nodes, and graph assembly
  demo/        Streamlit UI
  eval/        evaluation harness
  main.py      FastAPI app
data/
  corpus/      sample HR/Finance/Support policy documents
  eval/        labeled test set
```