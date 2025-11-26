// Resolve API URL at build time, but allow runtime override via `window.__API_URL__`.
export const API_URL =
  (typeof window !== "undefined" && window.__API_URL__) ||
  import.meta.env.VITE_BACKEND_URL ||
  import.meta.env.VITE_API_URL ||
  'http://localhost:5000';

// Helper for API fetches that accepts either a full URL or a path.
export async function apiFetch(pathOrUrl, options) {
  const url =
    typeof pathOrUrl === "string" && /^https?:\/\//.test(pathOrUrl)
      ? pathOrUrl
      : `${API_URL}${pathOrUrl.startsWith("/") ? pathOrUrl : `/${pathOrUrl}`}`;
  // Helpful debug log when diagnosing live-site issues
  if (
    typeof window !== "undefined" &&
    window.location &&
    window.location.hostname !== "localhost"
  ) {
    console.debug("[apiFetch] url=", url);
  }
  try {
    const res = await fetch(url, options);
    return res;
  } catch (err) {
    const message = err && err.message ? err.message : String(err);
    const userMessage =
      message.includes("blocked") || message.includes("Blocked")
        ? "Network request was blocked by the browser or an extension (ERR_BLOCKED_BY_CLIENT). Try disabling ad-block/privacy extensions for this site."
        : `Network error when contacting API (${message}). Check backend and network connectivity.`;
    console.warn("[apiFetch] network error:", message);
    const e = new Error(userMessage);
    e.cause = err;
    throw e;
  }
}
