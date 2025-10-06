import { io } from "socket.io-client";

// Pick your backend URL (adjust for local vs deployed)
const URL =
  import.meta.env.MODE === "development"
    ? "http://10.85.140.16:4000"
    : "https://your-backend.onrender.com";

// Create ONE socket instance and export it
export const socket = io(URL, {
  transports: ["websocket"],
  autoConnect: true,
});
