"use client";

export default function TestImagesPage() {
  const testImages = [
    "/images/outfit-quiz/F-CB1.png",
    "/images/outfit-quiz/F-CB2.png", 
    "/images/outfit-quiz/F-OM1.png",
    "/images/outfit-quiz/F-ST1.png",
    "/images/outfit-quiz/F-MIN1.png"
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Image Test Page</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testImages.map((imageUrl, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="aspect-square bg-gray-100 flex items-center justify-center">
                <img
                  src={imageUrl}
                  alt={`Test image ${index + 1}`}
                  className="w-full h-full object-contain"
                  onError={(e) => {
                    console.error('Image failed to load:', imageUrl);
                    e.currentTarget.style.display = 'none';
                    const fallback = document.createElement('div');
                    fallback.className = 'flex flex-col items-center justify-center text-red-500 p-4';
                    fallback.innerHTML = `
                      <div class="text-4xl mb-2">❌</div>
                      <div class="text-center">
                        <div class="text-sm font-medium mb-1">Failed to load</div>
                        <div class="text-xs text-gray-400">${imageUrl}</div>
                      </div>
                    `;
                    e.currentTarget.parentNode?.appendChild(fallback);
                  }}
                  onLoad={() => {
                    console.log('✅ Image loaded successfully:', imageUrl);
                  }}
                />
              </div>
              <div className="p-4">
                <p className="text-sm text-gray-600 font-mono">{imageUrl}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Instructions:</h2>
          <ol className="list-decimal list-inside space-y-1 text-sm">
            <li>Check if all images load properly</li>
            <li>Open browser console to see load/error messages</li>
            <li>If images fail, check the network tab for 404 errors</li>
            <li>Try hard refresh (Cmd+Shift+R) if needed</li>
          </ol>
        </div>
      </div>
    </div>
  );
} 