# 🧪 Frontend Click Tracking - Test Checklist

## Prerequisites

- ✅ Backend running on http://127.0.0.1:8001
- ✅ Frontend running via Streamlit

## Test 1: User Session Initialization

**What to Check:**

- [ ] Open frontend in browser
- [ ] Check Analytics tab → Session Info
- [ ] Verify User ID is generated (format: `user_xxxxxxxx`)
- [ ] Verify Session ID is generated (format: `session_xxxxxxxxx`)

**Expected:** Unique IDs displayed in Analytics tab

---

## Test 2: Search with Query Analysis

**Steps:**

1. Go to "Smart Search" tab
2. Search for: "romantic comedy"
3. Look at results section

**What to Check:**

- [ ] See 3 info boxes above results:
  - 🧠 Query Intent (should show "Emotion Based")
  - ⚖️ Search Weight (should show high % for Semantic)
  - 👤 User ID (partial ID shown)

**Expected:** Query analysis displayed correctly

---

## Test 3: Click Tracking (View Button)

**Steps:**

1. From search results, click "👁️ View" on first drama
2. Watch for success message

**What to Check:**

- [ ] Green success message appears: "✅ Clicked: [Drama Name]"
- [ ] No errors in console
- [ ] Go to Analytics tab → Popular Dramas
- [ ] Verify the clicked drama appears in popular list

**Expected:** Click tracked and visible in analytics

---

## Test 4: Watchlist Add

**Steps:**

1. From search results, click "➕ Watchlist" on second drama
2. Watch for state change

**What to Check:**

- [ ] Success message: "✅ Added to watchlist: [Drama Name]"
- [ ] Button changes to "✓ In List" (green/primary style)
- [ ] Go to Analytics tab → Your Watchlist
- [ ] Verify drama appears in watchlist section

**Expected:** Drama saved to watchlist and displayed

---

## Test 5: Watchlist Remove

**Steps:**

1. Click "✓ In List" button on a drama in watchlist
2. OR go to Analytics tab and click 🗑️ next to watchlist item

**What to Check:**

- [ ] Drama removed from watchlist
- [ ] Button reverts to "➕ Watchlist"
- [ ] Analytics tab updates to show reduced count

**Expected:** Drama removed successfully

---

## Test 6: Similar Drama Search

**Steps:**

1. From search results, click "🔄 Similar" on any drama
2. Watch page behavior

**What to Check:**

- [ ] Page triggers new search automatically
- [ ] Search uses clicked drama title as query
- [ ] New results appear
- [ ] Can see similar dramas

**Expected:** Similar search triggered correctly

---

## Test 7: Analytics Dashboard

**Steps:**

1. Go to "📈 Analytics" tab
2. Review all sections

**What to Check:**

- [ ] **Session Info**: Shows User ID, Session ID, Watchlist count
- [ ] **Your Watchlist**: Lists saved dramas (if any)
- [ ] **Most Popular Dramas**: Shows dramas with scores and clicks
- [ ] **Trending Searches**: Shows recent queries with intent types
- [ ] **Overall Platform Stats**: Shows totals (searches, clicks, CTR, users)

**Expected:** All analytics sections populated with data

---

## Test 8: Backend Data Verification

**Steps:**

1. Open PowerShell in backend directory
2. Run verification commands

**Commands:**

```powershell
# View last 5 interactions
Get-Content analytics_data\interactions.jsonl | Select-Object -Last 5

# View last 5 searches
Get-Content analytics_data\search_log.jsonl | Select-Object -Last 5

# View user stats (pretty print)
Get-Content analytics_data\user_stats.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**What to Check:**

- [ ] `interactions.jsonl` contains your clicks and watchlist actions
- [ ] `search_log.jsonl` contains your searches with intents
- [ ] `user_stats.json` shows aggregated stats for your user_id

**Expected:** All backend files updated correctly

---

## Test 9: Multiple Users Simulation

**Steps:**

1. Open frontend in incognito/private window
2. Perform a search and click
3. Go to Analytics tab in both windows

**What to Check:**

- [ ] Each window has different User ID
- [ ] Each window has separate Session ID
- [ ] Each window has independent watchlist
- [ ] Popular Dramas aggregates clicks from both sessions
- [ ] Platform stats show "Unique Users: 2"

**Expected:** Independent sessions tracked separately

---

## Test 10: Session Persistence

**Steps:**

1. Add 3 dramas to watchlist
2. Navigate between tabs (Smart Search ↔ Analytics)
3. Perform new search
4. Check watchlist again

**What to Check:**

- [ ] Watchlist items persist across tab changes
- [ ] User ID remains same
- [ ] Session ID remains same
- [ ] All interactions linked to same session

**Expected:** Session state maintained during browsing

---

## 🐛 Common Issues & Solutions

### Issue: "No analytics data showing"

**Solution:**

- Verify backend is running
- Check browser console for API errors
- Verify `analytics_data/` folder exists in backend

### Issue: "Watchlist not saving"

**Solution:**

- Check session state initialization
- Look for JavaScript errors
- Verify `st.rerun()` is working

### Issue: "Buttons not responding"

**Solution:**

- Check Streamlit version (requires recent version)
- Clear browser cache
- Restart Streamlit server

### Issue: "Duplicate key error"

**Solution:**

- Each button has unique key with drama title
- Ensure drama titles don't have special characters breaking keys

---

## ✅ Success Criteria

**All Tests Pass If:**

- ✅ User sessions tracked with unique IDs
- ✅ Clicks logged with position tracking
- ✅ Watchlist add/remove works smoothly
- ✅ Query analysis displays correctly
- ✅ Analytics tab shows real data
- ✅ Backend files updated correctly
- ✅ Multiple users tracked independently
- ✅ No console errors or crashes

---

## 📊 Expected Test Results

After completing all tests, you should see in Analytics:

**Your Watchlist:**

- 2-3 dramas (from Test 4)

**Popular Dramas:**

- Multiple dramas with scores 1-4
- Click counts matching your actions

**Trending Searches:**

- "romantic comedy" with intent: emotion_based
- Other queries you tested

**Platform Stats:**

- Total Searches: 5-10
- Total Clicks: 10-15
- Average CTR: 30-50%
- Unique Users: 1 (or 2 if incognito tested)

---

## 🚀 Next Steps After Testing

If all tests pass:

1. ✅ **Phase 1 Complete!** - Both backend and frontend integrated
2. 📝 Document any bugs found
3. 🎯 Ready for Phase 2 planning
4. 🌟 Optional: Add more UI polish (animations, better error handling)

If tests fail:

1. 🐛 Debug using browser console
2. 📋 Check backend logs for errors
3. 🔍 Verify API endpoints responding
4. 💬 Report issues for troubleshooting
