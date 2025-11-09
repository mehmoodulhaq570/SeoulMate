# 🚀 Phase 1 - Quick Start Guide

## Run & Test in 3 Steps

### Step 1: Start Backend

```bash
cd backend
python app.py
```

### Step 2: Run Tests

```bash
python test_phase1.py
```

### Step 3: Try API

```bash
# Query with intent detection
curl "http://127.0.0.1:8001/recommend?title=sad%20drama&top_n=5"

# Check analytics
curl "http://127.0.0.1:8001/analytics/summary"
```

---

## 🎯 Key Features

| Feature              | What It Does                | Example                                 |
| -------------------- | --------------------------- | --------------------------------------- |
| **Intent Detection** | Understands query type      | "Park Seo-joon" → ACTOR_BASED           |
| **Dynamic Alpha**    | Auto-adjusts search weights | Actor search: 35% semantic, 65% lexical |
| **Query Expansion**  | Adds synonyms               | "funny" → "comedy, humorous, witty"     |
| **Click Tracking**   | Logs user behavior          | Tracks clicks, watchlist, views         |
| **Analytics**        | Shows trends & stats        | Popular dramas, trending searches       |

---

## 📊 New API Endpoints

```bash
# Recommendations (enhanced)
GET /recommend?title=query&user_id=123&session_id=abc

# Log interaction
POST /analytics/interaction?user_id=123&drama_title=Goblin&action=click

# Get popular dramas
GET /analytics/popular?days=7&limit=20

# Get trending searches
GET /analytics/trending-searches?days=7

# Get analytics summary
GET /analytics/summary?days=7

# Get user stats
GET /analytics/user-stats/{user_id}
```

---

## 🧪 Test Different Query Types

```bash
# Emotion-based (high semantic)
curl "http://127.0.0.1:8001/recommend?title=sad%20emotional%20drama"

# Actor-based (high lexical)
curl "http://127.0.0.1:8001/recommend?title=Park%20Seo-joon%20drama"

# Genre-based (balanced)
curl "http://127.0.0.1:8001/recommend?title=romantic%20comedy"

# Similar-to (semantic)
curl "http://127.0.0.1:8001/recommend?title=like%20Goblin"

# Top-rated
curl "http://127.0.0.1:8001/recommend?title=best%202023%20drama"
```

---

## 📈 Check Response

```json
{
  "query": {
    "Title": "sad drama",
    "expanded": "sad melodrama tearjerker emotional tragic drama"
  },
  "analysis": {
    "intent": "emotion_based",
    "dynamic_alpha": 0.85,
    "confidence": 0.9
  },
  "recommendations": [...]
}
```

---

## 🔧 Files Added

- `backend/query_analyzer.py` - Query intelligence
- `backend/analytics.py` - User tracking
- `backend/test_phase1.py` - Test suite
- `analytics_data/` - Analytics storage (auto-created)
- `PHASE1_COMPLETE.md` - Full documentation

---

## ✅ Success Checklist

- [ ] Backend starts without errors
- [ ] Test suite passes all tests
- [ ] Query intent detection works
- [ ] Dynamic alpha changes per query type
- [ ] Analytics endpoints return data
- [ ] API docs show new endpoints: http://127.0.0.1:8001/docs

---

## 🎉 You're Ready!

**SeoulMate v4.0 Phase 1** is now running with:

- Smart query understanding
- Dynamic search weights
- User behavior tracking
- Real-time analytics

**Next**: Phase 2 will add personalization, context-awareness, and visual dashboard!
