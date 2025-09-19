document.addEventListener('DOMContentLoaded', () => {
    // --- Get all the HTML elements ---
    const menuBtn = document.getElementById('menu-btn');
    const sidebar = document.getElementById('sidebar');
    const newChatBtn = document.getElementById('new-chat-btn');
    const historySidebar = document.getElementById('history-sidebar');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatBox = document.getElementById('chat-box');
    const micBtn = document.getElementById('mic-btn');

    let currentSessionId = null;

    // --- MENU TOGGLE LOGIC ---
    menuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    // --- SESSION AND HISTORY MANAGEMENT ---
    const loadHistorySidebar = async () => {
        try {
            const response = await fetch('/list_chats');
            const chatIds = await response.json();
            
            const existingLinks = historySidebar.querySelectorAll('.history-link');
            existingLinks.forEach(link => link.remove());

            chatIds.forEach(id => {
                const link = document.createElement('a');
                link.href = '#';
                link.textContent = `Chat ${id.substring(0, 8)}...`;
                link.classList.add('history-link');
                link.dataset.sessionId = id;
                
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    loadChat(id);
                    if (window.innerWidth < 768) { // Close sidebar on mobile after click
                        sidebar.classList.remove('open');
                    }
                });
                
                historySidebar.appendChild(link);
            });
        } catch (error) {
            console.error('Failed to load history sidebar:', error);
        }
    };

    const loadChat = async (sessionId) => {
        try {
            const response = await fetch(`/load_chat/${sessionId}`);
            const history = await response.json();
            chatBox.innerHTML = '';
            history.forEach(message => {
                appendMessage(message.sender, message.text);
            });
            currentSessionId = sessionId;
        } catch (error) {
            console.error('Failed to load chat:', error);
        }
    };

    const startNewChat = async () => {
        try {
            const response = await fetch('/start_chat', { method: 'POST' });
            const data = await response.json();
            currentSessionId = data.session_id;
            chatBox.innerHTML = '';
            appendMessage('bot', 'Hello! How can I help you today?');
            await loadHistorySidebar(); // Refresh sidebar after starting a new chat
        } catch (error) {
            console.error('Failed to start a new chat:', error);
        }
    };

    // --- CORE CHAT FUNCTIONALITY ---
    const sendMessage = async () => {
        const messageText = userInput.value.trim();
        if (messageText === '' || !currentSessionId) return;
        appendMessage('user', messageText);
        userInput.value = '';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message: messageText, session_id: currentSessionId })
            });
            const data = await response.json();
            appendMessage('bot', data.response);
            speakText(data.response);
        } catch (error) {
            console.error('Error:', error);
            appendMessage('bot', 'Sorry, something went wrong.');
        }
    };
    
    const appendMessage = (sender, text) => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', sender);
        const p = document.createElement('p');
        p.textContent = text;
        messageDiv.appendChild(p);
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    };
    
    // --- VOICE ASSISTANT FUNCTIONALITY ---
    const speakText = (text) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        window.speechSynthesis.speak(utterance);
    };

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        micBtn.addEventListener('click', () => {
            recognition.start();
        });
        recognition.onresult = (event) => {
            const spokenText = event.results[0][0].transcript;
            userInput.value = spokenText;
sendMessage();
        };
    } else {
        micBtn.style.display = 'none';
    }

    // --- EVENT LISTENERS ---
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
    newChatBtn.addEventListener('click', startNewChat);

    // --- INITIAL LOAD ---
    startNewChat();
});