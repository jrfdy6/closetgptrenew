# ChatGPT Plugin Setup - AI Clone Backend

## ✅ Implementation Complete

All required endpoints and infrastructure for the ChatGPT plugin have been implemented.

## 📁 Files Created

### Plugin Manifest & API Spec
- **`.well-known/ai-plugin.json`** - ChatGPT plugin manifest
- **`openapi.json`** - OpenAPI 3.1.0 specification
- **`static/logo.png`** - Placeholder logo (needs to be replaced)

### Routes Implemented
- **`backend/src/routes/rag_ingest.py`** - Enhanced ingestion with chunking and embeddings
- **`backend/src/routes/knowledge.py`** - RAG retrieval and knowledge endpoints

### Configuration
- **`backend/app.py`** - Updated with:
  - CORS middleware for ChatGPT origins
  - Static file serving
  - Routes for plugin manifest and OpenAPI spec
  - Router mounting for new endpoints

## 🔌 Endpoints

### 1. `/api/ingest_drive` (POST)
**Description**: Ingest Google Drive folders with full RAG pipeline
- Downloads files from Google Drive
- Extracts text from PDFs and Google Docs
- Chunks text into manageable pieces (1000 chars, 200 char overlap)
- Generates embeddings using OpenAI `text-embedding-ada-002`
- Stores chunks with embeddings in Firestore `knowledge_chunks` collection

**Request Body**:
```json
{
  "user_id": "string",
  "folder_id": "string",
  "max_files": 10
}
```

**Response**:
```json
{
  "accepted": true,
  "message": "Ingestion started in background...",
  "user_id": "string",
  "folder_id": "string",
  "max_files": 10,
  "status": "pending"
}
```

**Status**: Returns 202 immediately, processing happens in background

### 2. `/api/chat` (POST)
**Description**: RAG retrieval using vector search
- Generates embedding for query
- Searches Firestore `knowledge_chunks` collection
- Uses cosine similarity to find most relevant chunks
- Returns top N chunks with similarity scores

**Request Body**:
```json
{
  "query": "string",
  "limit": 5
}
```

**Response**:
```json
{
  "chunks": [
    {
      "chunk_id": "string",
      "text": "string",
      "metadata": {},
      "similarity": 0.85
    }
  ],
  "query": "string",
  "count": 5
}
```

### 3. `/api/knowledge/search` (GET)
**Description**: Keyword-based search of knowledge chunks

**Query Parameters**:
- `query` (required): Search query string
- `limit` (optional, default: 10): Maximum results

**Response**:
```json
{
  "chunks": [
    {
      "chunk_id": "string",
      "text": "string",
      "metadata": {},
      "similarity": 0.5
    }
  ],
  "query": "string",
  "count": 10
}
```

### 4. `/api/knowledge/get` (GET)
**Description**: Get a specific chunk by ID

**Query Parameters**:
- `chunk_id` (required): Chunk ID to retrieve

**Response**:
```json
{
  "chunk_id": "string",
  "text": "string",
  "metadata": {},
  "embedding_available": true
}
```

## 🔧 Configuration

### Environment Variables Required

1. **Firebase**:
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_PRIVATE_KEY`
   - `FIREBASE_CLIENT_EMAIL`
   - `FIREBASE_CLIENT_ID`
   - `FIREBASE_CLIENT_X509_CERT_URL`

2. **OpenAI** (for embeddings):
   - `OPENAI_API_KEY`

3. **Google Drive** (for ingestion):
   - `GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE` (recommended)
   - OR `GOOGLE_APPLICATION_CREDENTIALS`

### CORS Origins Added
- `https://aiclone-production-32dc.up.railway.app`
- `https://chat.openai.com`
- `http://localhost:3000`

## 📊 Firestore Collections

### `knowledge_chunks`
Stores chunked and embedded documents:
```json
{
  "user_id": "string",
  "file_id": "string",
  "file_name": "string",
  "folder_id": "string",
  "text": "string",
  "chunk_index": 0,
  "mime_type": "string",
  "embedding": [0.123, ...],  // 1536-dimensional vector
  "metadata": {
    "total_chunks": 5,
    "chunk_size": 1000,
    "file_name": "document.pdf"
  },
  "created_at": 1234567890.0,
  "updated_at": 1234567890.0
}
```

### `ingest_jobs`
Tracks ingestion job status:
```json
{
  "user_id": "string",
  "folder_id": "string",
  "status": "completed|failed|started",
  "details": {
    "processed": 10,
    "skipped": 2,
    "total_chunks": 45,
    "errors": []
  },
  "ts": 1234567890.0
}
```

## 🧪 Testing in ChatGPT

1. **Install the Plugin**:
   - Use manifest URL: `https://aiclone-production-32dc.up.railway.app/.well-known/ai-plugin.json`

2. **Test Ingestion**:
   ```
   Ingest the folder 1sZQZ9r3kfxgSR5A7HOFtU159B-HhvJRH for user dev-user
   ```

3. **Test Search**:
   ```
   Search my knowledge for "Jumpstart framework"
   ```

4. **Test Retrieval**:
   ```
   Summarize the core steps from the retrieved documents
   ```

## 📝 Next Steps

1. **Replace Logo**: 
   - Replace `static/logo.png` with your actual logo (512x512px PNG)
   - See `static/LOGO_INSTRUCTIONS.md` for details

2. **Update Contact Info**:
   - Update `contact_email` in `.well-known/ai-plugin.json`
   - Update `legal_info_url` if needed

3. **Deploy**:
   - Push to your repository
   - Ensure environment variables are set on Railway
   - Verify endpoints are accessible

4. **Test**:
   - Verify all endpoints respond correctly
   - Test with actual Google Drive folders
   - Verify embeddings are generated and stored
   - Test RAG retrieval with various queries

## 🔍 Troubleshooting

### Embeddings Not Generating
- Check `OPENAI_API_KEY` is set
- Verify API key is valid and has credits
- Check logs for OpenAI API errors

### Ingestion Not Working
- Verify Google Drive service account credentials
- Check folder permissions (service account needs access)
- Review `ingest_jobs` collection for error details

### Retrieval Returning Empty Results
- Verify chunks were stored in `knowledge_chunks` collection
- Check if embeddings were generated (should have `embedding` field)
- Try keyword search first to verify chunks exist

## 📚 Additional Resources

- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [ChatGPT Plugin Documentation](https://platform.openai.com/docs/guides/plugins)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)

