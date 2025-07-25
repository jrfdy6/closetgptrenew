# 🔐 Security Implementation Guide

This document outlines the comprehensive security features implemented in the Wardrobe System.

## 🛡️ Security Components

### 1. **Image Sanitization** (`src/utils/image_sanitizer.py`)

**What it does:**
- Strips EXIF metadata (location, camera info, etc.)
- Validates file types and content
- Resizes images to prevent abuse
- Converts to safe formats
- Prevents malicious uploads

**Usage:**
```python
from src.utils.image_sanitizer import ImageSanitizer

sanitizer = ImageSanitizer()
result = sanitizer.sanitize_image("uploaded_image.jpg")
# Returns: sanitized image path and metadata
```

**Features:**
- ✅ EXIF data removal
- ✅ File type validation
- ✅ Size limits (50MB max)
- ✅ Format conversion to JPEG
- ✅ Malicious content detection

---

### 2. **Rate Limiting** (`src/middleware/rate_limiter.py`)

**What it does:**
- Prevents API abuse and DDoS attacks
- Different limits for different endpoints
- User-based and IP-based limiting
- Admin users get higher limits

**Configuration:**
```python
# Default limits (requests per minute)
{
    "default": 60,      # General endpoints
    "auth": 10,         # Authentication attempts
    "upload": 20,       # File uploads
    "outfit_generation": 30,  # AI outfit generation
    "analytics": 100,   # Analytics events
    "feedback": 50      # Feedback submissions
}
```

**Usage:**
```python
from src.middleware.rate_limiter import RateLimiter, create_rate_limit_middleware

# Add to FastAPI app
app.middleware("http")(create_rate_limit_middleware(rate_limiter))
```

---

### 3. **Field-Level Encryption** (`src/utils/encryption.py`)

**What it does:**
- Encrypts sensitive personal data
- Uses AES-256-GCM for authenticated encryption
- Unique keys per field and user
- Protects emails, photos, personal notes

**Encrypted Fields:**
- ✅ Email addresses
- ✅ Phone numbers
- ✅ Profile images
- ✅ Personal notes
- ✅ Address information

**Non-Encrypted Fields:**
- ❌ Wardrobe items (public data)
- ❌ Outfit combinations
- ❌ Analytics data
- ❌ Public preferences

**Usage:**
```python
from src.utils.encryption import encrypt_sensitive_data, decrypt_sensitive_data

# Encrypt user data
encrypted_data = encrypt_sensitive_data(user_data, user_id)

# Decrypt user data
decrypted_data = decrypt_sensitive_data(encrypted_data, user_id)
```

---

### 4. **Firestore Security Rules**

**Updated Rules:**
```javascript
// Users can only access their own data
match /users/{userId}/wardrobe/{itemId} {
  allow read, write: if request.auth != null && request.auth.uid == userId;
}

// Only admins can write to analytics
match /wardrobe_stats/{document} {
  allow read: if request.auth != null;
  allow write: if request.auth != null && request.auth.token.admin == true;
}
```

**Security Features:**
- ✅ User isolation (users can only access their own data)
- ✅ Admin-only analytics access
- ✅ Authentication required for all operations
- ✅ Deny by default

---

### 5. **Firebase Storage Rules**

**Updated Rules:**
```javascript
// Only authenticated users can access their own files
match /users/{userId}/{allPaths=**} {
  allow read, write: if request.auth != null && request.auth.uid == userId;
}

// Default deny all other access
match /{allPaths=**} {
  allow read, write: if false;
}
```

---

## 🚀 Quick Start

### 1. Install Security Dependencies

```bash
pip install -r requirements_security.txt
```

### 2. Set Environment Variables

```bash
# Create .env file
ENCRYPTION_MASTER_KEY=your-secure-master-key-here
FIREBASE_PROJECT_ID=your-project-id
```

### 3. Run Security Setup

```bash
python scripts/security_setup.py
```

### 4. Test Security Rules

```bash
# Start Firestore emulator
gcloud emulators firestore start

# Run security tests
python tests/test_firestore_rules.py
```

---

## 🔧 Integration with Existing App

### Add to Your FastAPI App

```python
from fastapi import FastAPI
from src.middleware.rate_limiter import RateLimiter, create_rate_limit_middleware
from src.utils.image_sanitizer import sanitize_uploaded_image
from src.utils.encryption import encrypt_sensitive_data

app = FastAPI()

# Add rate limiting
rate_limiter = RateLimiter()
app.middleware("http")(create_rate_limit_middleware(rate_limiter))

# Use in upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile, user_id: str):
    # Sanitize image
    result = sanitize_uploaded_image(file, "uploads/")
    
    # Encrypt sensitive metadata
    encrypted_metadata = encrypt_sensitive_data({
        "original_filename": file.filename,
        "user_notes": "Personal notes"
    }, user_id)
    
    return {"status": "success", "file_id": result["file_hash"]}
```

---

## 🧪 Testing Security Features

### 1. Image Sanitization Test

```python
# Test image sanitization
python -c "
from src.utils.image_sanitizer import ImageSanitizer
sanitizer = ImageSanitizer()
result = sanitizer.sanitize_image('test_image.jpg')
print(f'Sanitized: {result}')
"
```

### 2. Rate Limiting Test

```bash
# Test rate limiting (should get 429 after 60 requests)
for i in {1..70}; do
  curl http://localhost:8000/api/test
done
```

### 3. Encryption Test

```python
# Test encryption
python -c "
from src.utils.encryption import encrypt_sensitive_data, decrypt_sensitive_data
data = {'email': 'test@example.com'}
encrypted = encrypt_sensitive_data(data, 'user123')
decrypted = decrypt_sensitive_data(encrypted, 'user123')
print(f'Original: {data}')
print(f'Decrypted: {decrypted}')
"
```

---

## 📊 Security Audit

Run a comprehensive security audit:

```bash
python scripts/security_setup.py
```

This will:
- ✅ Test all security components
- ✅ Validate Firestore rules
- ✅ Check encryption functionality
- ✅ Verify rate limiting
- ✅ Generate security report

---

## 🔒 Security Best Practices

### 1. **Environment Variables**
- Store encryption keys securely
- Use different keys for development/production
- Rotate keys regularly

### 2. **File Uploads**
- Always sanitize uploaded images
- Validate file types server-side
- Store files in secure locations

### 3. **API Security**
- Use rate limiting on all endpoints
- Validate all inputs
- Log security events

### 4. **Data Protection**
- Encrypt sensitive personal data
- Use least privilege access
- Regular security audits

---

## 🚨 Security Monitoring

### Logs to Monitor

```bash
# Rate limiting violations
grep "Rate limit exceeded" logs/app.log

# Failed authentication attempts
grep "Authentication failed" logs/app.log

# Image sanitization issues
grep "Image sanitization failed" logs/app.log
```

### Metrics to Track

- Rate limit violations per user
- Failed authentication attempts
- Image upload success/failure rates
- Encryption/decryption errors

---

## 🔧 Troubleshooting

### Common Issues

1. **Rate Limiting Not Working**
   - Check Redis connection (if using Redis backend)
   - Verify middleware is added to FastAPI app

2. **Image Sanitization Fails**
   - Install Pillow: `pip install Pillow`
   - Check file permissions for temp directory

3. **Encryption Errors**
   - Verify ENCRYPTION_MASTER_KEY is set
   - Check key format (base64 encoded)

4. **Firestore Rules Issues**
   - Test with Firestore emulator
   - Check rule syntax in Firebase console

---

## 📞 Support

For security-related issues:

1. Check the logs for detailed error messages
2. Run the security audit: `python scripts/security_setup.py`
3. Test individual components using the test scripts
4. Review this documentation for configuration details

---

## 🔄 Updates

To update security components:

```bash
# Update dependencies
pip install -r requirements_security.txt --upgrade

# Re-run security audit
python scripts/security_setup.py

# Test all components
python tests/test_firestore_rules.py
```

---

**Remember:** Security is an ongoing process. Regularly review and update your security measures! 