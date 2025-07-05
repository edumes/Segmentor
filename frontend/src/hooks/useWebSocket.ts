import { useEffect, useRef } from 'react';

interface WebSocketMessage {
  type: string;
  items: any[];
}

export function useWebSocket(url: string, onMessage: (data: WebSocketMessage) => void) {
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Create WebSocket connection
    ws.current = new WebSocket(url);

    // Connection opened
    ws.current.addEventListener('open', () => {
      console.log('WebSocket connection established');
    });

    // Listen for messages
    ws.current.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    });

    // Connection closed
    ws.current.addEventListener('close', () => {
      console.log('WebSocket connection closed');
    });

    // Connection error
    ws.current.addEventListener('error', (error) => {
      console.error('WebSocket error:', error);
    });

    // Cleanup on unmount
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url, onMessage]);

  return ws.current;
} 