request = {
    "login_1234": bytes.fromhex("ab aa 07 c5 31 32 33 34 c6 55"),
    "query_timer": bytes.fromhex("ab aa 03 e6 e5 55"),
}

response = {
    "login_success": bytes.fromhex("ab bb 04 c5 35 f4 55"),
    "timer": bytes.fromhex("ab bb 07 e6 00 00 00 00 e1 55"),
}
