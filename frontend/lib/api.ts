const getApiBase = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "");
  }

  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    const localNetworkHosts = ["localhost", "127.0.0.1", "0.0.0.0"];
    const isPrivateHost = /^(172\.|10\.|192\.168\.)/.test(host);

    if (localNetworkHosts.includes(host) || isPrivateHost) {
      return "";
    }
  }

  return "";
};

const API_BASE = getApiBase();

export async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const normalized = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = API_BASE ? `${API_BASE}${normalized}` : normalized;
  const headers = new Headers(options?.headers);
  if (options?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(url, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.error || `API error (${res.status})`);
  }

  return res.json();
}
