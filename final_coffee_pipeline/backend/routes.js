import express from "express";
import { sendCommand, sendCoffeeTimerToPico } from "./mqttClient.js";
import { dbPromise, getStatus } from "./server.js";

export const router = express.Router();

router.get("/", (req, res) => {
  res.json({ message: "Backend is alive!" });
});

router.get("/status", (req, res) => {
  const status = getStatus();
  res.json(status);
});

router.get("/latest-temps", async (req, res) => {
  try {
    const now = new Date();
    const db = await dbPromise;
    const rows = await db.all(
      `
      SELECT * 
      FROM temperatures 
      WHERE timestamp >= datetime(?, '-10 minutes')
      ORDER BY timestamp ASC
    `,
      now.toISOString()
    );

    // Convert UTC timestamps to GMT+3
    const convertedRows = rows.map((row) => {
      const utcDate = new Date(row.timestamp + "Z");
      const gmt3Date = new Date(utcDate.getTime());
      return {
        ...row,
        timestamp: gmt3Date.toISOString(),
      };
    });

    res.json(convertedRows);
  } catch (err) {
    console.error("❌ Failed to fetch latest temperatures:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

router.post("/brew-now", (req, res) => {
  const cups = req.body.cups;
  if (!cups || typeof cups !== "number" || cups < 1 || cups > 12) {
    return res.status(400).json({ message: "Invalid number of cups" });
  }
  const duration = 5 + (cups - 4) / 2; // 4 cups = 5 min, +0.5 min per extra cup

  console.log("Brew coffee request received");
  const command = { command: "MAKE_COFFEE_NOW", param: { cups, duration } };
  const response = sendCommand(command);
  res.json(response);
});

router.post("/set-timer", (req, res) => {
  const cups = req.body.cups;
  const datetime = req.body.datetime; // should be ISO string
  if (!cups || typeof cups !== "number" || cups < 1 || cups > 12) {
    return res.status(400).json({ message: "Invalid number of cups" });
  }
  const durationMinutes = 5 + (cups - 4) / 2; // 4 cups = 5 min, +0.5 min per extra cup

  console.log("Received timer request:", req.body);

  // ✅ Convert to Date first
  const userDate = new Date(datetime);
  if (isNaN(userDate.getTime())) {
    return res.status(400).json({ message: "Invalid date format" });
  }

  // ✅ Subtract duration (in ms)
  const startTimestamp = userDate.getTime() - durationMinutes * 60 * 1000;
  const coffeeTimer = new Date(startTimestamp);

  // ✅ Check it's not in the past
  if (coffeeTimer < new Date()) {
    return res.status(400).json({ message: "Cannot set timer in the past" });
  }

  console.log("Adjusted start time:", coffeeTimer.toISOString());

  sendCoffeeTimerToPico(coffeeTimer, cups, durationMinutes);
  res.json({ message: `Coffee timer set for ${coffeeTimer}` });
});
