import secrets

rooms:dict={}

def generate_room_id():
    room_id = secrets.token_urlsafe()

    while room_id in rooms:
        room_id = secrets.token_urlsafe()

    return room_id
