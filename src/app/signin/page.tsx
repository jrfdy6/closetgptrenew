"use client";
import { useState } from 'react';

export default function SignIn() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [testValue, setTestValue] = useState('Initial');

  console.log("SignIn component rendered - SIMPLE TEST");
  
  const handleTestClick = () => {
    console.log("Test button clicked!");
    setTestValue('Clicked at ' + new Date().toISOString());
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-950 dark:to-indigo-900 flex items-center justify-center">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-8 shadow-lg w-full max-w-md">
        <div style={{ color: 'red', fontWeight: 'bold', marginBottom: 16 }}>DEBUG: SignIn component rendered - SIMPLE TEST {Date.now()}</div>
        <div style={{ color: 'blue', marginBottom: 16 }}>Test Value: {testValue}</div>
        <button 
          onClick={handleTestClick}
          className="bg-green-500 text-white px-4 py-2 rounded mb-4"
        >
          Test Button (Click Me!)
        </button>
        
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {isSignUp ? "Create Account" : "Sign In"}
          </h1>
          <p className="text-gray-600 mt-2">
            {isSignUp ? "Join ClosetGPT today!" : "Welcome back to ClosetGPT"}
          </p>
        </div>

        <form className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              type="email"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your email"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input
              type="password"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your password"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold transition-colors"
          >
            {isSignUp ? "Create Account" : "Sign In"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsSignUp(!isSignUp)}
            className="text-blue-600 hover:text-blue-700 underline"
            type="button"
          >
            {isSignUp ? "Already have an account? Sign In" : "Don't have an account? Sign Up"}
          </button>
        </div>
        
        <div className="mt-6 text-center">
          <a href="/" className="text-gray-600 hover:text-gray-800">
            ← Back to Home
          </a>
        </div>
      </div>
    </div>
  );
} 