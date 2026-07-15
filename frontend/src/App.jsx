import { Routes, Route } from "react-router-dom";
import MainProductList from "./main/ProductList";
import AdminProductList from "./admin/ProductList";
import ProductForm from "./admin/ProductForm";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MainProductList />} />
      <Route path="/admin/products" element={<AdminProductList />} />
      <Route path="/admin/create" element={<ProductForm />} />
      <Route path="/admin/products/:id" element={<ProductForm />} />
    </Routes>
  );
}
