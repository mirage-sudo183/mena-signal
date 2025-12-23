# MENA Signal - TODO

## Known Issues

### 1. News Accuracy
The ingested news items are not accurately filtered for AI funding-specific content. The RSS feeds sometimes include general tech news, opinion pieces, and non-funding related articles.

**Potential fixes:**
- Add keyword filtering during ingestion (e.g., "raised", "funding", "series", "million", "investment")
- Implement a pre-filter using LLM to classify articles before storing
- Curate better RSS sources that are more funding-specific
- Add manual review/hide functionality for irrelevant items

### 2. AI Analysis Not Working
The MENA Fit Score analysis shows stub values (score: 50, generic summary) because the OpenAI API key is not configured.

**To fix:**
1. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```
2. Restart the backend services:
   ```bash
   docker-compose restart backend worker
   ```
3. New items will automatically get real LLM analysis
4. To re-analyze existing items, trigger a manual ingest or implement a re-analysis endpoint

---

## Future Improvements

- [ ] Better RSS source curation for funding-specific news
- [ ] Pre-filtering of articles by relevance
- [ ] Bulk re-analysis of items when API key is added
- [ ] More granular error handling for failed analyses
- [ ] Rate limiting for OpenAI API calls
- [ ] Caching of analysis results
- [ ] Export functionality for favorited items
- [ ] Email digest of high-scoring opportunities

