import express from "express";
const app = express();

app.get("/should_start", (req, res) => {
  res.set("Connection", "close"); // important for Pico
  res.set("Transfer-Encoding", "identity"); // disable chunked
  res.json({ brew: true });
});

app.get("/", (req, res) => {
  res.send("Coffee backend is alive");
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log("Server running on", PORT));
