import { WebSocketServer } from "ws";

const server = new WebSocketServer({ port: 8080 });

server.on("connection", (socket) => {
  console.log("New client connected");

  socket.on("message", (message) => {
    console.log(`Received: ${message}`);
    socket.send(message);
  });

  socket.on("close", () => {
    console.log("Client disconnected");
  });
});
