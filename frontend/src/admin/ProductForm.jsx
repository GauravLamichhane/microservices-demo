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
  const { id } = useParams(); // present only on the edit route
  const isEditing = Boolean(id);
  const navigate = useNavigate();

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

  async function handleSubmit(e) {
    e.preventDefault();

    setError("");

    if (!title.trim()) {
      setError("Title is required.");
      return;
    }

    if (!image.trim()) {
      setError("Image URL is required.");
      return;
    }

    setSaving(true);
    try {
      if (isEditing) {
        await updateProduct(id, { title, image });
      } else {
        await createProduct({ title, image });
        setTitle("");
        setImage("");
      }
      setError("");
      navigate("/products/");
    } catch (err) {
      setError(
        isEditing ? "Failed to update product." : "Failed to create product.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError("");
    try {
      const { upload_url, public_url } = await getUploadUrl(file.name);
      await axios.put(upload_url, file, {
        headers: { "Content-Type": file.type },
      });
      setImage(public_url);
    } catch (err) {
      setError("Failed to upload image.");
    } finally {
      setUploading(false);
    }
  }

  if (loading) {
    return <p className="mx-10 mt-10">Loading product…</p>;
  }

  return (
    <form onSubmit={handleSubmit} className="mx-10 mt-10">
      <h2>{isEditing ? "Edit Product" : "Add Product"}</h2>

      {error && (
        <p className="mb-4 rounded bg-red-100 p-2 text-red-600">{error}</p>
      )}

      <div className="mb-4">
        <label className="mb-2 block">Title</label>
        <input
          type="text"
          className="w-2xl rounded border p-2"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter product title"
        />
      </div>

      <div className="mb-4">
        <label className="mb-2 block">Product Image</label>
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileChange}
        />
        {uploading && <p className="text-sm text-gray-500">Uploading…</p>}
        {image && !uploading && (
          <div className="mt-2">
            <img
              src={image}
              alt="Preview"
              className="h-24 w-24 rounded object-cover"
            />
          </div>
        )}
      </div>

      <button
        type="submit"
        disabled={saving || uploading}
        className="rounded bg-blue-400 px-4 py-2 text-white disabled:opacity-50 cursor-pointer hover:bg-blue-600"
      >
        {uploading
          ? "Uploading…"
          : saving
            ? isEditing
              ? "Saving…"
              : "Adding…"
            : isEditing
              ? "Save Changes"
              : "Add Product"}
      </button>
    </form>
  );
}
