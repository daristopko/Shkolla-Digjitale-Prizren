function updateClock() {
  const time = new Date().toLocaleTimeString('en-GB');

  const clock = document.getElementById('clock');
  const clockDisplay = document.getElementById('clock-display');

  if (clock) clock.textContent = time;
  if (clockDisplay) clockDisplay.textContent = time;
}

updateClock();
setInterval(updateClock, 1000);



let highestZ = 10;

function setupWindow(win) {
    let isDragging = false;
    let offsetX = 0;
    let offsetY = 0;

    const titlebar = win.querySelector('.window-titlebar');
    const closeButton = win.querySelector('.window-close');

    titlebar.addEventListener('mousedown', (event) => {
        isDragging = true;
        event.preventDefault();
        offsetX = event.clientX - win.offsetLeft;
        offsetY = event.clientY - win.offsetTop;
        highestZ++;
        win.style.zIndex = highestZ;
    });
    document.addEventListener('mousemove', (event) => {
        if (!isDragging) return;
        win.style.position = 'absolute';
        win.style.left = `${event.clientX - offsetX}px`;
        win.style.top = `${event.clientY - offsetY}px`;
    });
    document.addEventListener('mouseup', () => {
        isDragging = false;
    });

    closeButton.addEventListener('click', () => {
        win.style.display = 'none';
    });
}

const taskbarIcons = document.querySelectorAll('.taskbar-icon');

taskbarIcons.forEach(icon => {
  icon.addEventListener('click', event => {
    const targetId = event.currentTarget.dataset.target;
    const windowElement = document.getElementById(targetId);

    if (windowElement) {
      windowElement.style.display = 'block';
    } else {
      console.warn(`No window found with ID: ${targetId}`);
    }
  });
});


let currentInput = '0';
let previousInput = '';
let operator = null;
let shouldResetDisplay = false;

const display = document.getElementById('calc-display');

function updateDisplay() {
    display.textContent = currentInput;
}

function handleNumber(num) {
    if (shouldResetDisplay) {
        currentInput = num;
        shouldResetDisplay = false;
    } else if (currentInput === '0') {
        currentInput = num;
    } else {
        currentInput += num;
    }
    updateDisplay();
}

function handleOperator(op) {
    if (operator !== null) handleEquals(); 
    previousInput = currentInput;
    operator = op;
    shouldResetDisplay = true;
}

function handleEquals() {
    if (!operator || !previousInput) return;

    const prev = parseFloat(previousInput);
    const current = parseFloat(currentInput);
    let result;

    if (operator === '+') result = prev + current;
    else if (operator === '−') result = prev - current;
    else if (operator === '×') result = prev * current;
    else if (operator === '÷') result = current === 0 ? 'Error' : prev / current;

    currentInput = result.toString();
    updateDisplay();

    operator = null;
    previousInput = '';
    shouldResetDisplay = true;
}

document.getElementById('calc-buttons').addEventListener('click', e => {
    const btn = e.target.textContent;

    if (!btn) return;

    if (!isNaN(btn) || btn === '.') handleNumber(btn);
    else if (btn === '+' || btn === '−' || btn === '×' || btn === '÷') handleOperator(btn);
    else if (btn === '=') handleEquals();
    else if (btn === 'C') { 
        currentInput = '0';
        previousInput = '';
        operator = null;
        shouldResetDisplay = false;
        updateDisplay();
    }
});


const startBtn = document.getElementById('start-btn');
const startMenu = document.getElementById('start-menu');

startBtn.addEventListener('click', () => {
    if (startMenu.style.display === 'none' || startMenu.style.display === '') {
        startMenu.style.display = 'block';
    } else {
        startMenu.style.display = 'none';
    }
});


const startMenuItems = document.querySelectorAll('.start-menu-item');
startMenuItems.forEach(item => {
    item.addEventListener('click', () => {
        const chatbotWindow = document.getElementById('window-chatbot');
        chatbotWindow.style.display = 'block';
        startMenu.style.display = 'none';
    });
});


setupWindow(document.getElementById('window-calculator'));
setupWindow(document.getElementById('window-notepad'));
setupWindow(document.getElementById('window-clock'));
setupWindow(document.getElementById('window-chatbot'));


function getBotResponse(text) {
    text = text.toLowerCase();

    if (text.includes('hello') || text.includes('hi')) {
        return 'Hello!';
    } else if (text.includes('what is your name')) {
        return 'DarisOS Bot';
    } else if (text.includes('what is the time')) {
        return 'Check the clock app.';
    } else if (text.includes('capital city of france')) {
        return 'Paris';
    } else if (text.includes('largest planet in solar system')) {
        return 'Jupiter';
    } else if (text.includes('speed of light in m/s')) {
        return '299,792,458 m/s';
    } else if (text.includes('who made you')) {
        return 'Daris Topko';
    } else if (text.includes('what is the meaning of life')) {
        return '42';
    } else if (text.includes('water boiling point')) {
        return '100°C';
    } else if (text.includes('what is the smallest planet in our solar system')) {
        return 'Mercury';
    } else if (text.includes('how many continents are there on earth')) {
        return '7';
    } else if (text.includes('what is html')) {
        return 'Markup language for web pages';
    } else if (text.includes('what is css')) {
        return 'Styling language for web pages';
    } else if (text.includes('what is javascript')) {
        return 'Programming language for web interactivity';
    } else if (text.includes('who is albert einstein')) {
        return 'Famous physicist, theory of relativity';
    } else if (text.includes('what is the sun')) {
        return 'Star at the center of our solar system';
    } else if (text.includes('how many planets are in our solar system')) {
        return '8 planets in our solar system';
    } else if (text.includes('what is gravity')) {
        return 'Force that attracts objects toward each other';
    } else if (text.includes('who invented the world wide web')) {
        return 'Tim Berners-Lee invented the World Wide Web';
    } else if (text.includes('capital city of kosovo')) {
        return 'Pristina';
    } else {
        return "I don't know that one, try asking something else!";
    }
}


const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');
const chatSend = document.getElementById('chat-send');

function sendMessage() {
    const userText = chatInput.value.trim();
    if (!userText) return;

    
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-msg-user';
    userMsg.textContent = userText;
    chatMessages.appendChild(userMsg);

    
    const botMsg = document.createElement('div');
    botMsg.className = 'chat-msg-bot';
    botMsg.textContent = getBotResponse(userText);
    chatMessages.appendChild(botMsg);

    chatInput.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


chatSend.addEventListener('click', sendMessage);
chatInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') sendMessage();
});