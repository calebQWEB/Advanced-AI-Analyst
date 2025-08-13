"use client";
import { useAuth } from "@/provider/AuthProvider";
import { LogIn, UserPlus, LogOut, User } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React from "react";

const Navbar = () => {
  const { user, session, loading, signOut } = useAuth();
  const router = useRouter();
  const handleSignOut = async () => {
    try {
      await signOut();
      router.push("/login");
      console.log("User signed out successfully");
    } catch (error) {
      console.error("Error signing out:", error);
    }
  };

  return (
    <nav className="flex items-center justify-between px-8 py-4 bg-gray-900 text-gray-200">
      <Link
        href="/"
        className="text-2xl md:text-3xl font-extrabold text-blue-400 tracking-wider"
      >
        AI <span className="text-gray-50">Analyst</span>
      </Link>

      <div className="flex items-center gap-6">
        {loading ? (
          <div className="text-sm">Loading...</div>
        ) : user ? (
          // Show when user is logged in
          <div className="flex items-center gap-4">
            <span className="text-sm">
              Welcome, {user.user_metadata.display_name || user.email}
            </span>
            <button
              onClick={handleSignOut}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-full bg-red-500 hover:bg-red-600 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              Sign Out
            </button>
          </div>
        ) : (
          // Show when user is not logged in
          <>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 text-sm font-medium transition-colors hover:text-blue-400"
            >
              <LogIn className="h-4 w-4" />
              Login
            </Link>
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-full bg-blue-500 hover:bg-blue-600 transition-colors"
            >
              <UserPlus className="h-4 w-4" />
              Sign up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
