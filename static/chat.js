document.addEventListener('DOMContentLoaded', function () {
    const chatSocket = new WebSocket(
        'ws://' + window.location.host +
        '/chat/'
    );

    chatSocket.onopen = function (e) {
        console.log('WebSocket connection established.');
    };

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        const message = data['message'];
        const threadId = data['thread_id'];

        // Update the UI to display the received message
        const threadDiv = document.querySelector(`[data-thread-id="${threadId}"]`);
        const messagesList = threadDiv.querySelector('.messages');
        const messageElement = document.createElement('li');
        messageElement.textContent = message;
        messagesList.appendChild(messageElement);
    };

    document.querySelector('#message-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const messageInputDom = document.querySelector('#message-input');
        const message = messageInputDom.value;
        const threadId = /* Obtain the thread ID */; // You may need to adjust this

        // Send the message through WebSocket
        chatSocket.send(JSON.stringify({
            'message': message,
            'thread_id': threadId
        }));

        // Clear the input field
        messageInputDom.value = '';
    });
});
