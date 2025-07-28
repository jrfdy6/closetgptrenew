#!/usr/bin/env python3
"""
Test backend locally with Firebase environment variables
"""

import os
import sys
import subprocess
import time
import requests

def set_firebase_env():
    """Set Firebase environment variables"""
    firebase_env = {
        "FIREBASE_PROJECT_ID": "closetgptrenew",
        "FIREBASE_PRIVATE_KEY_ID": "3a500f42d1d3e7b1dbdfbb6feeea429a8e17fe60",
        "FIREBASE_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDl+u/+p1YK8u+5\nkJ/Tlpp6yKcuEA/Y7XlS5tGw/I3GY40bKF41tsnLkjMrFSQ9QJ5vNniQ2rNeyYfj\nnOfV7UXH3v2qUm00oCHf0DhXbNk48DdR/2TpXyJ4RA0f4rX4QMMNTFnYmGj5246F\nHhyC8upDM8G5LY+//QTVGeg4F6zcVIHk5SeYdXaifyxBa4nGI4AAnZelCgz/q6+K\nzrKcy4/XqDe9uT+g57o91+soJG0wfs9oSy2C0+Ib+guFtwFSvDUwLaXH21pJXGoh\nwEp93VRusRx0mpSOdh7V+/s17AM94MPWFJ7oX2woH77xZuHCcg2lkA3+seZJ5ewh\nTKS+R2mrAgMBAAECggEAAeS/b4QgZaKubdBOoJPC3dpWr6U0nDKh8+UwOmbTiM8I\nOf43fsKGH59dvUl4ebcIfVEgTDQ6YEA3vQLTt3Bmr+I0I6zeEIR1z72LjGmHBSL+\nyzWkUELKQ92h+Ts8O4XWlUtycFTnUfdVN99eZYc4F1zCIZL9Qs8DtSveos3/GSlM\n9/kppelT6+g6o5LrxK/XftDHH99LuGxDx7Xz74Eo3S0uxnS67T1cWost86oZbyM5\ne77X8syvih+4FLROG7sn/1NNX5Y7geZYB68FOVsYqjZ04ApO4pYIvjYUKv19RJLm\nPMB6s5lIKyWRWaUrbzL3RCmLnTXloal8Hr1qgHpOwQKBgQD0lgQqz8nYPF7XuLnD\nyvmLcVMz12Jo//HV2cIno8+qAJSwxDhg7XBbejVvoLzVSb+eTyaNHkMhiDbjiYTm\nGAE+v4JAZXmX1tJnPUi+tPCHNbaVVpNqYmtKiLp8Ji76YykH4Id+G2SUmf3oE/F2\nMFntK8XA4k/y2wjoJgCjQxmAcQKBgQDwtm5bKMzoZIlkwgYnVFnhdevpqZbBKs+T\n3ia1jHwyiaC9OwTdAeUPfFATtCqJFO2UpZuRYWsEUhLzyYiitUqOyW9JciFJsNqy\narSZ1tDlRYptQzsaL8f4DUr+pjLzADZ+1DD4JyDoDTarBaISxebBb1jsuoDdD0JE\nNQRxTmOZ2wKBgQDZnGOGx6sZZdUob6Vv6zaNdz2EwVxAeX/sObuB00BfS/b/MwXK\nT1cJPLkwYT3BMsV3D4sIQWWO/wd++IqywabR8kfsDZzamHpI+oCvlILwebzCL+4m\n1/wHq5DoBn0Dr5gA9yb1719Uy5HZm2zZL/nCh5CBpZlmRLUu/yjQGVImMQKBgFVt\nuW665TYY8DYFMh/lLNz6d9Z+rJUzt2XYMs695BofhB+Ega5aDMxZJyZHC82I0uSt\nfa+z7kIjSrygqtBsHODeFpPvYGcB0Cv/+MacWZj0/DLY6HHbwVGEjjggDfb1/WE3\nt4VqhaA1iFBb+HBHMiU2ek3RxwgtcSw50LDRzEF/AoGAVDCN6kR+7ubmoKFhzulp\nqjg9Cs6W+oPlW4mgr7XxuyhkX/2tN7rJMI6ZQtE4QQ2XR3Zp9Ed7GB3Q8GMgD5RL\nmL/8b9mT15IrQe5BNVAMig+d9oHYwhLxfs/2JWHjrYDH/o8ixTmRow3feJ73WXqm\n6v5dkz9cjHjJVh+pjCKD2/E=\n-----END PRIVATE KEY-----\n",
        "FIREBASE_CLIENT_EMAIL": "firebase-adminsdk-fbsvc@closetgptrenew.iam.gserviceaccount.com",
        "FIREBASE_CLIENT_ID": "110004373816846158464",
        "FIREBASE_CLIENT_X509_CERT_URL": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40closetgptrenew.iam.gserviceaccount.com"
    }
    
    for key, value in firebase_env.items():
        os.environ[key] = value
    
    print("✅ Firebase environment variables set")

def test_backend_local():
    """Test backend locally"""
    try:
        print("🔍 Starting backend locally...")
        
        # Set environment variables
        set_firebase_env()
        
        # Start the backend
        process = subprocess.Popen([
            "python3", "-m", "uvicorn", "src.app:app", 
            "--host", "0.0.0.0", "--port", "8080"
        ], env=os.environ.copy())
        
        # Wait for server to start
        time.sleep(5)
        
        print("🔍 Testing health endpoint...")
        response = requests.get("http://localhost:8080/health")
        print(f"Health status: {response.status_code}")
        print(f"Health response: {response.json()}")
        
        print("🔍 Testing outfits endpoint...")
        response = requests.get("http://localhost:8080/api/outfits/test")
        print(f"Outfits test status: {response.status_code}")
        print(f"Outfits test response: {response.text}")
        
        # Stop the server
        process.terminate()
        process.wait()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing backend locally: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing backend locally with Firebase environment variables...")
    test_backend_local() 