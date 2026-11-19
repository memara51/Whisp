
import asyncio
import json
from urllib.request import urlopen, Request

import websockets
from websockets.exceptions import ConnectionClosed

BASE_HTTP = "http://127.0.0.1:8000"
BASE_WS = "ws://127.0.0.1:8000"


def create_room():
    request = Request(
        f"{BASE_HTTP}/api/rooms",
        data=b"",
        method="POST"
    )

    with urlopen(request, timeout=5) as response:
        result = json.loads(response.read())

    return result["room_id"]


async def expect_rejected(room_id, description):
    try:
        connection = await websockets.connect(
            f"{BASE_WS}/ws/{room_id}",
            open_timeout=5
        )

    except Exception as error:
        status = getattr(
            getattr(error, "response", None),
            "status_code",
            None
        )

        if status == 403 or "403" in str(error):
            print(f"PASS: {description}")
        else:
            raise RuntimeError(
                f"Unexpected connection error during {description}: {error}"
            ) from error

    else:
        await connection.close()
        raise AssertionError(
            f"FAIL: {description} — connection was accepted!"
        )


async def main():

    print("\n========== SECURELINK BACKEND TESTS ==========\n")

    # TEST 1: Check whether the server is running
    with urlopen(f"{BASE_HTTP}/status", timeout=5) as response:
        assert response.status == 200

    print("PASS: FastAPI server is running")

    # TEST 2: Create a room
    room_id = create_room()

    assert room_id
    print("PASS: Room created:", room_id)

    # TEST 3: Connect Alice
    room_url = f"{BASE_WS}/ws/{room_id}"

    alice = await websockets.connect(room_url)
    print("PASS: Alice connected")

    # TEST 4: Connect Bob
    bob = await websockets.connect(room_url)
    print("PASS: Bob connected")

    await expect_rejected(
    room_id,
    "Third participant (Joe) rejected"
    )

    # TEST 5: Send a message and test echo
    message = "Hello from Alice!"

    await alice.send(message)

    response = await asyncio.wait_for(
        alice.recv(),
        timeout=5
    )

    expected = f"Server received: {message}"

    assert response == expected, (
        f"Expected {expected!r}, received {response!r}"
    )

    print("PASS: Alice sent a message and received the echo")

    # TEST 6: Alice disconnects
    await alice.close()
    print("PASS: Alice disconnected")

    # TEST 7: Verify Bob is disconnected automatically
    try:
        await asyncio.wait_for(bob.recv(), timeout=5)
        raise AssertionError(
            "FAIL: Bob was not disconnected"
        )

    except ConnectionClosed:
        print("PASS: Bob was disconnected automatically")

    # TEST 8: Verify the old room was destroyed
    await expect_rejected(
        room_id,
        "Old room ID is rejected after destruction"
    )

    # TEST 9: Verify nonexistent rooms are rejected
    await expect_rejected(
        "fake-room-123",
        "Nonexistent room is rejected"
    )

    print("\n========== ALL TESTS PASSED ==========\n")


if __name__ == "__main__":
    asyncio.run(main())
