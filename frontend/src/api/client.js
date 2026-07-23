import axios from "axios";

const baseURL = import.meta.env.VITE_ADMIN_API_URL || "/api/admin";
export const api = axios.create({ baseURL });

const flaskBaseURL = import.meta.env.VITE_MAIN_API_URL || "/api/main";
const flaskApi = axios.create({ baseURL: flaskBaseURL });

export async function getAdminProducts() {
  const { data } = await api.get("admin/products/");
  return data;
}

export async function getMainProducts() {
  const { data } = await flaskApi.get("/products"); // Flask
  return data;
}

export async function likeProduct(id) {
  const { data } = await flaskApi.post(`/products/${id}/like`);
  return data;
}

export async function createProduct(payload) {
  const { data } = await api.post("admin/products/", payload);
  return data;
}

export async function updateProduct(id, payload) {
  const { data } = await api.put(`admin/products/${id}/`, payload);
  return data;
}

export async function deleteProduct(id) {
  const { data } = await api.delete(`admin/products/${id}/`);
  return data;
}

export async function getProduct(id) {
  const { data } = await api.get(`admin/products/${id}/`);
  return data;
}

// search service
export async function searchProducts(query) {
  const { data } = await flaskApi.get(`/search?q=${encodeURIComponent(query)}`);
  return data;
}

export async function getAuditLogs(limit = 50) {
  const { data } = await flaskApi.get(`/audit-logs?limit=${limit}`);
  return data;
}

export async function getUploadUrl(filename) {
  const { data } = await api.post("/products/upload-url/", { filename });
  return data;
}
