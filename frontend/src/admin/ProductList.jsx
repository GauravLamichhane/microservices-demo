import { useEffect, useState } from "react";
import { deleteProduct, getAdminProducts, updateProduct } from "../api/client";
import { useNavigate } from "react-router-dom";
export default function ProductList() {
  const [products, setProducts] = useState([]);
  const navigate = useNavigate();

  async function loadProducts() {
    const data = await getAdminProducts();
    console.log(data);
    setProducts(data);
  }

  async function handleDelete(id) {
    const confirmed = window.confirm("Are you sure you want to delete this ?");
    if (!confirmed) return;
    await deleteProduct(id);
    loadProducts(); //update the state so the data saved in the state is not shown even though the data is not in the backend
  }
  useEffect(() => {
    loadProducts();

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";

    const socket = new WebSocket(
      `${protocol}://${window.location.host}/ws/likes/`,
    );
    socket.onopen = () => console.log("WS Connected");
    socket.onclose = (e) => console.log("WS Closed", e);
    socket.onerror = (e) => console.log("WS Error", e);

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
    <div className="p-6">
      <button
        onClick={() => navigate("/admin/create/")}
        className="bg-green-400 cursor-pointer px-4 py-4 mb-2 hover:bg-green-600"
      >
        Add product
      </button>
      <table className="w-full border border-gray-300">
        <thead className="bg-gray-100">
          <tr>
            <th className="border p-3 text-left">ID</th>
            <th className="border p-3 text-left">Title</th>
            <th className="border p-3 text-left">Image</th>
            <th className="border p-3 text-left">Likes</th>
            <th className="border p-3 text-left">Action</th>
          </tr>
        </thead>

        <tbody>
          {products.map((product) => (
            <tr key={product.id}>
              <td className="border p-3">{product.id}</td>

              <td className="border p-3">{product.title}</td>

              <td className="border p-3">
                <img
                  src={product.image}
                  alt={product.title}
                  className="h-16 w-16 rounded object-cover"
                />
              </td>

              <td className="border p-3">{product.likes}</td>

              <td
                className="border px-2
            "
              >
                <div className="">
                  <button
                    className="rounded bg-red-500 px-3 py-2 text-white hover:bg-red-600 mr-2"
                    onClick={() => handleDelete(product.id)}
                  >
                    Delete
                  </button>
                  <button
                    className="rounded bg-blue-500 px-2 py-2 text-white hover:bg-blue-600"
                    onClick={() => navigate(`/admin/products/${product.id}`)}
                  >
                    Edit
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
