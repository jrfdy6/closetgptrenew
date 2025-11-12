# 🎨 ClosetGPT Apps SDK - MCP Implementation

Complete guide to building and deploying ClosetGPT as a native ChatGPT app using the Model Context Protocol (MCP).

## 📚 What We Built

Based on [OpenAI's Apps SDK documentation](https://developers.openai.com/apps-sdk/concepts/design-guidelines), we created:

1. **MCP Server** (`backend/mcp_server.py`) - Implements Model Context Protocol
2. **6 Core Tools** - Functions ChatGPT can call
3. **Native UI Components** - Cards, carousels matching Apps SDK guidelines
4. **Conversational Flow** - Integrated inline experiences

## 🎯 Design Philosophy

Following [Apps SDK design principles](https://developers.openai.com/apps-sdk/concepts/design-guidelines):

### ✅ **Conversational**
- Natural extension of ChatGPT conversation
- Actions happen inline without breaking flow
- "What should I wear?" feels native

### ✅ **Simple**
- Each interaction = single clear action
- Outfit cards show only essential info
- Max 2 CTAs per card

### ✅ **Visual**
- Inline carousels for browsing outfits
- Fullscreen mode for wardrobe exploration
- Image-first design

## 🛠️ Architecture

```
ChatGPT Conversation
    ↓
MCP Protocol
    ↓
ClosetGPT MCP Server (mcp_server.py)
    ↓
Your Main API (closetgptrenew-production.railway.app)
    ↓
Firebase/Firestore
```

## 📦 Tools (Functions)

### 1. **get_wardrobe**
```
User: "Show me all my jackets"
→ Returns: Inline carousel of jacket cards
```

**UI Component:** Inline carousel
- Each card shows image, name, color, wear count
- "View Details" CTA button
- Max 8 items per carousel

### 2. **suggest_outfits**
```
User: "What should I wear to a wedding?"
→ Returns: Inline carousel of complete outfit suggestions
```

**UI Component:** Inline carousel
- Each card shows outfit combination
- Occasion badge, style metadata
- "Wear This" CTA button
- Max 5 outfits

### 3. **add_wardrobe_item**
```
User: *uploads image* "Add this shirt"
→ Returns: Inline card with item preview and confirm button
```

**UI Component:** Inline card
- Shows analyzed item details
- Edit controls for metadata
- "Confirm & Add" primary action

### 4. **get_wardrobe_stats**
```
User: "How many items do I have?"
→ Returns: Inline card with stats
```

**UI Component:** Inline card
- Total items, most common type/color
- Total wears tracked
- No actions needed (informational)

### 5. **mark_outfit_worn**
```
User: Clicks "Wear This" on outfit card
→ Updates wear counts for all items
```

**Triggered by:** CTA button in outfit card
**Result:** Confirmation message + updated stats

### 6. **get_item_details**
```
User: Clicks "View Details" on item card
→ Opens fullscreen with item history
```

**UI Component:** Fullscreen display
- Item image, all metadata
- Wear history graph
- Outfit suggestions with this item
- ChatGPT composer stays overlaid

## 🚀 Setup & Installation

### Prerequisites

```bash
# Install MCP SDK
pip install mcp

# Or install all MCP dependencies
pip install -r requirements-mcp.txt
```

### Local Testing

```bash
cd backend

# Set environment variables
export MAIN_API_URL=https://closetgptrenew-production.railway.app
export API_KEY=your-api-key

# Run MCP server
python mcp_server.py
```

### Test with MCP Inspector

```bash
# Install MCP Inspector
npx @modelcontextprotocol/inspector python mcp_server.py
```

This opens a web UI to test your MCP tools locally.

## 🎨 UI Components

### Inline Card Structure

```json
{
  "type": "inline_card",
  "title": "Navy Blazer",
  "image": "https://...",
  "metadata": [
    {"label": "Type", "value": "Jacket"},
    {"label": "Color", "value": "Navy"},
    {"label": "Worn", "value": "12 times"}
  ],
  "badge": "Business Casual",
  "actions": [
    {
      "type": "primary",
      "label": "Wear This",
      "tool": "mark_outfit_worn",
      "params": {"outfit_id": "123"}
    }
  ]
}
```

### Inline Carousel Structure

```json
{
  "type": "inline_carousel",
  "cards": [
    {/* card 1 */},
    {/* card 2 */},
    {/* card 3 */}
  ]
}
```

**Design Rules (from [guidelines](https://developers.openai.com/apps-sdk/concepts/design-guidelines#inline-carousel)):**
- 3-8 items per carousel
- Single CTA per card
- Image + title + max 2 metadata lines
- Consistent visual hierarchy

## 🚢 Deployment

### Option 1: Railway (Recommended)

1. **Create new Railway service** for MCP server
2. **Set root directory:** `/backend`
3. **Start command:** `python mcp_server.py`
4. **Environment variables:**
   ```
   MAIN_API_URL=https://closetgptrenew-production.railway.app
   API_KEY=<your-api-key>
   ```

### Option 2: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements-mcp.txt .
RUN pip install -r requirements-mcp.txt
COPY mcp_server.py .
CMD ["python", "mcp_server.py"]
```

## 📝 Submit to Apps SDK

### 1. Prepare App Metadata

Create `app_metadata.json`:

```json
{
  "name": "ClosetGPT",
  "description": "AI-powered wardrobe management and outfit recommendations",
  "category": "lifestyle",
  "icon_url": "https://your-domain.com/icon.png",
  "privacy_policy_url": "https://easyoutfitapp.com/privacy",
  "terms_of_service_url": "https://easyoutfitapp.com/terms"
}
```

### 2. Deploy MCP Server

Ensure your MCP server is:
- ✅ Publicly accessible
- ✅ Responding to MCP protocol requests
- ✅ Returns proper UI components
- ✅ Handles authentication

### 3. Test Integration

Use MCP Inspector to verify:
- All tools are discoverable
- Tool calls return proper responses
- UI components render correctly

### 4. Submit App

Follow [deployment guide](https://developers.openai.com/apps-sdk/deploy):
1. Connect your MCP server URL
2. Provide app metadata
3. Submit for review
4. OpenAI reviews within 1-3 business days

## 🧪 Testing Examples

### Test 1: Get Wardrobe

```
User: "Show me my wardrobe"

Expected:
→ Tool called: get_wardrobe
→ Response: Inline carousel with items
→ UI: 3-8 item cards displayed
```

### Test 2: Outfit Suggestion

```
User: "What should I wear to work today?"

Expected:
→ Tool called: suggest_outfits
   params: {occasion: "work"}
→ Response: Inline carousel with 3 outfits
→ UI: 3 outfit cards with "Wear This" buttons
```

### Test 3: Add Item

```
User: *uploads image* "Add this to my wardrobe"

Expected:
→ Tool called: add_wardrobe_item
→ Response: Inline card with item preview
→ UI: Card with "Confirm & Add" button
```

## 📊 Monitoring & Analytics

Track key metrics:
- Tool call frequency (which tools are most used?)
- User engagement (CTA click rates)
- Error rates
- Response times

## 🔒 Security & Privacy

Per [security guidelines](https://developers.openai.com/apps-sdk/guides/security-privacy):

### Authentication
- OAuth 2.0 user authentication
- API keys for server-to-server
- No storing sensitive data in MCP responses

### Privacy
- User consent required before accessing wardrobe
- Clear privacy policy
- Data deletion on request

### Data Handling
- Images processed but not stored by OpenAI
- User wardrobe data stays in your Firebase
- MCP server only proxies requests

## 🐛 Troubleshooting

### MCP Server Won't Start

```bash
# Check MCP SDK is installed
pip list | grep mcp

# Check Python version (3.11+)
python --version

# Check environment variables
echo $MAIN_API_URL
```

### Tools Not Showing in ChatGPT

- Verify MCP server is running
- Check tool definitions are valid
- Ensure inputSchema matches MCP spec
- Test with MCP Inspector first

### UI Components Not Rendering

- Verify JSON structure matches spec
- Check image URLs are accessible
- Ensure card metadata has required fields
- Test response format with Inspector

### API Connection Fails

- Check MAIN_API_URL is correct
- Verify API_KEY is valid
- Test main API endpoints directly
- Check CORS settings if applicable

## 📚 Resources

- [Apps SDK Documentation](https://developers.openai.com/apps-sdk)
- [Design Guidelines](https://developers.openai.com/apps-sdk/concepts/design-guidelines)
- [MCP Server Guide](https://developers.openai.com/apps-sdk/build/mcp-server)
- [Security Best Practices](https://developers.openai.com/apps-sdk/guides/security-privacy)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## ✨ Next Steps

1. **Test Locally**
   - Run MCP server
   - Test with MCP Inspector
   - Verify all tools work

2. **Deploy**
   - Deploy to Railway/Docker
   - Configure environment variables
   - Test production endpoints

3. **Submit**
   - Create app metadata
   - Submit to Apps SDK
   - Wait for approval

4. **Launch**
   - Announce in GPT Store
   - Collect user feedback
   - Iterate on UX

---

## 🎉 Success Criteria

Your ClosetGPT app is ready when:
- ✅ All 6 tools respond correctly
- ✅ UI components render beautifully
- ✅ Follows Apps SDK design guidelines
- ✅ Conversational flow feels natural
- ✅ Authentication works smoothly
- ✅ Privacy policy is clear

**You're building something special!** 🚀

ClosetGPT is a **perfect use case** for the Apps SDK - it's conversational, visual, action-oriented, and adds real value to ChatGPT.

