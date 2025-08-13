"use client";
import { Trash } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

export default function FileCard({
  id,
  filename,
  upload_date,
  status,
  session_token,
  refetchFiles,
  allFilesLoad,
}) {
  const [isDeleting, setIsDeleting] = useState(false);
  const AnalyzeFile = async () => {
    if (!session_token) {
      throw new Error("User is not authenticated");
    }
    if (!id) {
      throw new Error("File ID is missing");
    }

    try {
      const response = await fetch(`/api/analyze/${id}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session_token}`,
          "Content-Type": "application/json",
        },
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.message || "Failed to analyze file");
      }
      alert("File analysis started successfully!");
      console.log("File analysis result:", result);
    } catch (error) {
      alert(`Error: ${error.message}`);
      console.error("File analysis error:", error);
    } finally {
      refetchFiles();
    }
  };

  const deleteFile = async () => {
    if (!session_token) {
      throw new Error("User is not authenticated");
    }
    if (!id) {
      throw new Error("File ID is missing");
    }

    setIsDeleting(true);
    try {
      const response = await fetch(`/api/files/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${session_token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to delete file");
      }

      alert("File deleted successfully!");
    } catch (error) {
      console.error("Error deleting file:", error);
    } finally {
      refetchFiles();
      setIsDeleting(false);
    }
  };

  return (
    <div
      className="relative p-6 w-full max-w-sm bg-white/5 backdrop-blur-xl rounded-2xl shadow-xl border border-white/10
                 cursor-pointer transform transition-all duration-300 ease-in-out"
    >
      <div className="absolute inset-0 rounded-2xl pointer-events-none border border-transparent group-hover:border-blue-500 transition-colors duration-300"></div>

      <div className="flex items-center justify-between mb-7">
        <p className="text-sm text-gray-300 font-medium">
          Uploaded:{" "}
          {new Date(upload_date).toLocaleString("en-US", {
            dateStyle: "medium",
            timeStyle: "short",
          })}
        </p>

        <button onClick={deleteFile}>
          {isDeleting ? (
            <span className="animate-pulse">
              <Trash className="w-5 h-5 text-red-500" />
            </span>
          ) : (
            <Trash className="w-5 h-5 text-gray-400 hover:text-red-500 transition-colors duration-300" />
          )}
        </button>
      </div>

      <div className="flex items-center justify-between mb-4">
        <h3 className="text-2xl font-semibold text-white truncate max-w-[calc(100%-80px)]">
          {filename}
        </h3>

        {/* Status Badge */}
        <span
          className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide
            ${
              status === "analyzed"
                ? "bg-green-600/20 text-green-300 border border-green-500/30"
                : status === "processing"
                ? "bg-yellow-600/20 text-yellow-300 border border-yellow-500/30 animate-pulse"
                : status === "failed" || status === "error"
                ? "bg-red-600/20 text-red-300 border border-red-500/30"
                : "bg-gray-600/20 text-gray-300 border border-gray-500/30"
            }`}
        >
          {allFilesLoad ? "Processing..." : status}
        </span>
      </div>

      <div className="mt-5 grid gap-3">
        {status === "uploaded" || status === "error" || status === "failed" ? (
          <button
            className={`w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg shadow-md
                        hover:from-blue-700 hover:to-purple-700 transition-all duration-300 ease-in-out transform hover:scale-[1.02]
                        focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-75
                        ${allFilesLoad ? "opacity-60 cursor-not-allowed" : ""}`}
            disabled={allFilesLoad}
            onClick={(e) => {
              e.stopPropagation();
              AnalyzeFile();
            }}
          >
            {allFilesLoad ? "Analyzing..." : "Analyze File"}
          </button>
        ) : (
          <>
            <Link
              href={`/analytics/${id}`}
              className="group w-full inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg shadow-md
                         hover:from-blue-700 hover:to-purple-700 transition-all duration-300 ease-in-out transform hover:scale-[1.02]
                         focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-75"
              onClick={(e) => {
                e.stopPropagation();
              }}
            >
              View Analytics
              <span className="ml-2 group-hover:translate-x-1 transition-transform duration-200">
                →
              </span>
            </Link>
            <Link
              href={`/chat/${id}`}
              className="w-full inline-flex items-center justify-center px-6 py-3 bg-white/10 text-gray-200 font-medium rounded-lg shadow-md border border-white/20
                         hover:bg-white/20 hover:text-white transition-all duration-300 ease-in-out transform hover:scale-[1.02]
                         focus:outline-none focus:ring-4 focus:ring-gray-400 focus:ring-opacity-50"
              onClick={(e) => e.stopPropagation()}
            >
              Ask AI
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
