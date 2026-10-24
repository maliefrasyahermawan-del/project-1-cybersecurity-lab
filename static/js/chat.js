let currentChatMode = 'public'; // 'public' or contact_id
let chatPollingInterval = null;
let requestsPollingInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    openPublicRoom();
    startPollingRequests();
});

function fetchJSON(url, options = {}) {
    return fetch(url, {
        headers: {
            'Content-Type': 'application/json'
        },
        ...options
    }).then(res => res.json());
}

function openPublicRoom() {
    currentChatMode = 'public';
    document.getElementById('chat-header-title').innerText = 'Public Discussion Room';
    highlightSidebar('btn-public-room');
    startPollingChat();
}

function openPrivateRoom(contactId, contactName) {
    currentChatMode = contactId;
    document.getElementById('chat-header-title').innerText = `Private Chat with ${contactName}`;
    highlightSidebar(`contact-${contactId}`);
    startPollingChat();
}

function highlightSidebar(idToHighlight) {
    // Reset highlights
    document.getElementById('btn-public-room').style.borderColor = 'var(--border-color)';
    const contacts = document.querySelectorAll('.contact-item');
    contacts.forEach(c => c.style.borderColor = 'transparent');

    const el = document.getElementById(idToHighlight);
    if(el) {
        el.style.borderColor = 'var(--primary-red)';
    }
}

function startPollingChat() {
    if (chatPollingInterval) clearInterval(chatPollingInterval);
    fetchMessages();
    chatPollingInterval = setInterval(fetchMessages, 3000);
}

function startPollingRequests() {
    if (requestsPollingInterval) clearInterval(requestsPollingInterval);
    fetchRequestsAndContacts();
    requestsPollingInterval = setInterval(fetchRequestsAndContacts, 5000);
}

function fetchMessages() {
    let url = currentChatMode === 'public' ? '/api/chat/public' : `/api/chat/private/${currentChatMode}`;
    
    fetchJSON(url).then(messages => {
        renderMessages(messages);
    }).catch(e => console.error("Error fetching messages", e));
}

function renderMessages(messages) {
    const container = document.getElementById('chat-messages');
    
    // Check if scrolled to bottom before updating
    const isScrolledToBottom = container.scrollHeight - container.clientHeight <= container.scrollTop + 50;

    container.innerHTML = '';
    
    messages.forEach(msg => {
        const isMine = msg.sender_id === currentUserId;
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${isMine ? 'mine' : ''}`;
        
        const senderDiv = document.createElement('div');
        senderDiv.className = 'sender';
        senderDiv.innerText = isMine ? 'You' : msg.username;
        
        const contentDiv = document.createElement('div');
        contentDiv.innerText = msg.content;
        
        msgDiv.appendChild(senderDiv);
        msgDiv.appendChild(contentDiv);
        container.appendChild(msgDiv);
    });

    if (isScrolledToBottom) {
        container.scrollTop = container.scrollHeight;
    }
}

function sendMessage() {
    const input = document.getElementById('chat-input-field');
    const content = input.value.trim();
    if (!content) return;

    let url = currentChatMode === 'public' ? '/api/chat/public' : `/api/chat/private/${currentChatMode}`;
    
    fetchJSON(url, {
        method: 'POST',
        body: JSON.stringify({ content })
    }).then(res => {
        if(res.status === 'success') {
            input.value = '';
            fetchMessages(); // immediate update
        }
    });
}

function handleKeyPress(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
}

// Request System
function sendChatRequest() {
    const uniqueId = document.getElementById('target-unique-id').value.trim();
    if (!uniqueId) return;

    fetchJSON('/api/chat/request', {
        method: 'POST',
        body: JSON.stringify({ unique_id: uniqueId })
    }).then(res => {
        alert(res.message);
        if(res.status === 'success') {
            document.getElementById('target-unique-id').value = '';
        }
    });
}

function fetchRequestsAndContacts() {
    // Fetch Requests
    fetchJSON('/api/chat/requests/incoming').then(requests => {
        const container = document.getElementById('incoming-requests-list');
        if (requests.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.8rem; text-align: center;">No pending requests</p>';
        } else {
            container.innerHTML = '';
            requests.forEach(req => {
                const reqDiv = document.createElement('div');
                reqDiv.style.cssText = "background: #2a2a2a; padding: 10px; border-radius: 4px; margin-bottom: 10px;";
                reqDiv.innerHTML = `
                    <div style="font-size: 0.9rem; margin-bottom: 5px;">${req.username} (${req.unique_id})</div>
                    <div style="display: flex; gap: 5px;">
                        <button class="btn" style="flex: 1; padding: 5px; font-size: 0.8rem; background: #4caf50;" onclick="handleRequest(${req.id}, 'accept')">Accept</button>
                        <button class="btn" style="flex: 1; padding: 5px; font-size: 0.8rem; background: #f44336;" onclick="handleRequest(${req.id}, 'decline')">Decline</button>
                    </div>
                `;
                container.appendChild(reqDiv);
            });
        }
    });

    // Fetch Contacts
    fetchJSON('/api/chat/private/contacts').then(contacts => {
        const container = document.getElementById('private-contacts-list');
        if (contacts.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.8rem; text-align: center;">No private contacts</p>';
        } else {
            container.innerHTML = '';
            contacts.forEach(contact => {
                const contactDiv = document.createElement('div');
                contactDiv.className = 'contact-item';
                contactDiv.id = `contact-${contact.id}`;
                contactDiv.style.cssText = `
                    padding: 10px; 
                    border-radius: 4px; 
                    margin-bottom: 5px; 
                    cursor: pointer; 
                    background: var(--background-darker);
                    border: 1px solid ${currentChatMode == contact.id ? 'var(--primary-red)' : 'transparent'};
                `;
                contactDiv.innerText = contact.username;
                contactDiv.onclick = () => openPrivateRoom(contact.id, contact.username);
                container.appendChild(contactDiv);
            });
        }
    });
}

function handleRequest(reqId, action) {
    fetchJSON('/api/chat/request/handle', {
        method: 'POST',
        body: JSON.stringify({ request_id: reqId, action: action })
    }).then(res => {
        if(res.status === 'success') {
            fetchRequestsAndContacts(); // refresh lists immediately
        }
    });
}
