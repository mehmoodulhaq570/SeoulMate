"""
SeoulMate - K-Drama Recommendation System
Streamlit Frontend

Run with: streamlit run frontend/streamlit_app.py
"""

import streamlit as st
import requests
import pandas as pd
from typing import List, Dict
import uuid
import time

# ======================================================
# CONFIG
# ======================================================
API_URL = "http://127.0.0.1:8001"

# ======================================================
# SESSION STATE INITIALIZATION
# ======================================================
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{time.time()}"
if "last_search_id" not in st.session_state:
    st.session_state.last_search_id = None
if "watchlist" not in st.session_state:
    st.session_state.watchlist = set()
if "last_results" not in st.session_state:
    st.session_state.last_results = None
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "last_filter_params" not in st.session_state:
    st.session_state.last_filter_params = {}
if "viewed_dramas" not in st.session_state:
    st.session_state.viewed_dramas = []

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
    /* Main Header Styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        text-align: center;
        color: #6c757d;
        font-size: 1.3rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* Drama Card Styling */
    .drama-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .drama-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    .drama-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .rank-badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 50%;
        font-size: 1rem;
        font-weight: bold;
        backdrop-filter: blur(10px);
    }
    
    .drama-info {
        font-size: 1rem;
        line-height: 1.8;
        opacity: 0.95;
    }
    
    .drama-info strong {
        color: #FFD93D;
        font-weight: 600;
    }
    
    .score-badge {
        background: #FFD93D;
        color: #1A1A2E;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-block;
        margin-top: 1rem;
        font-size: 0.95rem;
        box-shadow: 0 4px 10px rgba(255, 217, 61, 0.3);
    }
    
    /* Filter Section Styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    
    /* Button Styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 2rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
    }
    
    /* Search Box Enhancement */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
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
    except Exception:
        return False


def log_interaction(drama_title: str, interaction_type: str, position: int = None):
    """Log user interaction (click, watchlist_add, watchlist_remove) to backend"""
    try:
        payload = {
            "user_id": st.session_state.user_id,
            "session_id": st.session_state.session_id,
            "search_id": st.session_state.last_search_id,
            "drama_title": drama_title,
            "interaction_type": interaction_type,
            "position": position,
        }
        requests.post(f"{API_URL}/analytics/interaction", json=payload, timeout=2)
    except Exception:
        pass  # Silently fail - don't disrupt user experience


def get_recommendations(query: str, top_n: int = 5, **filters) -> Dict:
    """Get recommendations from backend API with analytics tracking"""
    try:
        params = {
            "title": query,
            "top_n": top_n,
            "user_id": st.session_state.user_id,
            "session_id": st.session_state.session_id,
        }
        params.update(filters)

        response = requests.get(f"{API_URL}/recommend", params=params, timeout=10)
        if response.status_code == 200:
            result = response.json()
            # Store search_id for interaction tracking
            if "search_id" in result:
                st.session_state.last_search_id = result["search_id"]
            return result
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def format_drama_card(drama: Dict, rank: int) -> str:
    """Format drama data into interactive HTML card with click tracking"""
    title = drama.get("Title", "Unknown")
    genre = drama.get("Genre", drama.get("genres", "N/A"))
    description = drama.get(
        "Description", drama.get("description", "No description available")
    )

    # Truncate description
    if len(description) > 250:
        description = description[:250] + "..."

    cast = drama.get("Cast", drama.get("actors", "N/A"))
    rating = drama.get("rating_value", drama.get("score", "N/A"))
    episodes = drama.get("episodes", drama.get("Episodes", "N/A"))

    # Format cast
    if isinstance(cast, str) and len(cast) > 100:
        cast = cast[:100] + "..."

    card_html = f"""
    <div class="drama-card" id="drama-card-{rank}">
        <div class="drama-title">
            <span class="rank-badge">#{rank}</span>
            <span>{title}</span>
        </div>
        <div class="drama-info">
            <strong>🎭 Genre:</strong> {genre}<br>
            <strong>⭐ Rating:</strong> {rating} | <strong>📺 Episodes:</strong> {episodes}<br>
            <strong>🎬 Cast:</strong> {cast}<br><br>
            <strong>📖 Synopsis:</strong><br>
            {description}
        </div>
        <span class="score-badge">⭐ {rating}</span>
    </div>
    """

    return card_html, title, rank


# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.markdown("### 🎬 SeoulMate")
    st.markdown("*Your AI-Powered K-Drama Companion*")

    st.markdown("---")

    st.markdown("#### 🔍 About")
    st.markdown(
        """
    **SeoulMate** uses advanced AI to find your perfect K-drama match:
    
    - 🧠 **Fine-tuned SBERT** - Smart semantic understanding
    - 🔍 **Hybrid Search** - FAISS + BM25Plus for best results
    - 🎯 **Cross-Encoder** - Precision reranking
    - 📊 **1,922 Dramas** - Comprehensive database
    """
    )

    st.markdown("---")
    st.markdown("### ⚙️ Search Settings")
    top_n = st.slider(
        "📊 Number of Recommendations", 3, 15, 5, help="How many dramas to recommend"
    )

    st.markdown("---")
    st.markdown("### 🎯 Advanced Filters")

    with st.expander("🎭 Genre & People", expanded=False):
        genre = st.text_input(
            "🎭 Genre", "", placeholder="e.g., Romance, Action, Thriller"
        )
        director = st.text_input("🎬 Director", "", placeholder="e.g., Kim Eun-sook")
        screenwriters = st.text_input(
            "✍️ Screenwriter", "", placeholder="e.g., Park Ji-eun"
        )

    with st.expander("🏢 Production & Publisher", expanded=False):
        publisher = st.text_input(
            "📺 Publisher/Network", "", placeholder="e.g., tvN, Netflix"
        )
        keywords = st.text_input("🏷️ Keywords", "", placeholder="e.g., time travel, CEO")

    with st.expander("⭐ Ratings & Quality", expanded=False):
        rating_value = st.text_input("⭐ Min Rating", "", placeholder="e.g., 8.0")
        rating_count = st.text_input(
            "👥 Min Rating Count", "", placeholder="e.g., 1000"
        )

    with st.expander("🔄 Similar Drama Finder", expanded=False):
        similar_to = st.text_input(
            "🎯 Find Similar To", "", placeholder="Enter a drama title"
        )

    st.markdown("---")
    st.markdown("### 🔢 Sort Results")
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
        format_func=lambda x: {
            "": "Relevance (Default)",
            "rating_value": "⭐ Rating",
            "popularity": "🔥 Popularity",
            "date_published": "📅 Release Date",
            "episodes": "📺 Episode Count",
            "duration": "⏱️ Duration",
            "ranked": "🏆 Rank",
            "watchers": "👁️ Viewers",
        }.get(x, x),
    )
    sort_order = st.selectbox(
        "Sort Order",
        ["desc", "asc"],
        format_func=lambda x: "↓ Descending" if x == "desc" else "↑ Ascending",
    )

    st.markdown("---")
    st.markdown("### 📊 System Status")
    if check_api_health():
        st.success("✅ API Online")
    else:
        st.error("❌ API Offline")
        st.info("💡 Start backend: `python backend/app.py`")

# ======================================================
# MAIN CONTENT
# ======================================================
st.markdown('<div class="main-header">🎬 SeoulMate</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">✨ Discover Your Next Favorite K-Drama with AI-Powered Recommendations</div>',
    unsafe_allow_html=True,
)

# Search tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🔍 Smart Search", "👤 My Profile", "📊 Statistics", "📈 Analytics", "ℹ️ How It Works"]
)

with tab1:
    st.markdown("### 🎯 Find Your Perfect Drama")
    st.markdown(
        "Enter a drama title, describe what you're looking for, or use our advanced filters!"
    )

    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            "Search for K-Dramas:",
            placeholder="Try: 'Crash Landing on You', 'romantic comedy', 'time travel thriller'...",
            label_visibility="collapsed",
            key="search_input",
        )
    with col2:
        search_button = st.button("🔍 Search", use_container_width=True, type="primary")

    # Example queries with better styling
    st.markdown("##### 💡 Quick Searches")
    example_col1, example_col2, example_col3, example_col4 = st.columns(4)

    # Initialize session state for quick searches
    if "quick_search_query" not in st.session_state:
        st.session_state.quick_search_query = None
    if "quick_search_genre" not in st.session_state:
        st.session_state.quick_search_genre = None

    with example_col1:
        if st.button("💕 Crash Landing on You", use_container_width=True):
            st.session_state.quick_search_query = "Crash Landing on You"
            st.session_state.quick_search_genre = None
    with example_col2:
        if st.button("🍜 Itaewon Class", use_container_width=True):
            st.session_state.quick_search_query = "Itaewon Class"
            st.session_state.quick_search_genre = None
    with example_col3:
        if st.button("😂 Romantic Comedy", use_container_width=True):
            st.session_state.quick_search_query = "romantic comedy"
            st.session_state.quick_search_genre = "Romance"
    with example_col4:
        if st.button("🕰️ Historical Drama", use_container_width=True):
            st.session_state.quick_search_query = "historical"
            st.session_state.quick_search_genre = "Historical"

    # Use quick search values if available
    if st.session_state.quick_search_query:
        query = st.session_state.quick_search_query
        if (
            st.session_state.quick_search_genre and not genre
        ):  # Only override if sidebar is empty
            genre = st.session_state.quick_search_genre
        search_button = True
        # Clear after use
        st.session_state.quick_search_query = None
        st.session_state.quick_search_genre = None

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

        with st.spinner(
            "🔮 AI is analyzing thousands of dramas to find your perfect matches..."
        ):
            results = get_recommendations(query, top_n, **filter_params)

            # Store results in session state
            st.session_state.last_results = results
            st.session_state.last_query = query
            st.session_state.last_filter_params = filter_params

    # Display results from session state (persists across reruns)
    if st.session_state.last_results is not None:
        results = st.session_state.last_results
        filter_params = st.session_state.last_filter_params

        if "error" in results:
            st.error(f"❌ **Error:** {results['error']}")
            st.info(
                "💡 **Tip:** Make sure the backend is running with `python backend/app.py`"
            )
        else:
            recommendations = results.get("recommendations", [])

            if recommendations:
                st.success(
                    f"✨ **Found {len(recommendations)} amazing recommendations for you!**"
                )

                # Show query analysis insights
                if "analysis" in results:
                    analysis = results["analysis"]
                    intent = analysis.get("intent", "unknown")
                    alpha = analysis.get("dynamic_alpha", 0.7)

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.info(
                            f"🧠 **Query Intent:** {intent.replace('_', ' ').title()}"
                        )
                    with col_b:
                        st.info(
                            f"⚖️ **Search Weight:** {int(alpha*100)}% Semantic / {int((1-alpha)*100)}% Lexical"
                        )
                    with col_c:
                        st.info(f"👤 **User ID:** {st.session_state.user_id[:12]}...")

                # Display active filters
                active_filters = [
                    f"**{k.replace('_', ' ').title()}:** {v}"
                    for k, v in filter_params.items()
                    if v
                ]
                if active_filters:
                    st.info("🎯 **Active Filters:** " + " | ".join(active_filters))

                st.markdown("---")

                # Display results with interactive buttons
                for idx, drama in enumerate(recommendations, 1):
                    card_html, title, rank = format_drama_card(drama, idx)

                    # Display card
                    st.markdown(card_html, unsafe_allow_html=True)

                    # Interactive buttons below each card
                    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 3])

                    with btn_col1:
                        if st.button("👁️ View", key=f"view_{idx}_{title}"):
                            log_interaction(title, "click", position=idx)
                            # Add to viewed dramas (keep last 50)
                            if title not in st.session_state.viewed_dramas:
                                st.session_state.viewed_dramas.insert(0, title)
                                if len(st.session_state.viewed_dramas) > 50:
                                    st.session_state.viewed_dramas.pop()
                            st.toast(f"✅ Tracked click: {title}", icon="✅")

                    with btn_col2:
                        if title in st.session_state.watchlist:
                            if st.button(
                                "✓ In List",
                                key=f"watchlist_{idx}_{title}",
                                type="primary",
                            ):
                                st.session_state.watchlist.remove(title)
                                log_interaction(title, "watchlist_remove")
                                st.toast(f"Removed from watchlist: {title}", icon="ℹ️")
                                st.rerun()
                        else:
                            if st.button(
                                "➕ Watchlist", key=f"watchlist_{idx}_{title}"
                            ):
                                st.session_state.watchlist.add(title)
                                log_interaction(title, "watchlist_add")
                                st.toast(f"✅ Added to watchlist: {title}", icon="✅")
                                st.rerun()

                    with btn_col3:
                        if st.button("🔄 Similar", key=f"similar_{idx}_{title}"):
                            st.session_state.quick_search_query = title
                            st.session_state.quick_search_genre = None
                            st.session_state.last_results = (
                                None  # Clear to trigger new search
                            )
                            st.rerun()

                    st.markdown("---")

            else:
                st.warning(
                    "😔 No recommendations found. Try adjusting your search or filters!"
                )
                st.info(
                    "💡 **Tips:**\n- Try a broader search term\n- Remove some filters\n- Check spelling of drama titles"
                )

with tab2:
    st.markdown("### � My Profile")
    st.markdown(f"**User ID:** `{st.session_state.user_id}`")
    st.markdown(f"**Session ID:** `{st.session_state.session_id}`")
    
    st.markdown("---")
    
    # Watchlist Section
    st.markdown("### 📝 My Watchlist")
    if st.session_state.watchlist:
        st.info(f"You have **{len(st.session_state.watchlist)}** dramas in your watchlist")
        
        for drama in st.session_state.watchlist:
            col_w1, col_w2, col_w3 = st.columns([4, 1, 1])
            with col_w1:
                st.markdown(f"**🎬 {drama}**")
            with col_w2:
                if st.button("🔍 Search", key=f"search_watchlist_{drama}"):
                    st.session_state.quick_search_query = drama
                    st.session_state.last_results = None
                    st.rerun()
            with col_w3:
                if st.button("🗑️ Remove", key=f"remove_watchlist_{drama}"):
                    st.session_state.watchlist.remove(drama)
                    log_interaction(drama, "watchlist_remove")
                    st.toast(f"Removed: {drama}", icon="ℹ️")
                    st.rerun()
            st.markdown("---")
    else:
        st.warning("📭 Your watchlist is empty!")
        st.info("💡 **Tip:** Search for dramas and click '➕ Watchlist' to save them here.")
    
    st.markdown("---")
    
    # Viewed Dramas Section
    st.markdown("### 👁️ Recently Viewed")
    if st.session_state.viewed_dramas:
        st.info(f"You have viewed **{len(st.session_state.viewed_dramas)}** dramas in this session")
        
        for drama in st.session_state.viewed_dramas[:20]:  # Show last 20
            col_v1, col_v2, col_v3 = st.columns([4, 1, 1])
            with col_v1:
                st.markdown(f"**👁️ {drama}**")
            with col_v2:
                if st.button("🔍 Search", key=f"search_viewed_{drama}"):
                    st.session_state.quick_search_query = drama
                    st.session_state.last_results = None
                    st.rerun()
            with col_v3:
                if drama not in st.session_state.watchlist:
                    if st.button("➕ Add", key=f"add_viewed_{drama}"):
                        st.session_state.watchlist.add(drama)
                        log_interaction(drama, "watchlist_add")
                        st.toast(f"✅ Added to watchlist: {drama}", icon="✅")
                        st.rerun()
            st.markdown("---")
    else:
        st.warning("👁️ You haven't viewed any dramas yet!")
        st.info("💡 **Tip:** Search for dramas and click '👁️ View' to track them here.")
    
    st.markdown("---")
    
    # Clear buttons
    col_clear1, col_clear2 = st.columns(2)
    with col_clear1:
        if st.button("🗑️ Clear Watchlist", type="secondary", use_container_width=True):
            st.session_state.watchlist.clear()
            st.toast("Watchlist cleared!", icon="ℹ️")
            st.rerun()
    with col_clear2:
        if st.button("🗑️ Clear Viewed History", type="secondary", use_container_width=True):
            st.session_state.viewed_dramas.clear()
            st.toast("Viewed history cleared!", icon="ℹ️")
            st.rerun()

with tab3:
    st.markdown("### �📊 SeoulMate Statistics")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Total Dramas", "1,922", help="Complete database of K-dramas")
    with col2:
        st.metric(
            "🤖 AI Model",
            "v4.0 Phase 1",
            help="Latest recommendation engine with query intelligence",
        )
    with col3:
        st.metric("🎯 Accuracy", "Fine-tuned", help="Trained on 1,922 dramas")
    with col4:
        st.metric("⚡ Speed", "< 1s", help="Average response time")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 🧠 AI Technology Stack")
        st.markdown(
            """
        - **SBERT Model:** `sbert-finetuned-full`
          - 3 epochs training
          - Multilingual support
          - Semantic understanding
        
        - **Retrieval System:** Hybrid approach
          - FAISS IndexFlatIP for vector search
          - BM25Plus for lexical matching
          - **Dynamic Alpha** (α=0.2-0.95) 🆕
        
        - **Reranker:** Cross-encoder
          - 3 epochs training
          - 25,000+ training pairs
          - Precision refinement
        
        - **Phase 1 Enhancements:** 🆕
          - Query intent detection
          - Dynamic weight adjustment
          - Query expansion with synonyms
          - Click tracking & analytics
        """
        )

    with col_right:
        st.markdown("#### 🎯 Features")
        st.markdown(
            """
        ✅ **Smart Semantic Search**
        - Understands context and meaning
        - Works with descriptions
        
        ✅ **Fuzzy Matching**
        - Handles typos gracefully
        - Finds close matches
        
        ✅ **Advanced Filters**
        - Genre, director, network
        - Ratings and popularity
        - Custom keywords
        
        ✅ **Similar Drama Finder**
        - Discover shows like your favorites
        - AI-powered similarity
        
        ✅ **Flexible Sorting**
        - By rating, popularity, date
        - Ascending or descending
        """
        )

    st.markdown("---")
    st.markdown("#### 🔧 Backend Technology")
    st.code(
        """
    Backend: FastAPI v3.1
    Models: Sentence-Transformers (SBERT)
    Vector DB: FAISS
    Lexical: BM25Plus
    Reranker: Cross-Encoder
    """,
        language="text",
    )

with tab4:
    st.markdown("### 📈 Platform Analytics & Trends")

    # Fetch analytics from backend
    st.markdown("#### 🔥 Trending Right Now")
    try:
        # Popular dramas
        popular_response = requests.get(
            f"{API_URL}/analytics/popular", params={"days": 7}, timeout=5
        )
        if popular_response.status_code == 200:
            popular = popular_response.json()
            if popular:
                st.markdown("##### 🏆 Most Popular Dramas (Last 7 Days)")
                for item in popular[:10]:
                    col_p1, col_p2, col_p3 = st.columns([3, 1, 1])
                    with col_p1:
                        st.write(f"🎬 {item['drama_title']}")
                    with col_p2:
                        st.write(f"💯 Score: {item['score']}")
                    with col_p3:
                        st.write(f"👁️ Clicks: {item['clicks']}")

        # Trending searches
        st.markdown("---")
        trending_response = requests.get(
            f"{API_URL}/analytics/trending-searches", params={"limit": 10}, timeout=5
        )
        if trending_response.status_code == 200:
            trending = trending_response.json()
            if trending:
                st.markdown("##### 🔎 Trending Searches")
                for item in trending:
                    col_t1, col_t2, col_t3 = st.columns([3, 1, 1])
                    with col_t1:
                        st.write(f"🔍 {item['query']}")
                    with col_t2:
                        st.write(f"📊 {item['count']} searches")
                    with col_t3:
                        intent = item.get("intent", "unknown").replace("_", " ").title()
                        st.write(f"🧠 {intent}")

        # Overall analytics summary
        st.markdown("---")
        summary_response = requests.get(f"{API_URL}/analytics/summary", timeout=5)
        if summary_response.status_code == 200:
            summary = summary_response.json()
            st.markdown("##### 📊 Overall Platform Stats")

            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1:
                st.metric("🔍 Total Searches", summary.get("total_searches", 0))
            with col_s2:
                st.metric("👆 Total Clicks", summary.get("total_clicks", 0))
            with col_s3:
                ctr = summary.get("average_ctr", 0)
                st.metric("📈 Avg CTR", f"{ctr:.1f}%")
            with col_s4:
                st.metric("👥 Unique Users", summary.get("unique_users", 0))

    except Exception as e:
        st.warning(f"⚠️ Could not load analytics: {str(e)}")
        st.info("Make sure the backend is running!")

with tab5:
    st.markdown("### ℹ️ How SeoulMate Works")

    st.markdown("#### 🔍 The Recommendation Process")

    st.markdown(
        """
    **Step 1: Understanding Your Query** 🧠
    - SeoulMate uses AI to understand what you're looking for
    - Works with drama titles, genres, or descriptions
    - Handles typos and fuzzy matches
    
    **Step 2: Smart Search** 🔎
    - **Semantic Search (FAISS):** Finds dramas with similar meanings
    - **Lexical Search (BM25Plus):** Matches keywords and terms
    - Combines both for best results
    
    **Step 3: Filtering** 🎯
    - Applies your selected filters (genre, director, rating, etc.)
    - Sorts by your preferred criteria
    
    **Step 4: Precision Reranking** ⚡
    - Cross-encoder analyzes each match
    - Reorders results for maximum relevance
    
    **Step 5: Results!** 🎉
    - Top recommendations delivered to you
    - Complete with ratings, cast, and synopsis
    """
    )

    st.markdown("---")

    st.markdown("#### 🚀 Getting Started")
    st.markdown(
        """
    1. **Simple Search:** Just type a drama title or genre
    2. **Use Filters:** Refine by genre, director, ratings, etc.
    3. **Find Similar:** Enter a drama you love in "Similar To"
    4. **Sort Results:** Order by rating, popularity, or date
    """
    )

    st.markdown("---")

    st.markdown("#### 💡 Pro Tips")
    st.info(
        """
    - 🎭 **For Genre Searches:** Try "romantic comedy", "thriller", "historical"
    - 🎬 **For Director/Cast:** Use the advanced filters in the sidebar
    - ⭐ **For Top Rated:** Set minimum rating to 8.0 or higher
    - 🔄 **For Similar Dramas:** Use the "Similar To" filter
    - 📊 **For Sorting:** Choose "rating_value" to see highest rated first
    """
    )

    st.markdown("---")

    with st.expander("❓ Need Help?"):
        st.markdown(
            """
        **Common Questions:**
        
        - **Q: How accurate are the recommendations?**
          - A: Our AI is trained on 1,922 dramas with 3 epochs of fine-tuning for high accuracy.
        
        - **Q: Can I search in other languages?**
          - A: Our model supports multilingual queries!
        
        - **Q: How do I find dramas like my favorite?**
          - A: Use the "Similar To" filter and enter your favorite drama's title.
        
        - **Q: What if I get no results?**
          - A: Try broader search terms or remove some filters.
        """
        )

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 2rem; color: #6c757d;">
        <p style="font-size: 0.9rem; margin-bottom: 0.5rem;">
            Made with ❤️ by the SeoulMate Team | Powered by AI & Advanced Machine Learning
        </p>
        <p style="font-size: 0.8rem; opacity: 0.7;">
            © 2025 SeoulMate - Your K-Drama Companion | v4.0 Phase 1 🆕
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
