import { useEffect, useState } from "react";
import { socket } from "./socket";
import StatusSection from "./components/StatusSection";
import Chart from "./components/Chart";
import Controlls from "./components/Controlls";
import Feedback from "./components/Feedback";

function App() {
  const [chartData, setChartData] = useState([["Time", "Temperature (°C)"]]);
  const [scheduleTime, setScheduleTime] = useState("");
  const [selectedCups, setSelectedCups] = useState(null);
  const [isSending, setIsSending] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState({
    text: "",
    type: "success",
    visible: false,
  });

  // Socket event handlers
  useEffect(() => {
    socket.on("connect", () => {
      console.log("✅ Connected to Socket.IO server");
    });

    socket.on("temperature_update", (data) => {
      setChartData((prevData) => {
        console.log("🌡️ New temperature data:", data);
        const newPoint = [
          new Date(data.time).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            hour12: false,
          }),
          data.value,
        ];
        // Keep header, slice to last 59 points, then add new
        const header = prevData[0];
        const points = prevData.slice(1);
        const updatedPoints =
          points.length >= 59
            ? [...points.slice(1), newPoint]
            : [...points, newPoint];

        console.log("🌡️ New datapoints:", updatedPoints);
        return [header, ...updatedPoints];
      });
    });

    socket.on("disconnect", () => {
      console.log("❌ Disconnected from Socket.IO server");
    });

    // Cleanup when component unmounts
    return () => {
      socket.off("connect");
      socket.off("temperature_update");
      socket.off("disconnect");
    };
  }, []);

  // Send immediate brew command
  const brewNow = async () => {
    if (!selectedCups) {
      showFeedback("Please select number of cups first", "error");
      return;
    }

    setIsSending(true);
    showFeedback(`Brewing ${selectedCups} cups of coffee...`, "success");
    try {
      const res = await fetch("http://10.85.140.16:4000/brew-now", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cups: selectedCups }),
      });
      const data = await res.json();
    } catch (err) {
      console.log(err);
      showFeedback("Error sending command", "error");
    } finally {
      setIsSending(false);
    }
  };

  const scheduleBrew = async () => {
    if (!scheduleTime) {
      showFeedback("Please select a time", "error");
      return;
    }

    if (!selectedCups) {
      showFeedback("Please select number of cups first", "error");
      return;
    }

    setIsSending(true);
    try {
      const res = await fetch("http://10.85.140.16:4000/set-timer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ datetime: scheduleTime, cups: selectedCups }),
      });
      const data = await res.json();
      if (
        res.status === 400 &&
        data.message === "Cannot set timer in the past"
      ) {
        showFeedback("Cannot set timer in the past", "error");
        return;
      } else if (res.status === 400 && data.message === "Invalid date format") {
        showFeedback("Invalid date format", "error");
        return;
      }
      showFeedback(
        `Scheduled ${selectedCups} cups for ${new Date(
          scheduleTime
        ).toLocaleString()}`,
        "success"
      );
    } catch (err) {
      alert("Error scheduling brew");
    } finally {
      setIsSending(false);
    }
  };

  // Helper to show feedback messages
  const showFeedback = (message, type = "success") => {
    setFeedbackMessage({ text: message, type, visible: true });

    // Auto-hide after 10 seconds
    setTimeout(() => {
      setFeedbackMessage((prev) => ({ ...prev, visible: false }));
    }, 7000);
  };

  return (
    <div className="app-wrapper">
      <main className="coffee-app">
        <h1>☕ Smart Coffee</h1>

        <StatusSection />

        <Chart chartData={chartData} setChartData={setChartData} />

        <Controlls
          brewNow={brewNow}
          scheduleBrew={scheduleBrew}
          scheduleTime={scheduleTime}
          setScheduleTime={setScheduleTime}
          selectedCups={selectedCups}
          setSelectedCups={setSelectedCups}
          isSending={isSending}
        />
      </main>

      <Feedback feedbackMessage={feedbackMessage} />
    </div>
  );
}

export default App;
