# 🚀 ClosetGPT Deployment Guide - Fresh Start

## **Backend Deployment Options**

### **Option A: Railway (Recommended)**

1. **Go to [railway.app](https://railway.app)**
2. **Sign in with GitHub**
3. **Click "New Project" → "Deploy from GitHub repo"**
4. **Select repository: `closetgptrenew`**
5. **Configure deployment:**
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn src.app:app --host 0.0.0.0 --port 3001`

6. **Set Environment Variables in Railway Dashboard:**
   ```
   FIREBASE_PROJECT_ID=closetgptrenew
   FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@closetgptrenew.iam.gserviceaccount.com
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDl+u/+p1YK8u+5\nkJ/Tlpp6yKcuEA/Y7XlS5tGw/I3GY40bKF41tsnLkjMrFSQ9QJ5vNniQ2rNeyYfj\nnOfV7UXH3v2qUm00oCHf0DhXbNk48DdR/2TpXyJ4RA0f4rX4QMMNTFnYmGj5246F\nHhyC8upDM8G5LY+//QTVGeg4F6zcVIHk5SeYdXaifyxBa4nGI4AAnZelCgz/q6+K\nzrKcy4/XqDe9uT+g57o91+soJG0wfs9oSy2C0+Ib+guFtwFSvDUwLaXH21pJXGoh\nwEp93VRusRx0mpSOdh7V+/s17AM94MPWFJ7oX2woH77xZuHCcg2lkA3+seZJ5ewh\nTKS+R2mrAgMBAAECggEAAeS/b4QgZaKubdBOoJPC3dpWr6U0nDKh8+UwOmbTiM8I\nOf43fsKGH59dvUl4ebcIfVEgTDQ6YEA3vQLTt3Bmr+I0I6zeEIR1z72LjGmHBSL+\nyzWkUELKQ92h+Ts8O4XWlUtycFTnUfdVN99eZYc4F1zCIZL9Qs8DtSveos3/GSlM\n9/kppelT6+g6o5LrxK/XftDHH99LuGxDx7Xz74Eo3S0uxnS67T1cWost86oZbyM5\ne77X8syvih+4FLROG7sn/1NNX5Y7geZYB68FOVsYqjZ04ApO4pYIvjYUKv19RJLm\nPMB6s5lIKyWRWaUrbzL3RCmLnTXloal8Hr1qgHpOwQKBgQD0lgQqz8nYPF7XuLnD\nyvmLcVMz12Jo//HV2cIno8+qAJSwxDhg7XBbejVvoLzVSb+eTyaNHkMhiDbjiYTm\nGAE+v4JAZXmX1tJnPUi+tPCHNbaVVpNqYmtKiLp8Ji76YykH4Id+G2SUmf3oE/F2\nMFntK8XA4k/y2wjoJgCjQxmAcQKBgQDwtm5bKMzoZIlkwgYnVFnhdevpqZbBKs+T\n3ia1jHwyiaC9OwTdAeUPfFATtCqJFO2UpZuRYWsEUhLzyYiitUqOyW9JciFJsNqy\narSZ1tDlRYptQzsaL8f4DUr+pjLzADZ+1DD4JyDoDTarBaISxebBb1jsuoDdD0JE\nNQRxTmOZ2wKBgQDZnGOGx6sZZdUob6Vv6zaNdz2EwVxAeX/sObuB00BfS/b/MwXK\nT1cJPLkwYT3BMsV3D4sIQWWO/wd++IqywabR8kfsDZzamHpI+oCvlILwebzCL+4m\n1/wHq5DoBn0Dr5gA9yb1719Uy5HZm2zZL/nCh5CBpZlmRLUu/yjQGVImMQKBgFVt\nuW665TYY8DYFMh/lLNz6d9Z+rJUzt2XYMs695BofhB+Ega5aDMxZJyZHC82I0uSt\nfa+z7kIjSrygqtBsHODeFpPvYGcB0Cv/+MacWZj0/DLY6HHbwVGEjjggDfb1/WE3\nt4VqhaA1iFBb+HBHMiU2ek3RxwgtcSw50LDRzEF/AoGAVDCN6kR+7ubmoKFhzulp\nqjg9Cs6W+oPlW4mgr7XxuyhkX/2tN7rJMI6ZQtE4QQ2XR3Zp9Ed7GB3Q8GMgD5RL\nmL/8b9mT15IrQe5BNVAMig+d9oHYwhLxfs/2JWHjrYDH/o8ixTmRow3feJ73WXqm\n6v5dkz9cjHjJVh+pjCKD2/E=\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_ID=110004373816846158464
   FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40closetgptrenew.iam.gserviceaccount.com
   ENVIRONMENT=production
   SECRET_KEY=your-super-secure-secret-key-here
   OPENAI_API_KEY=your_openai_api_key_here
   WEATHER_API_KEY=your_weather_api_key_here
   ```

### **Option B: Render (Alternative)**

1. **Go to [render.com](https://render.com)**
2. **Sign in with GitHub**
3. **Click "New +" → "Web Service"**
4. **Connect GitHub repository: `closetgptrenew`**
5. **Configure:**
   - **Name:** `closetgpt-backend`
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn src.app:app --host 0.0.0.0 --port 3001`

6. **Set Environment Variables in Render Dashboard**

## **Frontend Deployment: Vercel**

1. **Go to [vercel.com](https://vercel.com)**
2. **Sign in with GitHub**
3. **Click "New Project"**
4. **Import repository: `closetgptrenew`**
5. **Configure:**
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

6. **Set Environment Variables in Vercel Dashboard:**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.railway.app
   NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=closetgptrenew.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=closetgptrenew
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=closetgptrenew.appspot.com
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
   NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
   NEXT_PUBLIC_OPENAI_API_KEY=your_openai_api_key
   NODE_ENV=production
   ```

## **Testing Your Deployment**

1. **Test Backend:**
   ```bash
   curl https://your-backend-url.railway.app/health
   ```

2. **Test Frontend:**
   - Visit your Vercel URL
   - Test authentication
   - Test outfit generation

## **Troubleshooting**

- **Backend not starting:** Check Railway/Render logs
- **CORS errors:** Update `ALLOWED_ORIGINS` in backend
- **Environment variables:** Verify all are set correctly
- **Build errors:** Check requirements.txt and package.json 