# Join to party
- Payload
```json
{
    "controller": "/party",
    "event": "join_party",
    "token": "Bearer {token}",
    "data": {
        "party": {
            "user_id": {user_id}, // int
            "user_avatar": {user_avatar} // str
            "invite_code": {invite_code} // str
        }
    }
}
```
- Response
```json
{
    "event": "user_joined",
    "data": {
        "user_id": {user_id}, // int
        "user_avatar": {user_avatar} // str
        "party_id": {party_id} // int
    }
}
```

# Set Video URL
- Payload
```json
{
    "controller": "/party",
    "event": "set_party_video_url",
    "token": "Bearer {token}",
    "data": {
        "update":{
            "party_id": {party_id}, // int
            "video_url": {video_url}, // str
            "user_id": {user_id} // int
        }
    }
}
```
- Response
```json
{
    "event": "update_party_video_url",
    "data": {
        "video_url": {video_url} // str
    }
}
```

# On Video Update
- Payload
```json
{
    "controller": "/party",
    "event": "update_video",
    "token": "Bearer {token}",
    "data": {
        "update": {
            "party_id": {party_id}, // int
            "user_id": {user_id}, // str
            "state": {state}, // pause, resume and seek
            "seek_to": {seek_to} // int
        }
    }
}
```
- Response
```json
{
    "event": "seek_to",
    "data": {
        "state": {state}, // str
        "seek_to": {seek_to} // int
    }
}
```