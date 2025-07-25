"use client";

import { useState } from "react";
import { useStorage } from "@/lib/hooks/useStorage";

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const { uploadFile, uploading, error } = useStorage();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    try {
      const path = `clothes/${Date.now()}_${file.name}`;
      const downloadURL = await uploadFile(file, path);
      console.log("File uploaded:", downloadURL);
      // TODO: Save clothing item to Firestore
      setFile(null);
      setPreview("");
    } catch (err) {
      console.error("Error uploading file:", err);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="photo">
          Upload Photo
        </label>
        <div>
          <label htmlFor="photo">
            {preview ? (
              <img
                src={preview}
                alt="Preview"
              />
            ) : (
              <div>
                <svg
                  aria-hidden="true"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 20 16"
                >
                  <path
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
                  />
                </svg>
                <p>
                  <span>Click to upload</span> or drag and drop
                </p>
                <p>
                  PNG, JPG or JPEG (MAX. 800x400px)
                </p>
              </div>
            )}
            <input
              id="photo"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
            />
          </label>
        </div>
      </div>

      {error && (
        <div>
          {error.message}
        </div>
      )}

      <button
        type="submit"
        disabled={!file || uploading}
      >
        {uploading ? "Uploading..." : "Upload"}
      </button>
    </form>
  );
} 