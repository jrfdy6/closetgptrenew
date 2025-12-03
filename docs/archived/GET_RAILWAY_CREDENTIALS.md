# 🔑 How to Get Railway Credentials for Backfill

## 📋 Step-by-Step Instructions

### 1. Open Railway Dashboard
Go to: https://railway.app/dashboard

### 2. Select Your Project
Click on `closetgptrenew-backend` (or your backend project name)

### 3. Click on the Backend Service
Click on the main service (the one that's deployed)

### 4. Go to Variables Tab
Click on **"Variables"** in the top navigation

### 5. Find Firebase Credentials
Look for these variables:
- `FIREBASE_PROJECT_ID`
- `FIREBASE_PRIVATE_KEY`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_CLIENT_ID`
- `FIREBASE_CLIENT_X509_CERT_URL`

### 6. Copy Each Variable
For each variable above:
1. Click on the variable name
2. Click the **"Copy"** button (or manually select and copy the value)
3. Save it temporarily

### 7. Set Them in Terminal
Open your terminal and run these commands (replace with your actual values):

```bash
export FIREBASE_PROJECT_ID='your-actual-project-id'
export FIREBASE_PRIVATE_KEY='your-actual-private-key-with-newlines'
export FIREBASE_CLIENT_EMAIL='your-actual-client-email'
export FIREBASE_CLIENT_ID='your-actual-client-id'
export FIREBASE_CLIENT_X509_CERT_URL='your-actual-cert-url'
```

**IMPORTANT:** The `FIREBASE_PRIVATE_KEY` will have `\n` in it - that's correct, keep them!

### 8. Run the Backfill Script
```bash
cd /Users/johnniefields/Desktop/Cursor/closetgptrenew
source backend/venv/bin/activate
python3 RAILWAY_ENV_BACKFILL.py
```

### 9. Choose Option
- Type `1` for dry run (safe test)
- Type `2` for production run

---

## 🎯 Quick Example

Here's what your export commands might look like (with fake values):

```bash
export FIREBASE_PROJECT_ID='closetgpt-12345'
export FIREBASE_PRIVATE_KEY='-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg...\n-----END PRIVATE KEY-----\n'
export FIREBASE_CLIENT_EMAIL='firebase-adminsdk@closetgpt-12345.iam.gserviceaccount.com'
export FIREBASE_CLIENT_ID='123456789012345678901'
export FIREBASE_CLIENT_X509_CERT_URL='https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk%40closetgpt-12345.iam.gserviceaccount.com'
```

---

## ✅ Verification

After setting the variables, run:
```bash
echo $FIREBASE_PROJECT_ID
```

If it prints your project ID, you're good to go!

---

## 📞 Need Help?

If you can't find the variables in Railway:
1. Take a screenshot of your Railway Variables page
2. Send it to me
3. I'll help you identify them!

**Ready? Go get those credentials from Railway!** 🚀

