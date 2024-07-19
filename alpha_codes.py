# Alpha codes dictionary
ALPHA_CODES = {
    '\x00': '[NUL]', '\x01': '[SOH]', '\x02': '[STX]', '\x03': '[ETX]', '\x04': '[EOT]',
    '\x05': '[ENQ]', '\x06': '[ACK]', '\x07': '[BEL]', '\x08': '[BS]', '\x09': '[HT]',
    '\x0A': '[LF]', '\x0B': '[VT]', '\x0C': '[FF]', '\x0D': '[CR]', '\x0E': '[SO]',
    '\x0F': '[SI]', '\x10': '[DLE]', '\x11': '[DC1]', '\x12': '[DC2]', '\x13': '[DC3]',
    '\x14': '[DC4]', '\x15': '[NAK]', '\x16': '[SYN]', '\x17': '[ETB]', '\x18': '[CAN]',
    '\x19': '[EM]', '\x1A': '[SUB]', '\x1B': '[ESC]', '\x1C': '[FS]', '\x1D': '[GS]',
    '\x1E': '[RS]', '\x1F': '[US]',
    '\x1C1': '[RED]', '\x1C2': '[GREEN]', '\x1C3': '[AMBER]', '\x1C4': '[DIM RED]',
    '\x1C5': '[DIM GREEN]', '\x1C6': '[BROWN]', '\x1C7': '[ORANGE]', '\x1C8': '[YELLOW]',
    '\x1C9': '[RAINBOW1]', '\x1CA': '[RAINBOW2]', '\x1CB': '[COLOR MIX]', '\x1CC': '[AUTOCOLOR]',
    '\x1B"': '[TOP]', '\x1B ': '[MIDDLE]', '\x1B&': '[BOTTOM]', '\x1B0': '[FILL]',
    '\x1B\x1A1': '[5x5 FONT]', '\x1B\x1A2': '[5x7 FONT]', '\x1B\x1A3': '[7x6 FONT]',
    '\x1B\x1A4': '[7x11 FONT]', '\x1B\x1A5': '[7 SHADOW FONT]', '\x1B\x1A6': '[8x16 FONT]',
    '\x1B\x1A7': '[10x12 FONT]', '\x1B\x1A8': '[FULL FONT]',
    '\x1Ba': '[ROTATE]', '\x1Bb': '[HOLD]', '\x1Bc': '[FLASH]', '\x1Bd': '[RESERVED]',
    '\x1Be': '[ROLL UP]', '\x1Bf': '[ROLL DOWN]', '\x1Bg': '[ROLL LEFT]', '\x1Bh': '[ROLL RIGHT]',
    '\x1Bi': '[WIPE UP]', '\x1Bj': '[WIPE DOWN]', '\x1Bk': '[WIPE LEFT]', '\x1Bl': '[WIPE RIGHT]',
    '\x1Bm': '[SCROLL]', '\x1Bn': '[AUTOMODE]', '\x1Bo': '[ROLL IN]', '\x1Bp': '[ROLL OUT]',
    '\x1Bq': '[WIPE IN]', '\x1Br': '[WIPE OUT]', '\x1Bs': '[COMPRESSED ROTATE]',
    '\x1Bt': '[EXPLODE]', '\x1Bu': '[CLOCK]',
    '\x1Bn0': '[TWINKLE]', '\x1Bn1': '[SPARKLE]', '\x1Bn2': '[SNOW]', '\x1Bn3': '[INTERLOCK]',
    '\x1Bn4': '[SWITCH]', '\x1Bn5': '[SLIDE]', '\x1Bn6': '[SPRAY]', '\x1Bn7': '[STARBURST]',
    '\x1Bn8': '[WELCOME]', '\x1Bn9': '[SLOT MACHINE]', '\x1BnA': '[NEWS FLASH]',
    '\x1BnB': '[TRUMPET ANIMATION]', '\x1BnC': '[CYCLE COLORS]',
    '\x13': '[CALL TIME]', '\x0B8': '[CALL DATE]',
    '\x1D0': '[WIDE OFF]', '\x1D1': '[WIDE ON]', '\x1D2': '[DOUBLE WIDE ON]',
    '\x1D3': '[DOUBLE WIDE OFF]',
    '\x1E0': '[PROPORTIONAL]', '\x1E1': '[FIXED WIDTH]',
    '\x1B \x1Bb': '[MIDDLE-HOLD]',
    '\x1B&\x1Bb': '[BOTTOM-HOLD]',
    '\x1B \x1Bc': '[MIDDLE-FLASH]',
    '\x1B&\x1Bc': '[BOTTOM-FLASH]',
}

def translate_alpha_codes(message):
    translated = ""
    i = 0
    while i < len(message):
        if message[i:i+3] in ALPHA_CODES:
            translated += ALPHA_CODES[message[i:i+3]]
            i += 3
        elif message[i:i+2] in ALPHA_CODES:
            translated += ALPHA_CODES[message[i:i+2]]
            i += 2
        elif message[i] in ALPHA_CODES:
            translated += ALPHA_CODES[message[i]]
            i += 1
        else:
            translated += message[i]
            i += 1
    return translated
