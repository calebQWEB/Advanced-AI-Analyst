"use client";
import FileUpload from "@/components/FileUpload";
import { useCallback, useEffect, useState } from "react";
import FileCard from "./_components/FileCard";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/provider/AuthProvider";
import LoadingSpinner from "@/utils/LoadingSpinner";
import ErrorMessage from "@/utils/ErrorMessage";
import Link from "next/link";

export default function DashboardMainPage() {
  const [allFiles, setAllFiles] = useState([]);
  const [allFilesError, setAllFilesError] = useState("");
  const [allFilesLoad, setAllFilesLoad] = useState(false);
  const { user, session } = useAuth();

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center text-gray-400">
          <h1 className="text-3xl font-bold mb-4">
            Please log in to access your dashboard
          </h1>
          <p className="mb-6">
            You need to be authenticated to view this page.
          </p>
          <Link
            href="/login"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-full shadow-lg transform transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-75"
          >
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  const getAllFiles = useCallback(async () => {
    setAllFilesError("");
    setAllFilesLoad(true);

    try {
      if (!session) throw new Error("Not authenticated");

      const response = await fetch("/api/files", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAllFiles(data.files); // assuming data has `files` field
    } catch (err) {
      setAllFilesError(err.message || String(err));
    } finally {
      setAllFilesLoad(false);
    }
  }, [session]);

  const updateProfile = async () => {
    const {
      data: { user },
    } = await supabase.auth.getUser();

    if (user) {
      const { error } = await supabase.from("profiles").upsert([
        {
          id: user.id,
          email: user.email,
          full_name: user.user_metadata?.display_name || "Anonymous",
        },
      ]);

      if (error) console.error("Profile insert failed:", error.message);
    }
  };

  useEffect(() => {
    updateProfile();
  }, []);

  useEffect(() => {
    if (session) {
      getAllFiles();
    }
  }, [getAllFiles]);

  return (
    <section className="px-8 py-4 bg-gray-900 min-h-screen">
      <div className="flex items-center justify-center">
        <FileUpload />
      </div>
      {allFilesLoad && <LoadingSpinner message="Fetching your files..." />}
      {allFilesError && (
        <ErrorMessage message={allFilesError} onRetry={getAllFiles} />
      )}
      {allFiles && (
        <div className="mt-9 flex items-center justify-start gap-3 flex-wrap">
          {allFiles.map((item) => (
            <FileCard
              key={item.id}
              {...item}
              session_token={session.access_token}
              refetchFiles={getAllFiles}
              allFilesLoad={allFilesLoad}
            />
          ))}
        </div>
      )}
    </section>
  );
}
