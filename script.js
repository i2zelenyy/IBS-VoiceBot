// =============================
// voicebot script.js (mit Web Speech API + Fake Server)
// =============================

// === FAKE SERVER SETUP ===
(function simulateFakeServer() {
  const originalFetch = window.fetch;

  window.fetch = async (input, init) => {
    if (typeof input === 'string' && input === '/api/fake-voicebot') {
      const requestBody = JSON.parse(init.body);
      const userMessage = requestBody.message;

      let botResponse = "Ich habe dich leider nicht verstanden.";
      if (userMessage.includes("Wetter")) {
        botResponse = "Heute ist es sonnig mit 20 °C.";
      } else if (userMessage.includes("Name")) {
        botResponse = "Ich heiße VoiceBot, nett dich kennenzulernen!";
      }

      return Promise.resolve({
        json: async () => ({ response: botResponse })
      });
    }
    return originalFetch(input, init);
  };
})();

// === SPRACHERKENNUNG ===
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = "de-DE";
recognition.interimResults = false;
recognition.maxAlternatives = 1;

let userMessage = "";

// === UI HANDLING ===
document.getElementById("recordBtn").addEventListener("click", () => {
  recognition.start();
  document.getElementById("userInput").textContent = "Höre zu...";
});

recognition.onresult = (event) => {
  userMessage = event.results[0][0].transcript;
  document.getElementById("userInput").textContent = userMessage;

  fetch("/api/fake-voicebot", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage })
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("botResponse").textContent = data.response;
    });
};

recognition.onerror = (event) => {
  document.getElementById("userInput").textContent = "Fehler: " + event.error;
};

document.getElementById("playBtn").addEventListener("click", () => {
  const msg = new SpeechSynthesisUtterance();
  msg.text = document.getElementById("botResponse").textContent;
  window.speechSynthesis.speak(msg);
});

document.getElementById("settingsBtn").addEventListener("click", () => {
  alert("Einstellungen sind noch nicht implementiert.");
});
