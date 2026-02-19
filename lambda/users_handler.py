def lambda_handler(event, context):
    users = [
        {"id": 1, "name": "Alice Kowalski", "email": "alice@example.com", "role": "admin"},
        {"id": 2, "name": "Bob Nowak",     "email": "bob@example.com",   "role": "editor"},
        {"id": 3, "name": "Carol Wiśniewska", "email": "carol@example.com", "role": "viewer"},
        {"id": 4, "name": "David Zając",   "email": "david@example.com", "role": "editor"},
        {"id": 5, "name": "Eva Wójcik",    "email": "eva@example.com",   "role": "viewer"},
    ]

    return {
        "statusCode": 200,
        "count": len(users),
        "users": users,
    }
