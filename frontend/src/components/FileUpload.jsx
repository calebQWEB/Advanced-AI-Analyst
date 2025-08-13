"use client";
import { useState } from "react";
import { Upload, FileSpreadsheet } from "lucide-react";
import { useAuth } from "@/provider/AuthProvider";

export default function FileUpload() {
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const { session } = useAuth();

  const uploadFile = async (file) => {
    setUploading(true);
    try {
      if (!session) {
        throw new Error("Not authenticated");
      }

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/api/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      alert("Uploaded Successfully");
    } catch (error) {
      alert(error);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      uploadFile(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      uploadFile(files[0]);
    }
  };
  return (
    <div className="w-full max-w-md mx-auto">
      <div
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        className={`border-2 border-dashed border-gray-500 rounded-lg p-8 text-center transition-all duration-300 ease-in-out
          ${dragActive ? "border-blue-500 bg-blue-50" : "border-gray-300"}
          ${uploading ? "opacity-60 cursor-not-allowed" : "cursor-pointer"}
        `}
      >
        <FileSpreadsheet className="mx-auto h-16 w-16 text-blue-500 mb-5" />

        {uploading ? (
          <div className="flex flex-col items-center">
            <p className="text-lg font-semibold text-gray-700 mb-3">
              Uploading...
            </p>
            <div className="w-20 h-20 border-4 border-t-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
          </div>
        ) : (
          <>
            <p className="text-gray-700 text-lg font-medium mb-2">
              Drag & Drop your file here
            </p>
            <p className="text-sm text-gray-500 mb-4">
              or click the button below to select a file
            </p>

            <label className="cursor-pointer">
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileSelect}
                className="hidden"
                disabled={uploading}
              />
              <div
                className={`inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md
                  hover:bg-blue-700 transition-colors duration-200 ease-in-out
                  ${uploading ? "pointer-events-none opacity-50" : ""}
                `}
              >
                <Upload className="w-5 h-5 mr-3" />
                Select File
              </div>
            </label>
            <p className="text-xs text-gray-400 mt-4">
              Supported formats: .xlsx, .xls, .csv
            </p>
          </>
        )}
      </div>
    </div>
  );
}
