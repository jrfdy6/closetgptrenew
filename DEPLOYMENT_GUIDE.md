# ClosetGPT Deployment & Testing Guide

## 🚀 Current Status

✅ **Backend**: Running on http://127.0.0.1:3001  
✅ **Frontend**: Running on http://localhost:3000  
✅ **Health Check**: Backend health endpoint responding  
✅ **Dependencies**: All packages installed and working  

---

## 🧪 Testing & Debugging Setup

### 1. Backend API Testing

#### Health & Monitoring Endpoints
```bash
# Health check
curl http://127.0.0.1:3001/health

# Metrics
curl http://127.0.0.1:3001/metrics

# System status
curl http://127.0.0.1:3001/ready

# Performance test
curl http://127.0.0.1:3001/api/performance/test
```

#### Authentication Testing
```bash
# Test auth endpoints
curl -X POST http://127.0.0.1:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://127.0.0.1:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

#### Wardrobe Management Testing
```bash
# Get wardrobe items (requires auth token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:3001/api/wardrobe/items

# Add wardrobe item
curl -X POST http://127.0.0.1:3001/api/wardrobe/items \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Blue Jeans",
    "category": "bottoms",
    "subcategory": "jeans",
    "color": "blue",
    "style": "casual",
    "season": "all",
    "image_url": "https://example.com/jeans.jpg"
  }'
```

#### Outfit Generation Testing
```bash
# Generate outfit
curl -X POST http://127.0.0.1:3001/api/outfit/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "occasion": "casual",
    "weather": "sunny",
    "temperature": 75,
    "preferences": ["comfortable", "stylish"]
  }'
```

### 2. Frontend Testing

#### Manual Testing Checklist
- [ ] **Homepage**: Loads correctly at http://localhost:3000
- [ ] **Authentication**: Sign up, login, logout flows
- [ ] **Wardrobe**: Add, edit, delete clothing items
- [ ] **Outfit Generation**: Generate outfits with different parameters
- [ ] **Style Quiz**: Complete style preference quiz
- [ ] **Analytics**: View analytics dashboard
- [ ] **Responsive Design**: Test on mobile/tablet

#### Browser Developer Tools
```javascript
// Test API calls from browser console
fetch('http://127.0.0.1:3001/health')
  .then(response => response.json())
  .then(data => console.log(data));

// Test with auth token
fetch('http://127.0.0.1:3001/api/wardrobe/items', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### 3. Automated Testing

#### Backend Tests
```bash
cd backend
pytest tests/ -v
```

#### Frontend Tests
```bash
cd frontend
npm test
```

#### E2E Tests
```bash
cd frontend
npm run cypress:open
```

---

## 🔧 Development Workflow

### 1. Starting Development Environment
```bash
# Terminal 1: Backend
cd backend
source ../.venv/bin/activate
python -m uvicorn src.app:app --host 127.0.0.1 --port 3001 --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 2. Environment Variables
Create `.env.local` in frontend directory:
```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:3001
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
```

### 3. Database Management
```bash
# View Firestore data
cd backend
python scripts/printWardrobeMetadata.py

# Seed test data
python scripts/seed_production_data.py

# Clear test data
python scripts/clear_wardrobe.py
```

---

## 🐛 Debugging Guide

### 1. Backend Debugging

#### Logs
```bash
# View structured logs
tail -f logs/backend.log

# View uvicorn logs
# (logs appear in terminal where uvicorn is running)
```

#### Common Issues
- **Import Errors**: Check Python path and virtual environment
- **Firebase Connection**: Verify credentials and project ID
- **CORS Issues**: Check CORS configuration in backend
- **Authentication**: Verify JWT tokens and Firebase Auth setup

### 2. Frontend Debugging

#### React DevTools
- Install React Developer Tools browser extension
- Use Components tab to inspect component state
- Use Profiler tab to analyze performance

#### Network Tab
- Check API calls in browser Network tab
- Verify request/response headers and payloads
- Look for CORS or authentication errors

#### Console Errors
```javascript
// Enable detailed error logging
localStorage.setItem('debug', '*');

// Check for specific errors
console.error('API Error:', error);
```

### 3. Database Debugging

#### Firestore Console
- Visit https://console.firebase.google.com
- Navigate to Firestore Database
- Check collections and documents
- Monitor real-time updates

#### Firebase CLI
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login and view data
firebase login
firebase firestore:get /users
```

---

## 📊 Monitoring & Analytics

### 1. Application Metrics
- **Response Times**: Monitor API endpoint performance
- **Error Rates**: Track 4xx and 5xx errors
- **User Activity**: Monitor user engagement
- **Resource Usage**: CPU, memory, database connections

### 2. Business Metrics
- **User Registration**: New user signups
- **Wardrobe Growth**: Items added per user
- **Outfit Generation**: Successful outfit recommendations
- **Feature Usage**: Most/least used features

### 3. Error Tracking
```python
# Backend error logging
logger.error("User action failed", extra={
    "user_id": user_id,
    "action": "outfit_generation",
    "error": str(error)
})

# Frontend error tracking
console.error("Frontend error:", {
    component: "OutfitGenerator",
    action: "generate_outfit",
    error: error.message
});
```

---

## 🚀 Production Deployment Checklist

### 1. Environment Setup
- [ ] Production Firebase project configured
- [ ] Environment variables set for production
- [ ] SSL certificates configured
- [ ] Domain and DNS configured

### 2. Security
- [ ] CORS origins restricted to production domain
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] Authentication properly configured

### 3. Performance
- [ ] CDN configured for static assets
- [ ] Database indexes optimized
- [ ] Caching strategies implemented
- [ ] Image optimization enabled

### 4. Monitoring
- [ ] Error tracking service configured (Sentry)
- [ ] Performance monitoring enabled
- [ ] Health checks implemented
- [ ] Backup strategies configured

---

## 🎯 Next Steps for Testing

1. **Manual Testing**: Go through all user flows manually
2. **API Testing**: Test all endpoints with various inputs
3. **Performance Testing**: Load test critical endpoints
4. **Security Testing**: Test authentication and authorization
5. **Cross-browser Testing**: Test on different browsers
6. **Mobile Testing**: Test responsive design on mobile devices

---

## 📞 Support & Troubleshooting

### Common Issues & Solutions

#### Backend Won't Start
```bash
# Check Python environment
which python
pip list | grep fastapi

# Check port availability
lsof -i :3001

# Check logs
tail -f logs/backend.log
```

#### Frontend Won't Start
```bash
# Check Node.js version
node --version

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### Database Connection Issues
```bash
# Check Firebase credentials
cat backend/firebase-credentials.json

# Test Firestore connection
python -c "from src.config.firebase import db; print('Connected')"
```

#### CORS Issues
```bash
# Check CORS configuration
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS http://127.0.0.1:3001/api/auth/login
```

---

Your ClosetGPT application is now ready for comprehensive testing and debugging! Both servers are running and all endpoints are accessible. Use this guide to systematically test all features and identify any issues before production deployment. 