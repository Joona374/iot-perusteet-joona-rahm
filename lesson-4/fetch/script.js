const url =
  "https://api.thingspeak.com/channels/3097334/feeds.json?api_key=Y8I90RIIW60XI3KY";

const logDiv = document.getElementById("log");

function fetchData() {
  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      const feeds = data.feeds;
      const dataPoints = feeds.map((feed) => ({
        time: feed.created_at,
        temp: parseFloat(feed.field1),
      }));
      logDiv.textContent = JSON.stringify(dataPoints, null, 2);
    });
}
