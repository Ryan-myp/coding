"""Example of bad Python code with anti-patterns."""

import os

# Bad: Global mutable state
users = []

def get_user(id):
    # Bad: No type hints, bare except
    try:
        return users[id]
    except:
        return None

def create_user(username, email):
    # Bad: No validation, no error handling
    user = {"username": username, "email": email}
    users.append(user)
    return user

def process_data(data):
    # Bad: Deep nesting, magic numbers
    if data:
        if len(data) > 0:
            if data[0] != "":
                if len(data[0]) > 5:
                    return data[0].upper()
    return ""
