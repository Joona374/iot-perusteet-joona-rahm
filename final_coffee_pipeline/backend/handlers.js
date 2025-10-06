import { io } from "./server.js";
import { dbPromise, setDeviceStatus } from "./server.js";

function getSqliteTimestamp() {
  return new Date().toISOString().slice(0, 19).replace("T", " ");
}

export async function handleTemp(tempValue) {
  try {
    const db = await dbPromise;
    await db.run("INSERT INTO temperatures (value) VALUES (?)", [tempValue]);

    // Emit to all connected clients
    io.emit("temperature_update", { value: tempValue, time: new Date() });
  } catch (err) {
    console.error("❌ handleTemp failed:", err);
  }
}

export function handleStatus(param) {
  if (!param) return console.error("No status param received");
  if (param === "IDLE") {
    setDeviceStatus("Idle, waiting for timer");
  } else if (param.STATUS === "TIMER_SET") {
    // param.TIME is [year, month, day, weekday, hour, minute, second, ms]
    const [year, month, day, , hour, minute, second] = param.TIME;
    const timerDate = new Date(year, month - 1, day, hour, minute, second);
    setDeviceStatus(
      `Timer set to start brewing at ${timerDate.toLocaleString()}`
    );
  } else if (param.STATUS === "MAKING_COFFEE") {
    setDeviceStatus("Brewing coffee, time remaining: " + param.TIME_LEFT + "s");
  } else if (param.STATUS === "COFFEE_DONE") {
    setDeviceStatus("Coffee is ready!");
  }
}
