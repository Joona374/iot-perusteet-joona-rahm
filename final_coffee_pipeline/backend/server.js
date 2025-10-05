import mqtt from "mqtt";

const broker = "mqtt://test.mosquitto.org:1883";
const topicSub = "iot/demo/responses";
const topicPub = "iot/demo/commands"; // the topic your Pico subscribes to

import express from "express";
const app = express();
const port = process.env.PORT || 4000;

app.get("/", (req, res) => {
  res.send("Hello World!");
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});

// Connect to the broker
const client = mqtt.connect(broker);

client.on("connect", () => {
  console.log(`✅ Connected to ${broker}`);

  // Subscribe to a topic (optional)
  client.subscribe(topicSub, (err) => {
    if (err) console.error("❌ Subscribe error:", err);
    else console.log(`📡 Subscribed to: ${topicSub}`);
  });

  // Publish a test message every 5 seconds
  setInterval(() => {
    const payload = `Hello Pico! ${new Date().toLocaleTimeString()}`;
    client.publish(topicPub, payload);
    console.log(`📤 Published to ${topicPub}: ${payload}`);
  }, 5000);
});

// Handle incoming messages (if you want to see what Pico publishes)
client.on("message", (topic, message) => {
  console.log(`📥 ${topic}: ${message.toString()}`);
});

// Optional: handle connection errors
client.on("error", (err) => {
  console.error("Broker error:", err);
});
