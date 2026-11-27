export async function generateECDHKeyPair() {
  const KeyPair = await crypto.subtle.generateKey(
    {
      name: 'ECDH',
      namedCurve: 'P-256',
    },
    false,
    ['deriveBits'],
  );
  return KeyPair;
}

export async function exportPublicKey(publicKey) {
  const raw = await crypto.subtle.exportKey('raw', publicKey);
  return btoa(String.fromCharCode(...new Uint8Array(raw)));
}
