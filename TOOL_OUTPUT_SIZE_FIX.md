# MongoDB Hybrid Search Tool Output Size Fix

## Problem
The Azure AI Agents service has a 512KB limit for tool outputs. The MongoDB hybrid search was returning results that exceeded this limit, causing this error:

```
'tool_outputs' too large: the combined tool outputs must be less than 512kb.
```

## Root Causes
1. **Large document sizes**: MongoDB documents contained full content, embeddings, and other large fields
2. **Too many results**: Returning many documents increased total output size
3. **No field filtering**: Returning entire documents instead of just relevant fields

## Solution Implemented

### 1. Field Projection
- Added `include_fields` parameter to specify which fields to include
- Default fields: `["_id", "content"]`

### 2. Result Limits
- Reduced default limit from 20 to 3 results
- Maximum limit enforced at 5 results
- Reduced `numCandidates` from 100 to 50

### 3. Text Truncation
- Truncate text fields longer than 500 characters
- More aggressive truncation (200 chars) if size still too large

### 4. Size Estimation and Dynamic Truncation
- Added `_estimate_size_and_truncate()` method
- Monitors output size and further reduces if needed
- Falls back to minimal fields if estimation fails

### 5. Optimized Pipeline
- Disabled `scoreDetails` in `$rankFusion` to reduce output
- Added proper field projection in both hybrid and fallback searches

## Usage
The function now automatically handles size limits:

```python
# Returns up to 3 results with default fields
results = await searcher.async_hybrid_search_mongodb_atlas("search query")

# Custom limits and fields
results = await searcher.async_hybrid_search_mongodb_atlas(
    "search query", 
    limit=2, 
    include_fields=["_id", "content"]
)
```

## Size Safeguards
- Default 400KB limit (80% of 512KB for safety buffer)
- Progressive truncation if over limit
- Fallback to minimal results if all else fails
