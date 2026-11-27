import { generateECDHKeyPair } from './crypto.js';
import { exportPublicKey } from './crypto.js';

async function createRoom() {
  const response = await fetch('http://localhost:8000/api/rooms', {
    method: 'POST',
  });
  const data = await response.json();
  console.log('got back', data);
  return data;
}

async function setUP() {
  const params = new URLSearchParams(window.location.search);
  const roomFromUrl = params.get('room');
  let room_id;
  if (roomFromUrl != null) {
    room_id = roomFromUrl;
  } else {
    const data = await createRoom();
    room_id = data.room_id;
  }
  console.log('Room ID:', room_id);
  document.title = room_id;
  const KeyPair = await generateECDHKeyPair();
  const socket = new WebSocket(`ws://127.0.0.1:8000/ws/${room_id}`);

  socket.onopen = async () => {
    const exportedKey = await exportPublicKey(KeyPair.publicKey);
    const envelope = { type: 'key', payload: exportedKey };
    socket.send(JSON.stringify(envelope));
  };

  socket.onmessage = (event) => {
    console.log('Received ', event.data);
  };
}

setUP();
