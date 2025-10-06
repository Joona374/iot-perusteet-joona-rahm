export default function Controlls({
  brewNow,
  scheduleBrew,
  scheduleTime,
  setScheduleTime,
  selectedCups,
  setSelectedCups,
  isSending,
}) {
  const cupOptions = [4, 6, 8, 10, 12];

  return (
    <section className="controls">
      <h2>Controls</h2>

      <div className="cup-selection">
        <h3>Number of Cups</h3>
        <div className="cup-buttons">
          {cupOptions.map((cups) => (
            <button
              key={cups}
              className={`cup-button ${
                selectedCups === cups ? "selected" : ""
              }`}
              onClick={() => setSelectedCups(cups)}
              disabled={isSending}
            >
              {cups}
            </button>
          ))}
        </div>
      </div>

      <button className="brew-now" onClick={brewNow} disabled={isSending}>
        {isSending ? "Sending..." : "☕ Brew Now"}
      </button>

      <div className="timer-controls">
        <div className="time-input-wrapper">
          <label>Schedule Time When Coffee is Ready:</label>
          <input
            type="datetime-local"
            value={scheduleTime}
            onChange={(e) => setScheduleTime(e.target.value)}
          />
        </div>
        <button onClick={scheduleBrew} disabled={isSending}>
          ⏰ Set Timer
        </button>
      </div>
    </section>
  );
}
