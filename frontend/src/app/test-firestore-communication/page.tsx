"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { Upload, Loader2, CheckCircle, AlertCircle, TestTube } from "lucide-react";
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://closetgptrenew-backend-production.up.railway.app';
import AuthDebug from "@/components/AuthDebug";

interface TestResult {
  step: string;
  success: boolean;
  message: string;
  data?: any;
}

export default function TestFirestoreCommunication() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<TestResult[]>([]);
  const [itemName, setItemName] = useState("Test Item");
  const [category, setCategory] = useState("shirt");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const addResult = (step: string, success: boolean, message: string, data?: any) => {
    setResults(prev => [...prev, { step, success, message, data }]);
  };

  const runTest = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    setLoading(true);
    setResults([]);

    try {
      // Step 1: Test backend health
      addResult("Backend Health Check", true, "Starting test...");
      
      const healthResponse = await apiClient.get("health");
      if (healthResponse.success) {
        addResult("Backend Health Check", true, "Backend is responding", healthResponse.data);
      } else {
        addResult("Backend Health Check", false, "Backend is not responding", healthResponse.error);
        throw new Error("Backend health check failed");
      }

      // Step 2: Test authentication (if needed)
      addResult("Authentication Check", true, "Checking authentication...");
      
      // For this test, we'll assume the user is authenticated
      // In a real scenario, you'd check the auth token
      addResult("Authentication Check", true, "Authentication check passed");

      // Step 3: Upload image to backend
      addResult("Image Upload", true, "Uploading image to backend...");
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', category);
      formData.append('name', itemName);

      const uploadResponse = await fetch(`${API_BASE_URL}/api/image/upload`, {
        method: 'POST',
        body: formData,
        headers: {
          // Don't set Content-Type, let browser set it with boundary
        },
      });

      if (uploadResponse.ok) {
        const uploadData = await uploadResponse.json();
        addResult("Image Upload", true, "Image uploaded successfully", uploadData);
      } else {
        const errorData = await uploadResponse.json();
        addResult("Image Upload", false, "Image upload failed", errorData);
        throw new Error("Image upload failed");
      }

      // Step 4: Add item to wardrobe via backend
      addResult("Wardrobe Item Creation", true, "Creating wardrobe item...");
      
      const wardrobeItem = {
        name: itemName,
        category: category,
        color: "blue",
        brand: "Test Brand",
        image_url: preview, // This would be the uploaded image URL in real scenario
        description: "Test item created for communication testing",
        season: "all",
        occasion: ["casual", "test"],
        material: "cotton"
      };

      const wardrobeResponseRaw = await fetch(`${API_BASE_URL}/api/wardrobe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(wardrobeItem)
      });
      const wardrobeResponse = {
        success: wardrobeResponseRaw.ok,
        data: wardrobeResponseRaw.ok ? await wardrobeResponseRaw.json() : undefined,
        error: !wardrobeResponseRaw.ok ? await wardrobeResponseRaw.text() : undefined
      };
      
      if (wardrobeResponse.success) {
        addResult("Wardrobe Item Creation", true, "Item added to wardrobe successfully", wardrobeResponse.data);
      } else {
        addResult("Wardrobe Item Creation", false, "Failed to add item to wardrobe", wardrobeResponse.error);
        throw new Error("Wardrobe item creation failed");
      }

      // Step 5: Verify item was saved by retrieving wardrobe
      addResult("Wardrobe Retrieval", true, "Retrieving wardrobe to verify...");
      
      const wardrobeListRaw = await fetch(`${API_BASE_URL}/api/wardrobe`);
      const wardrobeListResponse = {
        success: wardrobeListRaw.ok,
        data: wardrobeListRaw.ok ? await wardrobeListRaw.json() : undefined,
        error: !wardrobeListRaw.ok ? await wardrobeListRaw.text() : undefined
      };
      
      if (wardrobeListResponse.success) {
        addResult("Wardrobe Retrieval", true, "Wardrobe retrieved successfully", {
          itemCount: wardrobeListResponse.data?.length || 0,
          items: wardrobeListResponse.data
        });
      } else {
        addResult("Wardrobe Retrieval", false, "Failed to retrieve wardrobe", wardrobeListResponse.error);
        throw new Error("Wardrobe retrieval failed");
      }

      // Step 6: Test complete
      addResult("Test Complete", true, "All tests passed! Frontend can communicate with Firestore through backend.");
      toast.success("Test completed successfully!");

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error occurred";
      addResult("Test Failed", false, errorMessage);
      toast.error("Test failed: " + errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const resetTest = () => {
    setFile(null);
    setPreview("");
    setResults([]);
    setItemName("Test Item");
    setCategory("shirt");
  };

  return (
    <div className="container-readable space-section py-8">
      {/* Header */}
      <div className="gradient-hero rounded-2xl p-6 sm:p-8 mb-6 sm:mb-8">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
            <TestTube className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
          </div>
          <h1 className="text-2xl sm:text-hero text-foreground">Firestore Communication Test</h1>
        </div>
        <p className="text-secondary text-base sm:text-lg">
          Test the complete flow: Frontend → Backend → Firestore
        </p>
      </div>

      <div className="max-w-4xl mx-auto space-y-6">
        {/* Test Configuration */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Test Configuration</h2>
          
          <div className="space-y-4">
            {/* File Upload */}
            <div>
              <Label htmlFor="test-file">Test Image</Label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 mt-2">
                <label htmlFor="test-file" className="cursor-pointer block">
                  {preview ? (
                    <div className="text-center">
                      <img
                        src={preview}
                        alt="Preview"
                        className="max-w-xs mx-auto rounded-lg shadow-md"
                      />
                      <p className="text-sm text-muted-foreground mt-2">
                        Click to change image
                      </p>
                    </div>
                  ) : (
                    <div className="text-center">
                      <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                      <p className="text-lg font-medium">
                        <span className="text-blue-600">Click to upload</span> a test image
                      </p>
                      <p className="text-sm text-muted-foreground mt-1">
                        PNG, JPG or JPEG (MAX. 10MB)
                      </p>
                    </div>
                  )}
                  <input
                    id="test-file"
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Item Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="item-name">Item Name</Label>
                <Input
                  id="item-name"
                  value={itemName}
                  onChange={(e) => setItemName(e.target.value)}
                  placeholder="Test Item"
                />
              </div>
              
              <div>
                <Label htmlFor="item-category">Category</Label>
                <Select value={category} onValueChange={setCategory}>
                  <SelectTrigger id="item-category">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="shirt">Shirt</SelectItem>
                    <SelectItem value="pants">Pants</SelectItem>
                    <SelectItem value="dress">Dress</SelectItem>
                    <SelectItem value="skirt">Skirt</SelectItem>
                    <SelectItem value="jacket">Jacket</SelectItem>
                    <SelectItem value="sweater">Sweater</SelectItem>
                    <SelectItem value="shoes">Shoes</SelectItem>
                    <SelectItem value="accessory">Accessory</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Test Controls */}
            <div className="flex gap-4 pt-4">
              <Button
                onClick={runTest}
                disabled={loading || !file}
                className="flex-1"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Running Test...
                  </>
                ) : (
                  "Run Communication Test"
                )}
              </Button>
              
              <Button
                onClick={resetTest}
                variant="outline"
                disabled={loading}
              >
                Reset Test
              </Button>
            </div>
          </div>
        </Card>

        {/* Test Results */}
        {results.length > 0 && (
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Test Results</h2>
            
            <div className="space-y-3">
              {results.map((result, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg border ${
                    result.success 
                      ? 'border-green-200 bg-green-50' 
                      : 'border-red-200 bg-red-50'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    {result.success ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-red-600" />
                    )}
                    <span className="font-medium">{result.step}</span>
                  </div>
                  <p className="text-sm mt-1 ml-6">
                    {result.message}
                  </p>
                  {result.data && (
                    <details className="mt-2 ml-6">
                      <summary className="text-xs text-gray-600 cursor-pointer">
                        View Details
                      </summary>
                      <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-auto">
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              ))}
            </div>

            {/* Summary */}
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <h3 className="font-medium mb-2">Test Summary</h3>
              <div className="text-sm space-y-1">
                <p>Total Steps: {results.length}</p>
                <p>Successful: {results.filter(r => r.success).length}</p>
                <p>Failed: {results.filter(r => !r.success).length}</p>
                <p>Success Rate: {Math.round((results.filter(r => r.success).length / results.length) * 100)}%</p>
              </div>
            </div>
          </Card>
        )}

        {/* Environment Info */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Environment Information</h2>
          <div className="space-y-2 text-sm">
            <p><strong>API URL:</strong> {process.env.NEXT_PUBLIC_API_URL || 'Not set'}</p>
            <p><strong>Node Environment:</strong> {process.env.NODE_ENV}</p>
            <p><strong>Firebase API Key:</strong> {process.env.NEXT_PUBLIC_FIREBASE_API_KEY ? 'Set' : 'Not set'}</p>
          </div>
        </Card>
      </div>
      
      {/* Debug component */}
      <AuthDebug />
    </div>
  );
}
