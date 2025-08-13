"use client";
import FileUpload from "@/components/FileUpload";
import { useCallback, useEffect, useState } from "react";
import FileCard from "./_components/FileCard";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/provider/AuthProvider";
import LoadingSpinner from "@/utils/LoadingSpinner";
import ErrorMessage from "@/utils/ErrorMessage";

export default function DashboardMainPage() {
  const [allFiles, setAllFiles] = useState([]);
  const [allFilesError, setAllFilesError] = useState("");
  const [allFilesLoad, setAllFilesLoad] = useState(false);
  const { session } = useAuth();

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
