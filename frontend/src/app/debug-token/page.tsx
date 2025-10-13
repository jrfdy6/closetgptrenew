"use client";

import { getAuth } from "firebase/auth";
import { useState } from "react";

export default function DebugTokenPage() {
  const [token, setToken] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleGetToken() {
    try {
      setIsLoading(true);
      const user = getAuth().currentUser;
      
      if (!user) {
        alert("Not logged in yet! Please log in first.");
        return;
      }
      
      console.log("🔍 Getting Firebase token for user:", user.uid);
      const firebaseToken = await user.getIdToken(true);
      
      console.log("🔑 FIREBASE TOKEN:", firebaseToken);
      setToken(firebaseToken);
      
      // Also copy to clipboard if possible
      try {
        await navigator.clipboard.writeText(firebaseToken);
        alert("Token copied to clipboard and printed in console!");
      } catch {
        alert("Token printed in console! Copy it manually.");
      }
      
    } catch (error) {
      console.error("❌ Error getting token:", error);
      alert("Error getting token: " + error);
    } finally {
      setIsLoading(false);
    }
  }

  async function testBackendWithToken() {
    if (!token) {
      alert("Please get the token first!");
      return;
    }

    try {
      setIsLoading(true);
      console.log("🧪 Testing backend with token...");
      
      const response = await fetch('https://closetgptrenew-production.up.railway.app/api/wardrobe/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      console.log("📡 Backend response status:", response.status);
      console.log("📡 Backend response headers:", Object.fromEntries(response.headers.entries()));
      
      const responseText = await response.text();
      console.log("📡 Backend response body:", responseText);
      
      if (response.ok) {
        const data = JSON.parse(responseText);
        alert(`✅ Backend Success!\nStatus: ${response.status}\nItems: ${data.count || data.items?.length || 0}\nUser ID: ${data.user_id}`);
      } else {
        alert(`❌ Backend Error!\nStatus: ${response.status}\nResponse: ${responseText}`);
      }
      
    } catch (error) {
      console.error("❌ Error testing backend:", error);
      alert("Error testing backend: " + error);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <h1>🔑 Firebase Token Debug Page</h1>
      
      <div style={{ marginBottom: "2rem" }}>
        <h2>Step 1: Get Your Firebase Token</h2>
        <button 
          onClick={handleGetToken}
          disabled={isLoading}
          style={{
            padding: "1rem 2rem", 
            margin: "1rem 0", 
            fontSize: "1rem",
            backgroundColor: "#0070f3",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: isLoading ? "not-allowed" : "pointer"
          }}
        >
          {isLoading ? "Getting Token..." : "Get Firebase Token"}
        </button>
        
        {token && (
          <div style={{ marginTop: "1rem" }}>
            <p><strong>Token (first 50 chars):</strong> {token.substring(0, 50)}...</p>
          </div>
        )}
      </div>

      <div style={{ marginBottom: "2rem" }}>
        <h2>Step 2: Test Backend Directly</h2>
        <button 
          onClick={testBackendWithToken}
          disabled={isLoading || !token}
          style={{
            padding: "1rem 2rem", 
            margin: "1rem 0", 
            fontSize: "1rem",
            backgroundColor: "#28a745",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: (isLoading || !token) ? "not-allowed" : "pointer"
          }}
        >
          {isLoading ? "Testing..." : "Test Backend with Token"}
        </button>
      </div>

      <div style={{ marginTop: "2rem", padding: "1rem", backgroundColor: "#f5f5f5", borderRadius: "8px" }}>
        <h3>Instructions:</h3>
        <ol>
          <li>Make sure you're logged in with your Firebase account</li>
          <li>Click "Get Firebase Token" - it will be copied to clipboard and printed in console</li>
          <li>Click "Test Backend with Token" to see what the backend returns</li>
          <li>Check the browser console for detailed logs</li>
          <li>Share the results with me so I can help debug the proxy issue</li>
        </ol>
      </div>

      <div style={{ marginTop: "2rem", padding: "1rem", backgroundColor: "#fff3cd", borderRadius: "8px" }}>
        <h3>Expected Results:</h3>
        <ul>
          <li><strong>If backend returns 200:</strong> You should see your 155 wardrobe items</li>
          <li><strong>If backend returns 401:</strong> Token validation issue</li>
          <li><strong>If backend returns 403:</strong> Permission issue</li>
          <li><strong>If backend returns 500:</strong> Server error</li>
        </ul>
      </div>
    </div>
  );
}
