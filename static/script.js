// Client-side JavaScript for Enhanced UI - Chat, Charts, AJAX

// Chatbot functionality
function sendChatMessage() {
  const message = document.getElementById("chat-input").value;
  if (!message.trim()) return;

  // Display user message
  addChatMessage("You", message);

  // AJAX to Flask /chat
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: message }),
  })
    .then((response) => response.json())
    .then((data) => addChatMessage("AI Bot", data.response))
    .catch((error) => addChatMessage("AI Bot", "Sorry, try again!"));

  document.getElementById("chat-input").value = "";
}

function addChatMessage(sender, message) {
  const chatBox = document.getElementById("chat-box");
  const messageDiv = document.createElement("div");
  messageDiv.className =
    sender === "You" ? "chat-message user" : "chat-message bot";
  messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Chart.js Dashboard for Career Demand
function renderCareerChart(topCareers) {
  const ctx = document.getElementById("careerChart").getContext("2d");
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: topCareers.map((c) => c[0].replace("_", " ").toUpperCase()),
      datasets: [
        {
          data: topCareers.map((c) => c[1]),
          backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
      },
    },
  });
}

// Personality Test Logic
function submitPersonalityTest() {
  const answers = [];
  for (let i = 1; i <= 10; i++) {
    answers.push(document.querySelector(`input[name="q${i}"]:checked`).value);
  }

  fetch("/personality", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers: answers }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("personality-result").innerHTML =
        `Recommended Career: <strong>${data.career}</strong> (Score: ${data.score})`;
    });
}

// Resume Upload AJAX
function uploadResume() {
  const fileInput = document.getElementById("resume-file");
  const formData = new FormData();
  formData.append("resume", fileInput.files[0]);

  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("resume-analysis").innerHTML = `
            <h4>Detected Skills:</h4>
            <ul>${Object.entries(data.skills)
              .map(([cat, count]) => `<li>${cat}: ${count}</li>`)
              .join("")}</ul>
            <h4>Score: ${data.score}%</h4>
            <h4>Recommendations:</h4>
            <ul>${data.recommendations.map((r) => `<li>${r}</li>`).join("")}</ul>
        `;
    });
}

// Initialize on load
document.addEventListener("DOMContentLoaded", function () {
  // Chat enter key
  document
    .getElementById("chat-input")
    .addEventListener("keypress", function (e) {
      if (e.key === "Enter") sendChatMessage();
    });

  // Smooth scrolling for tabs
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute("href")).scrollIntoView({
        behavior: "smooth",
      });
    });
  });
});
