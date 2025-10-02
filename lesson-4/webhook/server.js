import express, { response } from "express";
const app = express();
const port = 3000;

const WEBHOOK_URL =
  "https://discord.com/api/webhooks/1423328790385397900/PvgemR5g5Zq2Zf3tUVyEjGRV17rMjXnjvf-uyIiinloCNegEbC9j-3xyw-hzoUbynnGr";
app.use(express.json());

app.post("/notify", (req, res) => {
  const { message } = req.body;

  if (!message) {
    return res.status(400).json({ error: "Message is required" });
  }

  fetch(WEBHOOK_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: message }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to send message: " + response.status);
      }
      res.json({ status: "Message sent" });
    })
    .catch((error) => {
      console.error("Error sending to Discord: " + error);
      res.status(500).json({ error: "Internal Server Error" });
    });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
