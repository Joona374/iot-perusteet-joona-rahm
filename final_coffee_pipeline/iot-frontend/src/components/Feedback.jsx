export default function Feedback({ feedbackMessage }) {
  return (
    <p
      className={`feedback-message ${feedbackMessage.type} ${
        feedbackMessage.visible ? "show" : "hide"
      }`}
    >
      {feedbackMessage.text}
    </p>
  );
}
