import { Routes, Route } from "react-router-dom";
import MainProductList from "./main/ProductList";
import AdminProductList from "./admin/ProductList";
import ProductForm from "./admin/ProductForm";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MainProductList />} />
      <Route path="/products" element={<AdminProductList />} />
      <Route path="/products/create" element={<ProductForm />} />
      <Route path="/products/:id" element={<ProductForm />} />
    </Routes>
  );
}
