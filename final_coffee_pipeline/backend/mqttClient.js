import mqtt from "mqtt";
import { handleTemp, handleStatus } from "./handlers.js";

const broker = "mqtt://test.mosquitto.org:1883";
const topicSub = "iot/demo/responses";
const topicPub = "iot/demo/commands";

let client;

export function initMqtt() {
  client = mqtt.connect(broker);

  client.on("connect", () => {
    console.log(`✅ Connected to ${broker}`);

    client.subscribe(topicSub, (err) => {
      if (err) console.error("❌ Subscribe error:", err);
      else console.log(`📡 Subscribed to: ${topicSub}`);
    });
  });

  // Handle incoming messages (if you want to see what Pico publishes)
  client.on("message", async (topic, message) => {
    try {
      const msgObj = JSON.parse(message.toString());
      // console.log(`${new Date().toLocaleString()} - 📥 ${topic}:`, msgObj);

      switch (msgObj.type) {
        case "TEMP":
          await handleTemp(msgObj.param);
          break;

        case "GET_TIME":
          sendTimeToPico();
          break;

        case "STATUS":
          handleStatus(msgObj.param);
          break;

        default:
          console.log("Unknown message type:", msgObj.type);
      }
    } catch (e) {
      console.error("Failed to parse message as JSON:", message.toString());
      console.error("Raw message buffer:", message);
      console.error("Message length:", message.length);
      console.error("Parse error details:", e.message);
      return;
    }
  });

  // Optional: handle connection errors
  client.on("error", (err) => {
    console.error("Broker error:", err);
  });
}

export function sendCommand(command) {
  if (!client) return { error: "MQTT not initialized" };

  const payload = JSON.stringify(command);
  client.publish(topicPub, payload);

  return { message: "Command sent to Pico W!" };
}

export function sendTimeToPico() {
  const now = new Date();
  const param = {
    y: now.getFullYear(),
    m: now.getMonth() + 1, // JS months are 0–11
    d: now.getDate(),
    H: now.getHours(),
    M: now.getMinutes(),
    S: now.getSeconds(),
  };

  const command = { command: "SET_TIME", param };
  sendCommand(command);
}

export function sendCoffeeTimerToPico(dateObj, cups, duration) {
  if (!(dateObj instanceof Date)) return console.error("Invalid dateObj");
  const param = {
    y: dateObj.getFullYear(),
    m: dateObj.getMonth() + 1,
    d: dateObj.getDate(),
    H: dateObj.getHours(),
    M: dateObj.getMinutes(),
    S: dateObj.getSeconds(),
    cups,
    duration,
  };
  sendCommand({ command: "SET_TIMER", param });
}
