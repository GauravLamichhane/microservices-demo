import { useState, useEffect } from "react";
import ProductCard from "./ProductCard";
import { getMainProducts, likeProduct, searchProducts } from "../api/client";

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [likeError, setLikeError] = useState({});
  const [searchQuery, setSearchQuery] = useState("");
  const [searchError, setSearchError] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadProducts() {
    try {
      setLoading(true);
      const data = await getMainProducts();
      setProducts(data);
      setError("");
    } catch {
      setError("Failed to load products");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProducts();
  }, []);

  useEffect(() => {
    const timer = setTimeout(async () => {
      try {
        setSearchError("");

        if (!searchQuery.trim()) {
          await loadProducts();
          return;
        }

        const results = await searchProducts(searchQuery);

        setProducts(results);

        if (results.length === 0) {
          setSearchError("No products found.");
        }
      } catch {
        setSearchError("Search failed.");
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  async function handleLike(id) {
    try {
      await likeProduct(id);

      setProducts((prev) =>
        prev.map((product) =>
          product.id === id
            ? { ...product, likes: product.likes + 1 }
            : product,
        ),
      );

      setLikeError((prev) => ({
        ...prev,
        [id]: null,
      }));
    } catch (error) {
      if (error.response?.status === 400) {
        setLikeError((prev) => ({
          ...prev,
          [id]: "Already liked!",
        }));
      } else {
        setLikeError((prev) => ({
          ...prev,
          [id]: "Something went wrong",
        }));
      }
    }
  }

  if (loading) {
    return <p className="p-6">Loading products...</p>;
  }

  if (error) {
    return <p className="p-6 text-red-500">{error}</p>;
  }

  return (
    <div className="min-h-screen bg-neutral-50 p-6">
      <div className="mb-6">
        <input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search products..."
          className="w-full max-w-md rounded border p-2"
        />
      </div>

      {searchError && <p className="mb-4 text-red-500">{searchError}</p>}

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {products.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            handleLike={handleLike}
            errorMessage={likeError[product.id]}
          />
        ))}
      </div>
    </div>
  );
}
