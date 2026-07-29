import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  createProduct,
  getProduct,
  updateProduct,
  getUploadUrl,
} from "../api/client";
import axios from "axios";

export default function ProductForm() {
  const { id } = useParams();
  const isEditing = Boolean(id);
  const navigate = useNavigate();

  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState("");

  const [title, setTitle] = useState("");
  const [image, setImage] = useState("");

  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(isEditing);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (!isEditing) return;

    getProduct(id)
      .then((product) => {
        setTitle(product.title);
        setImage(product.image);
      })
      .catch(() => setError("Couldn't load this product."))
      .finally(() => setLoading(false));
  }, [id, isEditing]);

  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (preview) {
      URL.revokeObjectURL(preview);
    }

    const objectUrl = URL.createObjectURL(file);

    setSelectedFile(file);
    setPreview(objectUrl);
  }

  async function handleSubmit(e) {
    e.preventDefault();

    setError("");

    if (!title.trim()) {
      return setError("Title is required.");
    }

    if (!isEditing && !selectedFile) {
      return setError("Please choose an image.");
    }

    setSaving(true);

    try {
      let imageUrl = image;

      if (selectedFile) {
        setUploading(true);

        try {
          const { upload_url, public_url } = await getUploadUrl(
            selectedFile.name,
          );

          await axios.put(upload_url, selectedFile, {
            headers: {
              "Content-Type": selectedFile.type,
            },
          });

          imageUrl = public_url;
        } finally {
          setUploading(false);
        }
      }

      if (isEditing) {
        await updateProduct(id, {
          title,
          image: imageUrl,
        });
      } else {
        await createProduct({
          title,
          image: imageUrl,
        });

        setTitle("");
        setImage("");
        setSelectedFile(null);

        if (preview) {
          URL.revokeObjectURL(preview);
        }

        setPreview("");
      }

      navigate("/products/");
    } catch {
      setError(
        isEditing ? "Failed to update product." : "Failed to create product.",
      );
    } finally {
      setSaving(false);
      setUploading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <p className="text-sm text-gray-400">Loading product…</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-10">
      <div className="mx-auto max-w-lg rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
        <h2 className="mb-6 text-xl font-semibold text-gray-900">
          {isEditing ? "Edit Product" : "Add Product"}
        </h2>

        {error && (
          <div className="mb-5 rounded-lg border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">
              Title
            </label>

            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Wireless Mouse"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">
              Product Image
            </label>

            <div className="flex items-center gap-4">
              {preview || image ? (
                <img
                  src={preview || image}
                  alt="Preview"
                  className="h-16 w-16 flex-shrink-0 rounded-lg border border-gray-200 object-cover"
                />
              ) : (
                <div className="flex h-16 w-16 flex-shrink-0 items-center justify-center rounded-lg border border-dashed border-gray-300 text-xs text-gray-400">
                  No image
                </div>
              )}

              <label className="flex-1 cursor-pointer rounded-lg border border-gray-300 px-3 py-2 text-center text-sm text-gray-600 transition hover:border-gray-400 hover:bg-gray-50">
                {uploading ? "Uploading..." : "Choose file"}

                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={saving || uploading}
            className="w-full rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {uploading
              ? "Uploading..."
              : saving
                ? isEditing
                  ? "Saving..."
                  : "Adding..."
                : isEditing
                  ? "Save Changes"
                  : "Add Product"}
          </button>
        </form>
      </div>
    </div>
  );
}
