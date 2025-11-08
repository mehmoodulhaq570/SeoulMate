"""
SeoulMate - K-Drama Recommendation System
Streamlit Frontend

Run with: streamlit run frontend/streamlit_app.py
"""

import streamlit as st
import requests
import pandas as pd
from typing import List, Dict

# ======================================================
# CONFIG
# ======================================================
API_URL = "http://127.0.0.1:8001"

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="SeoulMate - K-Drama Recommendations",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================================================
# CUSTOM CSS
# ======================================================
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #4ECDC4;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .drama-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .drama-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .drama-info {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .score-badge {
        background: #FFD93D;
        color: #1A1A2E;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 0.5rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ======================================================
# HELPER FUNCTIONS
# ======================================================
def check_api_health() -> bool:
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_recommendations(query: str, top_n: int = 5) -> Dict:
    """Get recommendations from backend API"""
    try:
        response = requests.get(
            f"{API_URL}/recommend", params={"title": query, "top_n": top_n}, timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def format_drama_card(drama: Dict, rank: int) -> str:
    """Format drama data into HTML card"""
    title = drama.get("Title", "Unknown")
    genre = drama.get("Genre", "N/A")
    description = drama.get("Description", "No description available")[:200] + "..."
    cast = drama.get("Cast", "N/A")

    return f"""
    <div class="drama-card">
        <div class="drama-title">#{rank} {title}</div>
        <div class="drama-info">
            <strong>Genre:</strong> {genre}<br>
            <strong>Cast:</strong> {cast}<br><br>
            {description}
        </div>
    </div>
    """


# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.image(
        "https://via.placeholder.com/300x150/667eea/ffffff?text=SeoulMate",
        use_container_width=True,
    )
    st.markdown("### 🎬 About")
    st.markdown(
        """
    **SeoulMate** is an AI-powered K-drama recommendation system using:
    
    - 🧠 Fine-tuned SBERT embeddings
    - 🔍 Hybrid retrieval (FAISS + BM25Plus)
    - 🎯 Cross-encoder reranking
    - 📊 1,922 K-dramas in database
    """
    )

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    top_n = st.slider("Number of recommendations", 3, 10, 5)

    st.markdown("#### Filters")
    genre = st.text_input("Genre", "")
    director = st.text_input("Director", "")
    publisher = st.text_input("Publisher", "")
    rating_value = st.text_input("Rating Value (min)", "")
    rating_count = st.text_input("Rating Count (min)", "")
    keywords = st.text_input("Keywords", "")
    screenwriters = st.text_input("Screenwriters", "")
    similar_to = st.text_input("Similar To (title)", "")

    sort_by = st.selectbox(
        "Sort By",
        [
            "",
            "rating_value",
            "popularity",
            "date_published",
            "episodes",
            "duration",
            "ranked",
            "watchers",
        ],
    )
    sort_order = st.selectbox("Sort Order", ["desc", "asc"])

    st.markdown("---")
    st.markdown("### 📊 System Status")
    if check_api_health():
        st.success("✅ API Online")
    else:
        st.error("❌ API Offline")
        st.info("Start backend: `python backend/app.py`")

# ======================================================
# MAIN CONTENT
# ======================================================
st.markdown('<div class="main-header">🎬 SeoulMate</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Discover Your Next Favorite K-Drama</div>',
    unsafe_allow_html=True,
)

# Search tabs
tab1, tab2, tab3 = st.tabs(["🔍 Search by Title", "🎲 Random Picks", "📊 Stats"])

with tab1:
    st.markdown("### Find Similar Dramas")

    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "Enter a K-drama title or describe what you want to watch:",
            placeholder="e.g., Crash Landing on You, romantic comedy, historical drama...",
            label_visibility="collapsed",
        )
    with col2:
        search_button = st.button("🔍 Search", use_container_width=True)

    # Example queries
    st.markdown("**Try these:**")
    example_col1, example_col2, example_col3 = st.columns(3)
    with example_col1:
        if st.button("Crash Landing on You"):
            query = "Crash Landing on You"
            search_button = True
    with example_col2:
        if st.button("Itaewon Class"):
            query = "Itaewon Class"
            search_button = True
    with example_col3:
        if st.button("Romantic Comedy"):
            query = "romantic comedy"
            search_button = True

    # Search results
    if query and search_button:
        # Collect all filter params from sidebar
        filter_params = {
            "genre": genre,
            "director": director,
            "publisher": publisher,
            "rating_value": rating_value,
            "rating_count": rating_count,
            "keywords": keywords,
            "screenwriters": screenwriters,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "similar_to": similar_to,
        }
        # Remove empty values
        filter_params = {k: v for k, v in filter_params.items() if v not in [None, ""]}
        params = {"title": query, "top_n": top_n}
        params.update(filter_params)
        with st.spinner("🔮 Finding perfect matches..."):
            try:
                response = requests.get(
                    f"{API_URL}/recommend", params=params, timeout=10
                )
                if response.status_code == 200:
                    results = response.json()
                else:
                    results = {"error": f"API error: {response.status_code}"}
            except Exception as e:
                results = {"error": str(e)}

            if "error" in results:
                st.error(f"❌ Error: {results['error']}")
                st.info("Make sure the backend is running: `python backend/app.py`")
            else:
                recommendations = results.get("recommendations", [])

                if recommendations:
                    st.success(f"✨ Found {len(recommendations)} recommendations!")

                    # Display results
                    for idx, drama in enumerate(recommendations, 1):
                        st.markdown(
                            format_drama_card(drama, idx), unsafe_allow_html=True
                        )
                else:
                    st.warning("No recommendations found. Try a different query!")

with tab2:
    st.markdown("### 🎲 Feeling Lucky?")
    st.info("Coming soon: Random drama picker based on mood, genre, or year!")

    if st.button("🎲 Pick Random Drama"):
        st.balloons()
        st.success("Feature coming soon!")

with tab3:
    st.markdown("### 📊 System Statistics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Dramas", "1,922")
    with col2:
        st.metric("Model Version", "v3.1")
    with col3:
        st.metric("Fine-tuned", "Yes ✅")

    st.markdown("---")
    st.markdown("**Model Stack:**")
    st.markdown(
        """
    - **SBERT:** sbert-finetuned-full (3 epochs, 1922 dramas)
    - **Retrieval:** FAISS IndexFlatIP + BM25Plus
    - **Reranker:** Cross-encoder (3 epochs, 25k pairs)
    - **Backend:** FastAPI v3.1
    """
    )

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #888; padding: 2rem;">Made with ❤️ by SeoulMate Team | Powered by AI</div>',
    unsafe_allow_html=True,
)
