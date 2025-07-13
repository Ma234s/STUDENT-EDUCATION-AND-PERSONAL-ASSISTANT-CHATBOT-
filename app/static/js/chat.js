// Pure-JS rule-based chatbot for demo/testing
const responseRules = [
  { re: /^(hi|hello|hey)\b/i, reply: "Hello! I'm Naira, your educational assistant." },
  { re: /\b(homework|assignment)\b/i, reply: "Sure—what subject are you working on?" },
  { re: /\b(thanks|thank you)\b/i, reply: "You're welcome!" },
  { re: /\b(bye|goodbye)\b/i, reply: "Goodbye! If you need more help, just let me know." }
];

function getBotResponse(msg) {
  for (let {re,reply} of responseRules)
    if (re.test(msg)) return reply;
  return "I'm sorry, I don't understand. Can you rephrase?";
}

let history = [];
function render() {
  const chat = document.getElementById("chat");
  chat.innerHTML = "";
  history.forEach(entry => {
    const div = document.createElement("div");
    div.className = "msg " + (entry.role === "user" ? "user" : "bot");
    div.textContent = entry.content;
    chat.append(div);
  });
  chat.scrollTop = chat.scrollHeight;
}

function send() {
  const inp = document.getElementById("input");
  const text = inp.value.trim();
  if (!text) return;
  history.push({ role: "user", content: text });
  render();
  inp.value = "";
  const botReply = getBotResponse(text);
  history.push({ role: "bot", content: botReply });
  render();
}

document.getElementById("send").onclick = send;
document.getElementById("input").addEventListener("keydown", e => {
  if (e.key === "Enter") send();
});

render(); 