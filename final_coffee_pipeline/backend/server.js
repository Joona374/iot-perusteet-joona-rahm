import express from "express";
import { WebSocketServer } from "ws";

const app = express();
const PORT = 3000;

// Basic REST for testing
app.get("/", (req, res) => {
  res.send("Coffee backend running ☕");
});

const server = app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
// BASIC REST FOR TESTING

const wss = new WebSocketServer({ server });

wss.on("connection", (socket) => {
  console.log("Pico connected via socket");

  socket.on("message", (data) => {
    console.log("Received data from Pico:", data.toString());
    // Echo the data back to the client
    socket.send(`Server received: ${data}`);
  });

  socket.on("close", () => {
    console.log("Pico disconnected");
  });

  setInterval(() => {
    socket.send(JSON.stringify({ action: "brew" }));
  }, 10000);
});
