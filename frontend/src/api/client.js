import axios from "axios";

//Django i.e admin service
const baseURL = "http://localhost:8000";
export const api = axios.create({ baseURL });

// Flask i.e main service
const flaskBaseURL = "http://localhost:8001";
const flaskApi = axios.create({ baseURL: flaskBaseURL });

export async function getAdminProducts() {
  const { data } = await api.get("/api/products/");
  return data;
}

export async function getMainProducts() {
  const { data } = await flaskApi.get("/api/products"); // Flask
  return data;
}

export async function likeProduct(id) {
  const { data } = await flaskApi.post(`/api/products/${id}/like`);
  return data;
}

export async function createProduct(payload) {
  const { data } = await api.post("/api/products/", payload);
  return data;
}

export async function updateProduct(id, payload) {
  const { data } = await api.put(`/api/products/${id}/`, payload);
  return data;
}

export async function deleteProduct(id) {
  const { data } = await api.delete(`/api/products/${id}/`);
  return data;
}

export async function getProduct(id) {
  const { data } = await api.get(`/api/products/${id}/`);
  return data;
}

// search service
export async function searchProducts(query) {
  //{ data } extracts only the data field.
  const { data } = await flaskApi.get(
    `/api/search?q=${encodeURIComponent(query)}`, // convert special char into URL-safe format
  );
  return data;
}
