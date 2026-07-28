import { useEffect, useState } from "react";
import { deleteProduct, getAdminProducts } from "../api/client";
import { useNavigate } from "react-router-dom";

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  async function loadProducts() {
    const data = await getAdminProducts();
    setProducts(data);
    setLoading(false);
  }

  async function handleDelete(id) {
    const confirmed = window.confirm("Are you sure you want to delete this?");
    if (!confirmed) return;
    await deleteProduct(id);
    loadProducts();
  }

  useEffect(() => {
    loadProducts();

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(
      `${protocol}://${window.location.host}/ws/likes/`,
    );

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProducts((prev) =>
        prev.map((product) =>
          product.id === data.product_id
            ? { ...product, likes: data.likes }
            : product,
        ),
      );
    };

    return () => socket.close();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Products</h1>
            <p className="mt-1 text-sm text-gray-500">
              {products.length} {products.length === 1 ? "product" : "products"}{" "}
              total
            </p>
          </div>
          <button
            onClick={() => navigate("/products/create/")}
            className="rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-gray-800"
          >
            + Add Product
          </button>
        </div>

        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Image
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Likes
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td
                    colSpan={4}
                    className="px-6 py-12 text-center text-sm text-gray-400"
                  >
                    Loading products…
                  </td>
                </tr>
              ) : products.length === 0 ? (
                <tr>
                  <td
                    colSpan={4}
                    className="px-6 py-12 text-center text-sm text-gray-400"
                  >
                    No products yet. Add your first one to get started.
                  </td>
                </tr>
              ) : (
                products.map((product) => (
                  <tr key={product.id} className="transition hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <img
                        src={product.image}
                        alt={product.title}
                        className="h-12 w-12 rounded-lg border border-gray-200 object-cover"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-medium text-gray-900">
                        {product.title}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 rounded-full bg-pink-50 px-2.5 py-1 text-xs font-medium text-pink-700">
                        ♥ {product.likes}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => navigate(`/products/${product.id}`)}
                        className="mr-3 text-sm font-medium text-blue-600 hover:text-blue-800"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(product.id)}
                        className="text-sm font-medium text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
