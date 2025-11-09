"""
Query Analyzer for SeoulMate v4.0
==================================
Phase 1 Enhancement: Query Intent Detection, Dynamic Weights, and Query Expansion

Features:
1. Intent Detection - Understand what user is looking for
2. Entity Extraction - Extract actors, genres, years, etc.
3. Query Expansion - Add synonyms and related terms
4. Dynamic Weight Calculation - Adjust semantic/lexical balance
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum


class QueryIntent(Enum):
    """Different types of user intents"""

    SIMILAR_TO = "similar_to"  # "like Goblin", "similar to..."
    GENRE_BROWSE = "genre_browse"  # "romance drama", "action series"
    ACTOR_BASED = "actor_based"  # "Park Seo-joon drama"
    TOP_RATED = "top_rated"  # "best drama", "top rated"
    YEAR_BASED = "year_based"  # "2023 drama", "recent shows"
    EMOTION_BASED = "emotion_based"  # "sad drama", "feel-good"
    CONSTRAINT_BASED = "constraint"  # "short drama", "under 10 episodes"
    TRENDING = "trending"  # "popular now", "trending"
    VAGUE = "vague"  # "good drama", "something nice"
    SPECIFIC_TITLE = "specific_title"  # Direct title search


# Synonym dictionary for query expansion
SYNONYMS = {
    # Emotions
    "funny": ["comedy", "humorous", "lighthearted", "hilarious", "witty"],
    "sad": ["melodrama", "tearjerker", "emotional", "tragic", "touching"],
    "scary": ["horror", "thriller", "suspense", "creepy", "dark"],
    "happy": ["uplifting", "cheerful", "feel-good", "heartwarming", "joyful"],
    "romantic": ["romance", "love story", "romantic", "sweet"],
    "exciting": ["action", "thrilling", "intense", "fast-paced"],
    # Time-related
    "old": ["classic", "vintage", "retro", "90s", "2000s"],
    "new": ["recent", "latest", "modern", "current", "2023", "2024", "2025"],
    "recent": ["new", "latest", "modern", "current"],
    # Quality
    "best": ["top rated", "highly rated", "excellent", "masterpiece"],
    "good": ["great", "quality", "recommended", "popular"],
    "popular": ["trending", "famous", "well-known", "hit"],
    # Length
    "short": ["mini series", "few episodes", "quick watch"],
    "long": ["many episodes", "extended", "lengthy series"],
}


# Intent detection patterns
INTENT_PATTERNS = {
    QueryIntent.SIMILAR_TO: [
        r"(like|similar to|same as|reminds me of)\s+(.+)",
        r"(similar|like)\s+",
        r"more\s+(of|like)",
    ],
    QueryIntent.ACTOR_BASED: [
        r"(with|starring|featuring|by)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(drama|series|show)",
    ],
    QueryIntent.TOP_RATED: [
        r"(best|top rated|highly rated|excellent|masterpiece)",
        r"(top|best)\s+\d+",
        r"highest\s+rated",
    ],
    QueryIntent.YEAR_BASED: [
        r"(20\d{2}|19\d{2})",  # Match years
        r"(recent|new|latest|current|modern)",
        r"from\s+(20\d{2})",
    ],
    QueryIntent.EMOTION_BASED: [
        r"(sad|funny|scary|happy|romantic|exciting|emotional|touching|heartwarming)",
        r"(cry|laugh|smile|scared|romance)",
        r"(feel good|tearjerker|lighthearted)",
    ],
    QueryIntent.CONSTRAINT_BASED: [
        r"(short|long|quick|under|less than|more than)\s+\d*\s*(episode|ep)",
        r"(mini series|limited series)",
    ],
    QueryIntent.TRENDING: [
        r"(trending|popular now|what's hot|viral|buzz)",
        r"(everyone\s+watching|currently\s+watching)",
    ],
    QueryIntent.VAGUE: [
        r"^(good|nice|great|something|any|recommend)(\s+drama)?$",
        r"^(what\s+should\s+i\s+watch|suggest|recommend)$",
    ],
}


class QueryAnalyzer:
    """Analyzes user queries to extract intent, entities, and expand terms"""

    def __init__(self):
        self.synonyms = SYNONYMS
        self.intent_patterns = INTENT_PATTERNS

    def analyze(self, query: str) -> Dict:
        """
        Main analysis function

        Returns:
            {
                'original_query': str,
                'intent': QueryIntent,
                'expanded_query': str,
                'entities': dict,
                'dynamic_alpha': float,
                'confidence': float
            }
        """
        query_lower = query.lower().strip()

        # Detect intent
        intent, confidence = self._detect_intent(query_lower)

        # Extract entities
        entities = self._extract_entities(query_lower)

        # Expand query with synonyms
        expanded_query = self._expand_query(query_lower)

        # Calculate dynamic alpha (semantic vs lexical weight)
        dynamic_alpha = self._calculate_dynamic_alpha(intent, entities)

        return {
            "original_query": query,
            "intent": intent,
            "expanded_query": expanded_query,
            "entities": entities,
            "dynamic_alpha": dynamic_alpha,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _detect_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """
        Detect user intent from query

        Returns:
            (intent, confidence_score)
        """
        # Check each intent pattern
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent, 0.9  # High confidence on pattern match

        # Check for specific title (capitalized words)
        if re.search(r"[A-Z][a-z]+(\s+[A-Z][a-z]+)+", query):
            return QueryIntent.SPECIFIC_TITLE, 0.8

        # Default to genre browse if contains common genres
        common_genres = [
            "romance",
            "action",
            "comedy",
            "thriller",
            "historical",
            "fantasy",
            "horror",
            "drama",
            "crime",
            "mystery",
        ]
        if any(genre in query for genre in common_genres):
            return QueryIntent.GENRE_BROWSE, 0.7

        # Fallback to vague
        return QueryIntent.VAGUE, 0.5

    def _extract_entities(self, query: str) -> Dict:
        """
        Extract entities like actors, years, genres, etc.

        Returns:
            {
                'actors': List[str],
                'genres': List[str],
                'years': List[int],
                'emotions': List[str],
                'constraints': Dict
            }
        """
        entities = {
            "actors": [],
            "genres": [],
            "years": [],
            "emotions": [],
            "constraints": {},
        }

        # Extract actors (capitalized names)
        actor_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b"
        entities["actors"] = re.findall(actor_pattern, query)

        # Extract years
        year_pattern = r"\b(19\d{2}|20[0-2]\d)\b"
        entities["years"] = [int(y) for y in re.findall(year_pattern, query)]

        # Extract genres
        common_genres = [
            "romance",
            "action",
            "comedy",
            "thriller",
            "historical",
            "fantasy",
            "horror",
            "drama",
            "crime",
            "mystery",
            "sci-fi",
            "melodrama",
            "slice of life",
        ]
        entities["genres"] = [g for g in common_genres if g in query.lower()]

        # Extract emotions
        emotions = [
            "sad",
            "funny",
            "scary",
            "happy",
            "romantic",
            "exciting",
            "emotional",
            "touching",
            "heartwarming",
        ]
        entities["emotions"] = [e for e in emotions if e in query.lower()]

        # Extract constraints (episode count, duration)
        episode_match = re.search(
            r"(under|less than|fewer than)\s+(\d+)\s+episode", query
        )
        if episode_match:
            entities["constraints"]["max_episodes"] = int(episode_match.group(2))

        episode_match = re.search(r"(more than|over)\s+(\d+)\s+episode", query)
        if episode_match:
            entities["constraints"]["min_episodes"] = int(episode_match.group(2))

        return entities

    def _expand_query(self, query: str) -> str:
        """
        Expand query with synonyms and related terms

        Example:
            "funny drama" -> "funny comedy humorous lighthearted drama"
        """
        words = query.split()
        expanded_words = []

        for word in words:
            expanded_words.append(word)

            # Add synonyms if available
            if word in self.synonyms:
                # Add top 2 synonyms to avoid too much expansion
                expanded_words.extend(self.synonyms[word][:2])

        return " ".join(expanded_words)

    def _calculate_dynamic_alpha(self, intent: QueryIntent, entities: Dict) -> float:
        """
        Calculate dynamic alpha (semantic vs lexical weight)

        Alpha ranges from 0.0 (all lexical) to 1.0 (all semantic)
        Default is 0.7 (70% semantic, 30% lexical)

        Strategy:
        - Specific searches (titles, actors) -> More lexical (lower alpha)
        - Vague/emotional searches -> More semantic (higher alpha)
        """
        # Intent-based weights
        intent_weights = {
            QueryIntent.SPECIFIC_TITLE: 0.3,  # Very lexical
            QueryIntent.ACTOR_BASED: 0.35,  # Mostly lexical
            QueryIntent.YEAR_BASED: 0.5,  # Balanced
            QueryIntent.GENRE_BROWSE: 0.65,  # Slightly semantic
            QueryIntent.TOP_RATED: 0.6,  # Balanced-semantic
            QueryIntent.EMOTION_BASED: 0.85,  # Very semantic
            QueryIntent.SIMILAR_TO: 0.75,  # Semantic
            QueryIntent.TRENDING: 0.55,  # Balanced
            QueryIntent.CONSTRAINT_BASED: 0.6,  # Balanced-semantic
            QueryIntent.VAGUE: 0.8,  # Very semantic
        }

        base_alpha = intent_weights.get(intent, 0.7)

        # Adjust based on entities
        if entities["actors"]:
            base_alpha -= 0.1  # More lexical if actor mentioned

        if entities["years"]:
            base_alpha -= 0.05  # Slightly more lexical

        if entities["emotions"]:
            base_alpha += 0.1  # More semantic for emotions

        # Clamp to valid range
        return max(0.2, min(0.95, base_alpha))


# Utility functions
def get_search_strategy(intent: QueryIntent) -> Dict:
    """
    Get recommended search strategy for each intent

    Returns:
        {
            'use_reranker': bool,
            'top_k_candidates': int,
            'apply_diversity': bool,
            'boost_popularity': float
        }
    """
    strategies = {
        QueryIntent.SPECIFIC_TITLE: {
            "use_reranker": False,  # Exact match is enough
            "top_k_candidates": 20,
            "apply_diversity": False,
            "boost_popularity": 0.0,
        },
        QueryIntent.ACTOR_BASED: {
            "use_reranker": True,
            "top_k_candidates": 50,
            "apply_diversity": True,
            "boost_popularity": 0.1,
        },
        QueryIntent.TOP_RATED: {
            "use_reranker": True,
            "top_k_candidates": 100,
            "apply_diversity": True,
            "boost_popularity": 0.2,
        },
        QueryIntent.EMOTION_BASED: {
            "use_reranker": True,
            "top_k_candidates": 80,
            "apply_diversity": True,
            "boost_popularity": 0.05,
        },
        QueryIntent.VAGUE: {
            "use_reranker": True,
            "top_k_candidates": 100,
            "apply_diversity": True,
            "boost_popularity": 0.3,  # Boost popular items
        },
        QueryIntent.TRENDING: {
            "use_reranker": False,
            "top_k_candidates": 50,
            "apply_diversity": True,
            "boost_popularity": 0.5,  # Heavy popularity boost
        },
    }

    # Default strategy
    default = {
        "use_reranker": True,
        "top_k_candidates": 50,
        "apply_diversity": True,
        "boost_popularity": 0.1,
    }

    return strategies.get(intent, default)


# Example usage and testing
if __name__ == "__main__":
    analyzer = QueryAnalyzer()

    # Test cases
    test_queries = [
        "romantic comedy drama",
        "something like Goblin",
        "Park Seo-joon drama",
        "best 2023 drama",
        "sad emotional drama",
        "short drama under 10 episodes",
        "trending drama",
        "good drama",
        "Crash Landing on You",
    ]

    print("=" * 80)
    print("QUERY ANALYZER TEST")
    print("=" * 80)

    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        result = analyzer.analyze(query)
        print(
            f"   Intent: {result['intent'].value} (confidence: {result['confidence']})"
        )
        print(f"   Dynamic Alpha: {result['dynamic_alpha']:.2f}")
        print(f"   Expanded: '{result['expanded_query']}'")
        if result["entities"]["actors"]:
            print(f"   Actors: {result['entities']['actors']}")
        if result["entities"]["genres"]:
            print(f"   Genres: {result['entities']['genres']}")
        if result["entities"]["emotions"]:
            print(f"   Emotions: {result['entities']['emotions']}")

        strategy = get_search_strategy(result["intent"])
        print(
            f"   Strategy: Reranker={strategy['use_reranker']}, "
            f"Diversity={strategy['apply_diversity']}, "
            f"Pop Boost={strategy['boost_popularity']}"
        )
