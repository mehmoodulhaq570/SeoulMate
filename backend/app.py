from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from rapidfuzz import process, fuzz
from functools import lru_cache
from rank_bm25 import BM25Okapi

# ======================================================
# CONFIGURATION
# ======================================================
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
MODEL_DIR = r"D:\Projects\SeoulMate\model_traning\models"
INDEX_DIR = r"D:\Projects\SeoulMate\model_traning\faiss_index"

# ======================================================
# FASTAPI SETUP
# ======================================================
app = FastAPI(title="Kdrama Hybrid Recommendation API", version="3.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# STAGE 1 — LOAD MODELS & INDEXES
# ======================================================
print("Stage 1: Loading models and FAISS index...")

model = SentenceTransformer(MODEL_NAME, cache_folder=MODEL_DIR)
index = faiss.read_index(os.path.join(INDEX_DIR, "index.faiss"))

with open(os.path.join(INDEX_DIR, "meta.pkl"), "rb") as f:
    metadata = pickle.load(f)

titles = [m["Title"] for m in metadata]
corpus = [
    f"{m.get('Title', '')} {m.get('Genre', '')} {m.get('Description', '')} {m.get('Cast', '')}"
    for m in metadata
]
bm25 = BM25Okapi([doc.split() for doc in corpus])

print(f"Loaded {len(metadata)} dramas successfully.")

# ======================================================
# STAGE 2 — LOAD OPTIONAL RERANKER
# ======================================================
try:
    print("Stage 2: Loading cross-encoder reranker...")
    reranker = CrossEncoder(CROSS_ENCODER_MODEL)
    use_reranker = True
    print("Cross-encoder reranker loaded successfully.")
except Exception as e:
    reranker = None
    use_reranker = False
    print(f"Warning: Could not load reranker ({e}). Continuing without it.")


# ======================================================
# STAGE 3 — HELPER FUNCTIONS
# ======================================================
def fuzzy_match_title(user_input: str, threshold=70):
    """Handle typos and near matches using fuzzy logic."""
    match, score, _ = process.extractOne(user_input, titles, scorer=fuzz.WRatio)
    if score >= threshold:
        return match, score
    return None, score


@lru_cache(maxsize=128)
def cached_encode(text: str):
    """Cached embedding generation for speed."""
    emb = model.encode([text], convert_to_numpy=True)
    faiss.normalize_L2(emb)
    return emb


# ======================================================
# STAGE 4 — HYBRID RECOMMENDATION PIPELINE
# ======================================================
def recommend(title: str, top_n=5, alpha=0.7):
    """
    Stage-based pipeline:
    1. Resolve user input (fuzzy match or free-text)
    2. Semantic search (FAISS)
    3. Lexical search (BM25)
    4. Hybrid combination
    5. Optional reranking (Cross-Encoder)
    """

    # ---- Stage 4.1: Title resolution ----
    drama = next((m for m in metadata if m["Title"].lower() == title.lower()), None)

    if not drama:
        match, score = fuzzy_match_title(title)
        if match:
            drama = next((m for m in metadata if m["Title"] == match), None)
            print(
                f"Fuzzy match: '{title}' -> '{match}' (confidence: {score:.1f}%)".encode(
                    "utf-8", errors="replace"
                ).decode(
                    "utf-8"
                )
            )

            query_text = f"{drama['Title']} {drama.get('Genre', '')} {drama.get('Description', '')} {drama.get('Cast', '')}"
        else:
            print(f"No close match found for '{title}', treating as free-text query.")
            query_text = title
    else:
        query_text = f"{drama['Title']} {drama.get('Genre', '')} {drama.get('Description', '')} {drama.get('Cast', '')}"

    # ---- Stage 4.2: FAISS Semantic Search ----
    query_emb = cached_encode(query_text)
    D, I = index.search(query_emb, top_n + 10)
    faiss_results = [
        (metadata[idx], float(score))
        for idx, score in zip(I[0], D[0])
        if idx < len(metadata)
    ]

    # ---- Stage 4.3: BM25 Lexical Search ----
    bm25_scores = bm25.get_scores(query_text.split())
    top_bm25_idx = np.argsort(bm25_scores)[::-1][: top_n + 10]
    bm25_results = [(metadata[i], float(bm25_scores[i])) for i in top_bm25_idx]

    # ---- Stage 4.4: Combine Results ----
    combined_scores = {}
    max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
    for rec, score in faiss_results:
        combined_scores[rec["Title"]] = alpha * score
    for rec, score in bm25_results:
        combined_scores[rec["Title"]] = combined_scores.get(rec["Title"], 0) + (
            1 - alpha
        ) * (score / max_bm25)

    sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    top_results = [
        next(m for m in metadata if m["Title"] == t) for t, _ in sorted_results[:top_n]
    ]

    # ---- Stage 4.5: Optional Reranking ----
    if use_reranker and reranker:
        try:
            pairs = [[query_text, r["Description"]] for r in top_results]
            rerank_scores = reranker.predict(pairs)
            top_results = [
                r
                for _, r in sorted(
                    zip(rerank_scores, top_results), key=lambda x: x[0], reverse=True
                )
            ]
        except Exception as e:
            print(f"Reranking failed: {e}")

    return {"queryok ok": {"Title": title}, "recommendations": top_results[:top_n]}


# ======================================================
# STAGE 5 — API ROUTES
# ======================================================
@app.get("/")
def root():
    return {"message": "Hybrid Kdrama Recommendation API v3.1 is running"}


@app.get("/recommend")
def get_recommendations(
    title: str = Query(..., description="Kdrama title or user query"), top_n: int = 5
):
    """Main recommendation endpoint."""
    return recommend(title, top_n)


# ======================================================
# STAGE 6 — RUN LOCALLY
# ======================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
