import React from 'react';
import Link from 'next/link';

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex gap-8">
        {/* Settings Sidebar */}
        <div className="w-64 flex-shrink-0">
          <h2 className="text-2xl font-bold mb-4">Settings</h2>
          <nav className="space-y-2">
            <Link 
              href="/settings/analysis" 
              className="block px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              Wardrobe Analysis
            </Link>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          {children}
        </div>
      </div>
    </div>
  );
} 