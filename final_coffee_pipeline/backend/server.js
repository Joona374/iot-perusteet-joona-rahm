import express from "express";
import cors from "cors";
import { router } from "./routes.js";
import { initMqtt, sendCommand } from "./mqttClient.js";
import { initDb } from "./db.js";
import { Server } from "socket.io";
import http, { get } from "http";

const app = express();
const server = http.createServer(app); // needed for socket.io
export const io = new Server(server, {
  cors: { origin: "*" },
});

app.use(cors());
app.use(express.json());
app.use("/", router);

const PORT = process.env.PORT || 4000;

let serverStatus = "Connected";
let deviceStatus = "Connecting...";

export const setDeviceStatus = (status) => {
  deviceStatus = status;
};

export const setServerStatus = (status) => {
  serverStatus = status;
};

export const getDeviceStatus = () => deviceStatus;
export const getServerStatus = () => serverStatus;

// Function to get current status and send CHECK_STATUS command
export const getStatus = () => (
  sendCommand({ command: "CHECK_STATUS", param: {} }),
  { server: serverStatus, device: deviceStatus }
);

// === INIT SEQUENCE ===
export const dbPromise = initDb(); // Promise for db handle
initMqtt();

// Socket.IO handlers
io.on("connection", (socket) => {
  console.log(`\n${new Date().toLocaleString()} - 🧠 New client connected`);

  socket.on("disconnect", () => {
    console.log(`\n${new Date().toLocaleString()} - ❌ Client disconnected`);
  });
});

server.listen(PORT, () => {
  console.log(
    `\n${new Date().toLocaleString()} - 🚀 Server listening on port ${PORT}`
  );
});
