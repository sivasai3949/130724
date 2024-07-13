document.getElementById('send-btn').addEventListener('click', function(event) {
    event.preventDefault();
    sendUserInput();
});

document.getElementById('user-input').addEventListener('keypress', function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        sendUserInput();
    }
});

document.getElementById('arrow-btn').addEventListener('click', function(event) {
    event.preventDefault();
    sendUserInput();
});

function sendUserInput() {
    var userInput = document.getElementById('user-input').value;
    if (!userInput.trim()) return;

    appendChat("user", userInput);
    showTypingIndicator(); // Show typing indicator (three dots GIF)

    fetch('/process_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'user_input=' + encodeURIComponent(userInput)
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator(); // Hide typing indicator after response is received

        if (data.error) {
            appendChat("robot", "Error: " + data.error);
        } else {
            if (data.response) {
                appendChat("robot", data.response);
            }
            if (data.question) {
                appendChat("robot", data.question);
            }
            if (data.options) {
                displayOptions(data.options);
            }
        }
    })
    .catch(error => {
        hideTypingIndicator(); // Hide typing indicator on error
        console.error('Error:', error);
    });
}

function appendChat(role, message) {
    var chatContainer = document.getElementById('chat-container');
    var chatBubble = document.createElement('div');
    chatBubble.classList.add('chat-bubble', role);
    chatBubble.textContent = message;
    chatContainer.appendChild(chatBubble);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTypingIndicator() {
    var typingIndicator = document.querySelector('.typing-indicator');
    typingIndicator.style.display = 'flex';
}

function hideTypingIndicator() {
    var typingIndicator = document.querySelector('.typing-indicator');
    typingIndicator.style.display = 'none';
}

function displayOptions(options) {
    var chatContainer = document.getElementById('chat-container');
    var optionsContainer = document.createElement('div');
    optionsContainer.classList.add('chat-bubble', 'robot');
    var optionsHtml = '<ul class="options-list">';
    options.forEach(option => {
        optionsHtml += `<li><button class="option-button" onclick="sendOption('${option}')">${option}</button></li>`;
    });
    optionsHtml += '</ul>';
    optionsContainer.innerHTML = optionsHtml;
    chatContainer.appendChild(optionsContainer);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendOption(option) {
    appendChat("user", option);
    showTypingIndicator(); // Show typing indicator when option is selected

    fetch('/process_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'user_input=' + encodeURIComponent(option)
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator(); // Hide typing indicator after response is received

        if (data.response) {
            appendChat("robot", data.response);
        }
        if (data.options) {
            displayOptions(data.options);
        }
        if (data.error) {
            appendChat("robot", "Error: " + data.error);
        }
    })
    .catch(error => {
        hideTypingIndicator(); // Hide typing indicator on error
        console.error('Error:', error);
    });
}

// Floating window message
window.onload = function() {
    var floatingWindow = document.createElement('div');
    floatingWindow.classList.add('floating-window');
    floatingWindow.innerText = "For Generating your personalised education pathways, please describe in few lines about your background, educational experiences, aspirations and higher education goals, as well as any financial constraints";
    document.body.appendChild(floatingWindow);

    setTimeout(function() {
        floatingWindow.style.right = '20px';
    }, 500);

    setTimeout(function() {
        floatingWindow.style.right = '-300px';
    }, 3500);
}
