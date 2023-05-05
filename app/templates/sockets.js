var socket = io();
socket.on('connect', function () {
    socket.emit('connected', {});
    });
{% for ch in channels %}
socket.on('{{ ch }}', (file) => {
    document.getElementById('{{ ch }}').innerHTML = file;
    });
{% endfor %}
