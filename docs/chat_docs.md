# Create chat
# On Video Update
- Payload
```json
{
    "controller": "/chat",
    "event": "create_message",
    "token": "Bearer {token}",
    "data": {
        "message": {
            "party_id": {party_id}, // int
            "user_id": {user_id}, // int
            "content": {content} // str
        }
    }
}
```
- Response
```json
{
    "event": "chat_sent",
    "data": {
        "user_id": {user_id}, // int
        "party_id": {party_id}, // int
        "content": {content} // str
    }
}
```