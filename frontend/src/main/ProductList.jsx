import { useState, useEffect } from "react";
import ProductCard from "./ProductCard";
import { getMainProducts, likeProduct } from "../api/client";
export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [likeError, setLikeError] = useState({});

  async function loadProducts() {
    const data = await getMainProducts();
    setProducts(data);
  }

  useEffect(() => {
    loadProducts();
  }, []);

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
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {products.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            handleLike={handleLike}
            errorMessage={likeError[[product.id]]}
          />
        ))}
      </div>
    </div>
  );
}
