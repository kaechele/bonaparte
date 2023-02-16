request = {
    "login_1234": bytes.fromhex("ab aa 07 c5 31 32 33 34 c6 55"),
    "query_timer": bytes.fromhex("ab aa 03 e6 e5 55"),
}

response = {
    "ble_version": bytes.fromhex("ab bb 06 f2 00 08 00 fc 55"),
    "login_success": bytes.fromhex("ab bb 04 c5 35 f4 55"),
    "mcu_version": bytes.fromhex("ab bb 06 f3 01 01 04 f1 55"),
    "timer_off": bytes.fromhex("ab bb 07 e6 00 00 00 00 e1 55"),
    "timer_201455_on": bytes.fromhex("ab bb 07 e6 14 0e 01 37 cd 55"),
    "on_state_all_off": bytes.fromhex("ab bb 05 e4 00 00 e1 55"),
    "off_state_all_off": bytes.fromhex("ab bb 05 e3 00 01 e7 55"),
    "led_color_0000ff": bytes.fromhex("ab bb 06 e1 00 02 ff 1a 55"),
    "led_controller_state": bytes.fromhex("ab bb 08 ee ff 00 00 ff 02 e4 55"),
}
