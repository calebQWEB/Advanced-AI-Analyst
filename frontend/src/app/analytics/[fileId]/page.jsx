"use client";
import { useAuth } from "@/provider/AuthProvider";
import ErrorMessage from "@/utils/ErrorMessage";
import LoadingSpinner from "@/utils/LoadingSpinner";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import AnalyticsDashboard from "../_components/AnalyticsDashboard";

export default function Analytics() {
  const { user, session } = useAuth();
  const { fileId } = useParams();
  const [fileData, setFileData] = useState(null);
  const [getFileError, setGetFileError] = useState("");
  const [getFileLoading, setGetFileLoading] = useState(false);
  const [fileAnalytics, setFileAnalytics] = useState(null);
  const [getAnalyticsError, setGetAnalyticsError] = useState("");
  const [getAnalyticsLoading, setGetAnalyticsLoading] = useState(false);

  const [isExportting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState("");

  const fetchFileData = async () => {
    if (!fileId || !session) {
      console.log("File ID or session is missing.");
      return;
    }

    setGetFileLoading(true);
    setGetFileError("");
    try {
      const response = await fetch(`/api/files/${fileId}`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch file data");
      }

      const data = await response.json();
      setFileData(data);
      console.log("File data:", data);
    } catch (error) {
      console.log("Error fetching file data:", error);
      setGetFileError(
        error.message || "An error occurred while fetching file data"
      );
    } finally {
      setGetFileLoading(false);
    }
  };

  const viewAnalytics = async () => {
    if (!fileId || !session) {
      setGetAnalyticsError("File ID or session is missing.");
      return;
    }

    setGetAnalyticsLoading(true);
    setGetAnalyticsError("");
    try {
      const response = await fetch(`/api/analyses/${fileId}`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          "Content-Type": "application/json",
        },
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.message || "Failed to get analytics");
      }
      setFileAnalytics(result.insights);
      console.log("File analysis result:", result.insights);
    } catch (error) {
      console.log("Error viewing analytics:", error);
      setGetAnalyticsError(error.message || "Failed to view analytics");
    } finally {
      setGetAnalyticsLoading(false);
    }
  };

  const exportPDF = async () => {
    if (!fileId || !session) {
      setGetFileError("File ID or session is missing.");
      return;
    }

    setIsExporting(true);
    setExportError("");

    try {
      const response = await fetch(`/api/export/${fileId}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        setExportError(`Failed to export PDF: ${errorText}`);
        console.error("Export error:", response.statusText);
        return;
      }

      const blob = await response.blob();

      let filename = `${fileId}_Analysis_Report.pdf`;
      const contentDisposition = response.headers.get("content-disposition");
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(
          /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
        );
        if (filenameMatch) {
          filename = filenameMatch[1].replace(/['"]/g, "");
        }
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();

      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);

      // Success notification (consider using a toast instead of alert)
      alert("PDF report downloaded successfully!");
    } catch (error) {
      console.error("Export error:", error);
      setExportError(error.message || "An error occurred while exporting PDF");
    } finally {
      setIsExporting(false);
    }
  };

  useEffect(() => {
    fetchFileData();
  }, [fileId, session]);

  useEffect(() => {
    if (fileId && session) {
      viewAnalytics();
    }
  }, [fileId, session]);

  if (getFileLoading || getAnalyticsLoading) {
    return (
      <section className="px-8 py-4 bg-gray-900 min-h-screen">
        <LoadingSpinner message="Fetching your files" />
      </section>
    );
  }

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

  return (
    <section className="px-8 py-4 bg-gray-900 min-h-screen mt-10">
      {getFileError && (
        <ErrorMessage message={getFileError} onRetry={fetchFileData} />
      )}
      {fileData ? (
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-extrabold leading-tight tracking-tight text-gray-400">
            Analytics for {fileData.filename}
          </h1>

          <button
            onClick={exportPDF}
            className="border border-white/20 rounded-lg bg-white/10 px-8 py-3 text-white shadow-2xl backdrop-blur-md cursor-pointer hover:bg-white/20 transition-colors duration-300"
          >
            {isExportting ? "Exporting..." : "Export to PDF"}
          </button>
        </div>
      ) : (
        <p className="text-gray-400">
          No analytics data available for this file.
        </p>
      )}

      {fileData && fileAnalytics && (
        <AnalyticsDashboard fileData={fileData} fileAnalytics={fileAnalytics} />
      )}
    </section>
  );
}
