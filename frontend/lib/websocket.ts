import { useEffect, useRef, useState } from "react";

const getWebSocketBase = () => {
  if (process.env.NEXT_PUBLIC_WS_URL) {
    return process.env.NEXT_PUBLIC_WS_URL.replace(/\/$/, "");
  }

  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/^http/, "ws").replace(/\/$/, "");
  }

  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    const isLocalHost =
      host === "localhost" ||
      host === "127.0.0.1" ||
      host === "0.0.0.0" ||
      /^(172\.|10\.|192\.168\.)/.test(host);
    if (!isLocalHost) {
      return "";
    }

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    return `${protocol}://${window.location.hostname}:8000`;
  }

  return "ws://localhost:8000";
};

const WS_BASE = getWebSocketBase();

export function useWebSocket<T>(channel: string, onMessage?: (data: T) => void) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastData, setLastData] = useState<T | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let ws: WebSocket;
    let timer: NodeJS.Timeout;

    const connect = () => {
      ws = new WebSocket(`${WS_BASE}${channel}`);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setLastData(parsed);
          if (onMessage) onMessage(parsed);
        } catch (e) {
          console.error("WS message parse error:", e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Auto-reconnect after 3s
        timer = setTimeout(connect, 3000);
      };

      ws.onerror = (err) => {
        console.error("WS error:", err);
        ws.close();
      };
    };

    connect();

    return () => {
      clearTimeout(timer);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [channel]);

  return { isConnected, lastData };
}
