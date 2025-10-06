import { useEffect } from "react";

export default function Chart({ chartData, setChartData }) {
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    // Fetch initial data once
    fetch(`${API_URL}/latest-temps`)
      .then((res) => res.json())
      .then((data) => {
        const newChartData = [
          ["Time", "Temperature (°C)"],
          ...data.map((row) => [
            new Date(row.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
              hour12: false,
            }),
            row.value,
          ]),
        ];
        setChartData(newChartData);
      })
      .catch((err) => console.error("Error fetching temperatures:", err));
  }, []);

  useEffect(() => {
    // If google isn't ready yet, wait until it is
    if (!window.google) return;

    let chart; // keep reference
    let cancelled = false;

    const drawChart = () => {
      if (cancelled) return;
      if (!window.google.visualization) return;

      const safeData =
        chartData.length > 1
          ? chartData
          : [
              ["Time", "Temperature (°C)"],
              ["", 0],
            ];

      const data = window.google.visualization.arrayToDataTable(safeData);

      const options = {
        title: "Temperature (last 10 min)",
        curveType: "function",
        legend: { position: "bottom", textStyle: { color: "#58a6ff" } },
        backgroundColor: "transparent",
        titleTextStyle: { color: "#58a6ff" },
        hAxis: {
          textStyle: { color: "#9ba3b4" },
          slantedText: false,
          gridlines: { count: 10 },
          showTextEvery: 6,
        },
        vAxis: {
          minValue: 15,
          maxValue: 80,
          textStyle: { color: "#9ba3b4" },
        },
        chartArea: {
          left: "8%",
          right: "3%",
          top: "10%",
          bottom: "25%",
          width: "89%",
          height: "65%",
        },
      };

      const container = document.getElementById("temperature-chart");
      if (!container) return;

      chart = new window.google.visualization.LineChart(container);
      chart.draw(data, options);
    };

    // ✅ Ensure the library is loaded before drawing
    window.google.charts.load("current", { packages: ["corechart"] });
    window.google.charts.setOnLoadCallback(drawChart);

    // cleanup
    return () => {
      cancelled = true;
    };
  }, [chartData]);

  return (
    <section className="chart-section">
      <h2>Temperature</h2>
      <div id="temperature-chart" style={{ width: "100%", height: "300px" }} />
    </section>
  );
}
