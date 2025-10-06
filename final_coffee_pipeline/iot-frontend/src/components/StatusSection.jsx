import { useState, useEffect } from "react";

export default function StatusSection() {
  const [deviceStatus, setDeviceStatus] = useState("Connecting...");
  const [serverStatus, setServerStatus] = useState("Connecting...");

  const API_URL = import.meta.env.VITE_API_URL;

  // Fetch system status
  useEffect(() => {
    const fetchStatus = () => {
      fetch(`${API_URL}/status`)
        .then((res) => res.json())
        .then((data) => {
          setDeviceStatus(data.device || "Unknown");
          setServerStatus(data.server || "Unknown");
          if (data.temperature) setTemperature(data.temperature);
        })
        .catch(() => setStatus("Error connecting to backend"));
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="status-card">
      <h2>Status</h2>
      <p>
        <strong>Device:</strong> {deviceStatus}
      </p>
      <p>
        <strong>Server:</strong> {serverStatus}
      </p>
    </section>
  );
}
