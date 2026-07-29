import { useEffect, useState } from "react";
import { getAuditLogs } from "../api/client";

const EVENT_STYLES = {
  product_created: { label: "Created", color: "bg-green-50 text-green-700" },
  product_updated: { label: "Updated", color: "bg-blue-50 text-blue-700" },
  product_deleted: { label: "Deleted", color: "bg-red-50 text-red-700" },
  product_liked: { label: "Liked", color: "bg-pink-50 text-pink-700" },
};

function EventBadge({ type }) {
  const style = EVENT_STYLES[type] || {
    label: type || "Unknown",
    color: "bg-gray-100 text-gray-600",
  };
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${style.color}`}
    >
      {style.label}
    </span>
  );
}

function formatPayload(payload) {
  if (payload === null || payload === undefined) return "—";
  if (typeof payload === "object") {
    return Object.entries(payload)
      .map(([key, value]) => `${key}: ${value}`)
      .join("  ·  ");
  }
  return String(payload);
}

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [limit, setLimit] = useState(50);

  async function loadLogs() {
    setLoading(true);
    setError("");
    try {
      const data = await getAuditLogs(limit);
      setLogs(data);
    } catch {
      setError("Failed to load audit logs.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadLogs();
  }, [limit]);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Audit Logs</h1>
            <p className="mt-1 text-sm text-gray-500">
              Recent events across the system, sourced from Kafka
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:border-gray-900 focus:outline-none"
            >
              <option value={20}>Last 20</option>
              <option value={50}>Last 50</option>
              <option value={100}>Last 100</option>
              <option value={200}>Last 200</option>
            </select>
            <button
              onClick={loadLogs}
              className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-gray-800"
            >
              Refresh
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Event
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Topic
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Details
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Time
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
                    Loading logs…
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td
                    colSpan={4}
                    className="px-6 py-12 text-center text-sm text-gray-400"
                  >
                    No audit logs found.
                  </td>
                </tr>
              ) : (
                logs.map((log, idx) => (
                  <tr key={idx} className="transition hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <EventBadge type={log.event_type} />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {log.topic || "—"}
                    </td>
                    <td className="max-w-md truncate px-6 py-4 text-sm text-gray-600">
                      {formatPayload(log.payload)}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                      {log.timestamp
                        ? new Date(log.timestamp).toLocaleString()
                        : "—"}
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
