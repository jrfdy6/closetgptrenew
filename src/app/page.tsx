import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-950 dark:to-indigo-900 text-center p-4">
      <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
        ClosetGPT
      </h1>
      <p className="text-lg text-gray-700 dark:text-gray-300 mb-8">
        Your AI-powered personal stylist - ROOT TEST
      </p>
      <div className="space-y-4">
        <Link href="/signin" className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors shadow-md">
          Go to Sign In
        </Link>
        <Link href="/test-static" className="inline-block bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors shadow-md ml-4">
          Test Static Page
        </Link>
      </div>
    </div>
  );
} 