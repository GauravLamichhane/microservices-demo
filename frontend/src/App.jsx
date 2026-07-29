import { Routes, Route } from "react-router-dom";
import MainProductList from "./main/ProductList";
import AdminProductList from "./admin/ProductList";
import ProductForm from "./admin/ProductForm";
import AuditLogs from "./main/AuditLogs";
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MainProductList />} />
      <Route path="/products" element={<AdminProductList />} />
      <Route path="/products/create" element={<ProductForm />} />
      <Route path="/products/:id" element={<ProductForm />} />
      <Route path="/audit-logs" element={<AuditLogs />} />
    </Routes>
  );
}
