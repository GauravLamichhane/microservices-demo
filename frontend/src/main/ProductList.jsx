import { useState, useEffect } from "react";
import ProductCard from "./ProductCard";
import { getMainProducts, likeProduct, searchProducts } from "../api/client";
export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [likeError, setLikeError] = useState({});
  const [searchQuery, setSearchQuery] = useState("");
  const [searchError, setSearchError] = useState("");

  async function loadProducts() {
    const data = await getMainProducts();
    setProducts(data);
  }

  useEffect(() => {
    loadProducts();
  }, []);

  async function handleSearch(e) {
    e.preventDefault();

    if (!searchQuery.trim()) {
      setSearchError("");
      loadProducts();
      return;
    }

    const results = await searchProducts(searchQuery);

    if (results.length === 0) {
      setProducts([]);
      setSearchError("No products found.");
    } else {
      setProducts(results);
      setSearchError("");
    }
  }

  async function handleLike(id) {
    try {
      await likeProduct(id);
      setLikeError((prev) => ({ ...prev, [id]: null }));
      loadProducts();
    } catch (error) {
      if (error.response && error.response.status === 400) {
        setLikeError((prev) => ({ ...prev, [id]: "Already liked!" }));
      } else {
        setLikeError((prev) => ({ ...prev, [id]: "Something went wrong" }));
      }
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 p-6">
      <form onSubmit={handleSearch} className="mb-4">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search products..."
          className="rounded border p-2"
        />
        <button
          type="submit"
          className="ml-2 rounded bg-blue-500 px-4 py-2 text-white"
        >
          Search
        </button>
        {searchError && <p className="text-red-500">{searchError}</p>}
      </form>
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
