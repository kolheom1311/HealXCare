const chatBody = document.querySelector(".chat-body");
const messageInput = document.querySelector(".message-input");
const sendMessage = document.querySelector("#send-message");
const fileInput = document.querySelector("#file-input");
const fileUploadWrapper = document.querySelector(".file-upload-wrapper");
const fileCancelButton = fileUploadWrapper.querySelector("#file-cancel");
const chatbotToggler = document.querySelector("#chatbot-toggler");
const closeChatbot = document.querySelector("#close-chatbot");
// API setup
const API_KEY = "AIzaSyBc1w_B8gO7_lF3Y2U7Hwyyz_OnceTr_1c";
const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=${API_KEY}`;
// Initialize user message and file data
const userData = {
    message: null,
    file: {
        data: null,
        mime_type: null,
    },
};
// Store chat history
let chatHistory = [];
const initialInputHeight = messageInput.scrollHeight;

const loadChatHistory = () => {
    const storedHistory = localStorage.getItem("chatHistory");
    if (storedHistory) {
        chatHistory = JSON.parse(storedHistory);
        chatHistory.forEach(chat => {
            let textContent = `<div class="message-text">${chat.parts[0].text}</div>`;
            let fileContent = chat.parts[1]?.inline_data
                ? `<img src="data:${chat.parts[1].inline_data.mime_type};base64,${chat.parts[1].inline_data.data}" class="attachment" />`
                : "";
            
            // Check if the message is from the bot (role: "model") and add avatar
            if (chat.role === "model") {
                textContent = `
                    <img class="bot-avatar" src="static/HealthStack-System/images/Normal/favicon.png" alt="efe" width="50" height="50">
                    ${textContent}
                `;
            }

            const messageDiv = createMessageElement(textContent + fileContent, chat.role === "user" ? "user-message" : "bot-message");
            chatBody.appendChild(messageDiv);
        });
    }
};

// Save chat history to local storage
const saveChatHistory = () => {
    localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
};

// Create message element with dynamic classes and return it
const createMessageElement = (content, ...classes) => {
    const div = document.createElement("div");
    div.classList.add("message", ...classes);
    div.innerHTML = content;
    return div;
};

const handleOutgoingMessage = (e) => {
    e.preventDefault();
    userData.message = messageInput.value.trim();
    messageInput.value = "";
    messageInput.dispatchEvent(new Event("input"));
    fileUploadWrapper.classList.remove("file-uploaded");

    // Create message content with optional image
    const messageContent = `<div class="message-text"></div>
                          ${userData.file.data ? `<img src="data:${userData.file.mime_type};base64,${userData.file.data}" class="attachment" />` : ""}`;
    const outgoingMessageDiv = createMessageElement(messageContent, "user-message");
    outgoingMessageDiv.querySelector(".message-text").innerText = userData.message;
    chatBody.appendChild(outgoingMessageDiv);
    chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });

    // Store message and file in chat history
    chatHistory.push({
        role: "user",
        parts: [{ text: userData.message }, ...(userData.file.data ? [{ inline_data: userData.file }] : [])],
    });

    // Save chat history
    saveChatHistory();

    // Simulate bot response with thinking indicator after a delay
    setTimeout(() => {
        const messageContent = `<img class="bot-avatar" src="static/HealthStack-System/images/Normal/favicon.png" alt="efe" width="50" height="50">
          <div class="message-text">
            <div class="thinking-indicator">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>`;
        const incomingMessageDiv = createMessageElement(messageContent, "bot-message", "thinking");
        chatBody.appendChild(incomingMessageDiv);
        chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
        generateBotResponse(incomingMessageDiv);
    }, 600);
};

const generateBotResponse = async (incomingMessageDiv) => {
    const messageElement = incomingMessageDiv.querySelector(".message-text");

    // Define the system instruction (meta prompt)
    const systemInstruction = "You are HealthBot, designed to assist users with health-related inquiries. Respond only to health questions and acknowledge greetings. If the user sends a file, acknowledge the file and provide a health-related response. If the user message is not regarding health, respond with a generic health-related message.";

    const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            system_instruction: {
                role: "system",
                    "parts": [
                        {
                            "text": `You are Heal Mitra, an AI assistant developed by HealXCare—a trusted provider of innovative healthcare solutions. Your mission is to assist users with health-related inquiries while promoting the benefits of HealXCare's services.  
                
                            🌟 **ABOUT HEALXCARE** 🌟  
                            - HealXCare is dedicated to enhancing healthcare accessibility with AI-driven support.  
                            - We offer expert guidance on medical advice, wellness, fitness, nutrition, and mental health.  
                            - Our solutions help users stay informed, monitor their health, and make better wellness decisions.  
                
                            🚫 **STRICT RULES: STAY ON TOPIC** 🚫  
                            - ❌ **Reject all non-health-related questions immediately.**  
                            - ❌ **Do NOT provide information on general knowledge, geography, coding, history, or finance.**  
                            - ❌ **If a user asks something unrelated to health, reply:**  
                              👉 *"I can only assist with health-related inquiries. Please ask me something about health and wellness."*  
                            - ❌ **If the user insists, do not engage. Simply repeat your refusal.**  
                
                            ✅ **HOW TO ASSIST USERS** ✅  
                            - If the question is about **medical advice, wellness, fitness, nutrition, or mental health**, answer normally and mention how HealXCare helps in these areas.  
                            - If the user sends a file, acknowledge it and ask how you can assist with their health concerns.  
                            - For greetings (e.g., 'hi', 'hello'), respond warmly and encourage a health-related discussion.  
                            - Keep responses **concise** (max 4-5 lines). If a user describes symptoms, always **suggest consulting a doctor** while highlighting HealXCare’s supportive role.  
                
                            🚨 **EXAMPLES (STRICTLY FOLLOW)** 🚨  
                            - Allowed: *"What are the symptoms of COVID-19?"* → ✅ Provide health information and mention how HealXCare supports COVID-19 awareness.  
                            - Blocked: *"Where is the Taj Mahal?"* → ❌ "I can only assist with health-related inquiries. Please ask me something about health and wellness."  
                            - Blocked: *"Write a Python script for sorting numbers."* → ❌ "I specialize in health and wellness. Let me know if you need guidance on a health topic!"  
                            - Blocked: *"Tell me a joke!"* → ❌ "I'm here to provide health information. Let me know if you need guidance on a health topic."  
                            
                            🔹 **PROMOTE HEALXCARE** 🔹  
                            Whenever relevant, mention HealXCare’s role in providing AI-powered health assistance, connecting users with medical professionals, and offering reliable wellness insights.`
                        }
                    ]                                                                                  
            },
            contents: chatHistory,
        }),
    };
    try {
        // Fetch bot response from API
        const response = await fetch(API_URL, requestOptions);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error.message);

        // Extract and display bot's response text
        const apiResponseText = data.candidates[0].content.parts[0].text.replace(/\*\*(.*?)\*\*/g, "$1").trim();
        messageElement.innerText = apiResponseText;

        // Add bot response to chat history
        chatHistory.push({
            role: "model",
            parts: [{ text: apiResponseText }],
        });

        // Save updated chat history
        saveChatHistory();
    } catch (error) {
        console.log(error);
        messageElement.innerText = error.message;
        messageElement.style.color = "#ff0000";
    } finally {
        // Reset user's file data and scroll chat to bottom
        userData.file = { data: null, mime_type: null };
        incomingMessageDiv.classList.remove("thinking");
        chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
    }
};


// Adjust input field height dynamically
messageInput.addEventListener("input", () => {
    messageInput.style.height = `${initialInputHeight}px`;
    messageInput.style.height = `${messageInput.scrollHeight}px`;
    document.querySelector(".chat-form").style.borderRadius = messageInput.scrollHeight > initialInputHeight ? "15px" : "32px";
});

// Handle Enter key press for sending messages
messageInput.addEventListener("keydown", (e) => {
    const userMessage = e.target.value.trim();
    if (e.key === "Enter" && !e.shiftKey && userMessage && window.innerWidth > 768) {
        handleOutgoingMessage(e);
    }
});

// Handle file input change and preview the selected file
fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        fileInput.value = "";
        fileUploadWrapper.querySelector("img").src = e.target.result;
        fileUploadWrapper.classList.add("file-uploaded");
        const base64String = e.target.result.split(",")[1];
        // Store file data in userData
        userData.file = {
            data: base64String,
            mime_type: file.type,
        };
    };
    reader.readAsDataURL(file);
});

// Cancel file upload
fileCancelButton.addEventListener("click", () => {
    userData.file = {};
    fileUploadWrapper.classList.remove("file-uploaded");
});

// Initialize emoji picker and handle emoji selection
const picker = new EmojiMart.Picker({
    theme: "light",
    skinTonePosition: "none",
    previewPosition: "none",
    onEmojiSelect: (emoji) => {
        const { selectionStart: start, selectionEnd: end } = messageInput;
        messageInput.setRangeText(emoji.native, start, end, "end");
        messageInput.focus();
    },
    onClickOutside: (e) => {
        if (e.target.id === "emoji-picker") {
            document.body.classList.toggle("show-emoji-picker");
        } else {
            document.body.classList.remove("show-emoji-picker");
        }
    },
});
document.querySelector(".chat-form").appendChild(picker);
sendMessage.addEventListener("click", (e) => handleOutgoingMessage(e));
document.querySelector("#file-upload").addEventListener("click", () => fileInput.click());
closeChatbot.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));

// Call loadChatHistory on page load
window.onload = loadChatHistory;