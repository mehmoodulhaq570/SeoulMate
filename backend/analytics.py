"""
User Analytics Module for SeoulMate v4.0
=========================================
Phase 1 Enhancement: Click Tracking and User Interaction Logging

Features:
1. Track user interactions (clicks, searches, watchlist actions)
2. Log search queries and results
3. Calculate implicit feedback scores
4. Store analytics data for future ML improvements
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, Counter


# Analytics data file
ANALYTICS_DIR = Path("analytics_data")
ANALYTICS_DIR.mkdir(exist_ok=True)

INTERACTIONS_FILE = ANALYTICS_DIR / "interactions.jsonl"  # JSONL for append efficiency
SEARCH_LOG_FILE = ANALYTICS_DIR / "search_log.jsonl"
USER_STATS_FILE = ANALYTICS_DIR / "user_stats.json"


class AnalyticsTracker:
    """Tracks and logs user interactions for recommendation improvement"""

    def __init__(self):
        self.interactions_file = INTERACTIONS_FILE
        self.search_log_file = SEARCH_LOG_FILE
        self.user_stats_file = USER_STATS_FILE

        # Ensure files exist
        self.interactions_file.touch(exist_ok=True)
        self.search_log_file.touch(exist_ok=True)
        if not self.user_stats_file.exists():
            self._save_user_stats({})

    def log_search(
        self,
        user_id: str,
        query: str,
        intent: str,
        results: List[str],
        filters: Dict,
        session_id: str,
    ) -> str:
        """
        Log a search query and its results

        Args:
            user_id: User identifier
            query: Search query
            intent: Detected intent from query analyzer
            results: List of drama titles returned
            filters: Applied filters (genre, rating, etc.)
            session_id: Session identifier

        Returns:
            search_id for tracking interactions
        """
        search_id = f"search_{datetime.utcnow().timestamp()}"

        search_data = {
            "search_id": search_id,
            "user_id": user_id,
            "query": query,
            "intent": intent,
            "results": results,
            "filters": filters,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "result_count": len(results),
        }

        # Append to search log (JSONL format)
        with open(self.search_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(search_data) + "\n")

        return search_id

    def log_interaction(
        self,
        user_id: str,
        drama_title: str,
        action: str,
        search_id: Optional[str] = None,
        position: Optional[int] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """
        Log user interaction with a drama

        Args:
            user_id: User identifier
            drama_title: Drama title
            action: Type of action (click, watchlist_add, watchlist_remove, rating, view_details)
            search_id: Related search ID (if from search results)
            position: Position in search results (1-indexed)
            session_id: Session identifier
            metadata: Additional metadata
        """
        interaction_data = {
            "user_id": user_id,
            "drama_title": drama_title,
            "action": action,
            "search_id": search_id,
            "position": position,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        # Append to interactions log
        with open(self.interactions_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(interaction_data) + "\n")

        # Update user stats
        self._update_user_stats(user_id, drama_title, action)

    def _update_user_stats(self, user_id: str, drama_title: str, action: str):
        """Update aggregated user statistics"""
        stats = self._load_user_stats()

        if user_id not in stats:
            stats[user_id] = {
                "total_searches": 0,
                "total_clicks": 0,
                "watchlist_adds": 0,
                "favorite_genres": [],
                "favorite_actors": [],
                "interaction_count": 0,
                "last_active": None,
                "clicked_dramas": [],
                "watchlist": [],
            }

        user_stats = stats[user_id]
        user_stats["interaction_count"] += 1
        user_stats["last_active"] = datetime.utcnow().isoformat()

        # Track specific actions
        if action == "click":
            user_stats["total_clicks"] += 1
            if drama_title not in user_stats["clicked_dramas"]:
                user_stats["clicked_dramas"].append(drama_title)
                # Keep only last 100 clicked dramas
                user_stats["clicked_dramas"] = user_stats["clicked_dramas"][-100:]

        elif action == "watchlist_add":
            user_stats["watchlist_adds"] += 1
            if drama_title not in user_stats["watchlist"]:
                user_stats["watchlist"].append(drama_title)

        elif action == "watchlist_remove":
            if drama_title in user_stats["watchlist"]:
                user_stats["watchlist"].remove(drama_title)

        self._save_user_stats(stats)

    def get_user_stats(self, user_id: str) -> Dict:
        """Get aggregated statistics for a user"""
        stats = self._load_user_stats()
        return stats.get(user_id, {})

    def get_click_through_rate(self, search_id: str) -> float:
        """
        Calculate click-through rate for a search

        Returns:
            CTR as a float (0.0 to 1.0)
        """
        # Load interactions
        interactions = self._load_interactions()

        # Filter by search_id
        search_interactions = [
            i for i in interactions if i.get("search_id") == search_id
        ]

        if not search_interactions:
            return 0.0

        # Count clicks
        clicks = sum(1 for i in search_interactions if i["action"] == "click")

        # Get result count from search log
        search_data = self._get_search_by_id(search_id)
        if not search_data:
            return 0.0

        result_count = search_data.get("result_count", 1)
        return clicks / result_count if result_count > 0 else 0.0

    def get_popular_dramas(self, days: int = 7, limit: int = 20) -> List[Dict]:
        """
        Get most popular dramas based on recent interactions

        Args:
            days: Look back period
            limit: Number of results

        Returns:
            List of {drama_title, score, click_count, watchlist_count}
        """
        interactions = self._load_interactions(days=days)

        # Count interactions per drama
        drama_scores = defaultdict(
            lambda: {"clicks": 0, "watchlist_adds": 0, "score": 0}
        )

        for interaction in interactions:
            drama = interaction["drama_title"]
            action = interaction["action"]

            if action == "click":
                drama_scores[drama]["clicks"] += 1
                drama_scores[drama]["score"] += 1  # Click = 1 point
            elif action == "watchlist_add":
                drama_scores[drama]["watchlist_adds"] += 1
                drama_scores[drama]["score"] += 3  # Watchlist = 3 points

        # Sort by score
        popular = [
            {
                "drama_title": drama,
                "score": data["score"],
                "click_count": data["clicks"],
                "watchlist_count": data["watchlist_adds"],
            }
            for drama, data in drama_scores.items()
        ]

        popular.sort(key=lambda x: x["score"], reverse=True)
        return popular[:limit]

    def get_trending_searches(self, days: int = 7, limit: int = 20) -> List[Dict]:
        """
        Get trending search queries

        Returns:
            List of {query, count, intent}
        """
        searches = self._load_searches(days=days)

        # Count query frequency
        query_counts = Counter()
        query_intents = {}

        for search in searches:
            query = search["query"].lower()
            query_counts[query] += 1
            query_intents[query] = search.get("intent", "unknown")

        # Build result
        trending = [
            {
                "query": query,
                "count": count,
                "intent": query_intents.get(query, "unknown"),
            }
            for query, count in query_counts.most_common(limit)
        ]

        return trending

    def get_user_preferences(self, user_id: str) -> Dict:
        """
        Infer user preferences from interaction history

        Returns:
            {
                'favorite_genres': List[str],
                'favorite_actors': List[str],
                'preferred_era': str,
                'avg_rating_preference': float
            }
        """
        interactions = self._load_interactions(user_id=user_id)

        # Get dramas user interacted with
        interacted_dramas = set()
        for interaction in interactions:
            if interaction["action"] in ["click", "watchlist_add"]:
                interacted_dramas.add(interaction["drama_title"])

        # TODO: Match with drama metadata to extract genres, actors, years
        # For now, return basic structure
        return {
            "interacted_dramas": list(interacted_dramas),
            "interaction_count": len(interactions),
            "watchlist_size": len(
                [i for i in interactions if i["action"] == "watchlist_add"]
            ),
        }

    def _load_interactions(
        self, days: Optional[int] = None, user_id: Optional[str] = None
    ) -> List[Dict]:
        """Load interactions from file with optional filtering"""
        if not self.interactions_file.exists():
            return []

        interactions = []
        cutoff_date = None

        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

        with open(self.interactions_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())

                    # Filter by date
                    if cutoff_date:
                        timestamp = datetime.fromisoformat(data["timestamp"])
                        if timestamp < cutoff_date:
                            continue

                    # Filter by user
                    if user_id and data.get("user_id") != user_id:
                        continue

                    interactions.append(data)
                except json.JSONDecodeError:
                    continue

        return interactions

    def _load_searches(self, days: Optional[int] = None) -> List[Dict]:
        """Load search logs with optional date filtering"""
        if not self.search_log_file.exists():
            return []

        searches = []
        cutoff_date = None

        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

        with open(self.search_log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())

                    if cutoff_date:
                        timestamp = datetime.fromisoformat(data["timestamp"])
                        if timestamp < cutoff_date:
                            continue

                    searches.append(data)
                except json.JSONDecodeError:
                    continue

        return searches

    def _get_search_by_id(self, search_id: str) -> Optional[Dict]:
        """Get search data by ID"""
        searches = self._load_searches()
        for search in searches:
            if search.get("search_id") == search_id:
                return search
        return None

    def _load_user_stats(self) -> Dict:
        """Load user statistics"""
        if not self.user_stats_file.exists():
            return {}

        with open(self.user_stats_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_user_stats(self, stats: Dict):
        """Save user statistics"""
        with open(self.user_stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

    def get_analytics_summary(self, days: int = 7) -> Dict:
        """
        Get overall analytics summary

        Returns summary of system usage and performance
        """
        interactions = self._load_interactions(days=days)
        searches = self._load_searches(days=days)

        # Calculate metrics
        total_searches = len(searches)
        total_interactions = len(interactions)
        total_clicks = sum(1 for i in interactions if i["action"] == "click")
        total_watchlist_adds = sum(
            1 for i in interactions if i["action"] == "watchlist_add"
        )

        # Unique users
        unique_users = len(set(i["user_id"] for i in interactions if "user_id" in i))

        # Average CTR
        avg_ctr = (total_clicks / total_searches) if total_searches > 0 else 0

        return {
            "period_days": days,
            "total_searches": total_searches,
            "total_interactions": total_interactions,
            "total_clicks": total_clicks,
            "total_watchlist_adds": total_watchlist_adds,
            "unique_users": unique_users,
            "average_ctr": round(avg_ctr, 3),
            "interactions_per_user": (
                round(total_interactions / unique_users, 2) if unique_users > 0 else 0
            ),
        }


# Singleton instance
_tracker = None


def get_tracker() -> AnalyticsTracker:
    """Get global analytics tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = AnalyticsTracker()
    return _tracker


# Example usage
if __name__ == "__main__":
    tracker = get_tracker()

    # Test logging
    print("Testing Analytics Tracker...")

    # Log a search
    search_id = tracker.log_search(
        user_id="test_user",
        query="romantic comedy",
        intent="genre_browse",
        results=["Drama 1", "Drama 2", "Drama 3"],
        filters={"genre": "Romance"},
        session_id="session_123",
    )
    print(f"✓ Logged search: {search_id}")

    # Log interactions
    tracker.log_interaction(
        user_id="test_user",
        drama_title="Drama 1",
        action="click",
        search_id=search_id,
        position=1,
        session_id="session_123",
    )
    print("✓ Logged click interaction")

    tracker.log_interaction(
        user_id="test_user",
        drama_title="Drama 1",
        action="watchlist_add",
        session_id="session_123",
    )
    print("✓ Logged watchlist add")

    # Get stats
    stats = tracker.get_user_stats("test_user")
    print(f"\n📊 User Stats: {json.dumps(stats, indent=2)}")

    summary = tracker.get_analytics_summary(days=30)
    print(f"\n📈 Analytics Summary: {json.dumps(summary, indent=2)}")
