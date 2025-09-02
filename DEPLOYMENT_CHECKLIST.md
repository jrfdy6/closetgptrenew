# Production Deployment Checklist

## Pre-Deployment Checklist

### 1. Environment Variables
- [ ] `NEXT_PUBLIC_BACKEND_URL` matches production backend URL
- [ ] Firebase credentials are correct for production
- [ ] All required environment variables are set in Vercel

### 2. Database Schema
- [ ] Run database migration if field names changed
- [ ] Verify data structure matches between dev and production
- [ ] Test with production data structure

### 3. API Endpoints
- [ ] All API routes work with production backend
- [ ] CORS is configured for production domains
- [ ] Authentication works with production Firebase

### 4. Testing
- [ ] Test wardrobe page with production data
- [ ] Test outfit generation with production data
- [ ] Test image upload with production storage

## Post-Deployment Checklist

### 1. Verify Core Features
- [ ] Wardrobe page loads all items
- [ ] Outfit generation works
- [ ] User authentication works
- [ ] Image upload works

### 2. Check Logs
- [ ] No errors in Vercel logs
- [ ] No errors in Railway logs
- [ ] API calls are successful

### 3. User Experience
- [ ] Page loads quickly
- [ ] No console errors
- [ ] All features work as expected

## Common Issues and Solutions

### Issue: Only 1 item shows instead of 114
**Cause**: Field name mismatch between dev and production
**Solution**: Run database migration script

### Issue: CORS errors
**Cause**: Backend CORS not configured for production domain
**Solution**: Update CORS configuration in backend

### Issue: Authentication fails
**Cause**: Firebase configuration mismatch
**Solution**: Verify Firebase credentials and domain configuration

### Issue: Images don't load
**Cause**: Storage bucket configuration mismatch
**Solution**: Verify Firebase Storage configuration

## Emergency Rollback

If deployment fails:
1. Revert to previous working commit
2. Push to main branch
3. Wait for automatic redeployment
4. Verify functionality is restored

## Database Migration Commands

```bash
# Run database migration
cd backend
python migrate_wardrobe_fields.py

# Verify migration worked
# Check Railway logs for successful queries
```
