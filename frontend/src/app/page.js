import { ArrowRight } from "lucide-react";
import Link from "next/link";
import React from "react"; // Import React

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gray-900 px-4 py-16 font-sans antialiased text-gray-400">
      <div className="text-center space-y-8 max-w-3xl">
        {/* Main Heading */}
        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold leading-tight tracking-tight text-gray-400">
          Your Intelligent{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 drop-shadow-lg">
            AI Analyst
          </span>
          .
        </h1>

        {/* Sub-paragraph */}
        <p className="text-lg sm:text-xl text-gray-400 leading-relaxed max-w-xl mx-auto">
          Unlock **seamless AI integration** and **powerful data insights** to
          streamline your workflows and make smarter decisions.
        </p>

        {/* Call to Action Button */}
        <Link
          href="/dashboard"
          className="inline-flex items-center justify-center gap-2 px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-full shadow-lg transform transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-75"
        >
          Get Started
          <ArrowRight className="w-5 h-5" />
        </Link>
      </div>
    </main>
  );
}
