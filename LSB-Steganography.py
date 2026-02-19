from PIL import Image
import string


# ---- small helpers to use in ecoding and decoding ----

def _to_bits(num, bit_count):
    # turn a number into a list of bits (most significant bit first)
    return [(num >> i) & 1 for i in range(bit_count)][::-1]


def _from_bits(bits):
    # rebuild an integer from a list of bits
    value = 0
    for b in bits:
        value = (value << 1) | b
    return value


def _border_coords(width, height):
    # get all the border pixels
    coords = []

    # all borders, first is top row to right, then to bottom, then to left and back up
    for x in range(width):
        coords.append((x, 0))

    for y in range(1, height - 1):
        coords.append((width - 1, y))

    if height > 1:
        for x in range(width - 1, -1, -1):
            coords.append((x, height - 1))

    if width > 1:
        for y in range(height - 2, 0, -1):
            coords.append((0, y))

    return coords


def _bytes_to_bits(data: bytes):
    bits = []
    for byte in data:
        bits.extend(_to_bits(byte, 8))
    return bits


def _bits_to_bytes(bits):
    # convert groups of 8 bits back into bytes
    assert len(bits) % 8 == 0
    out = bytearray()

    for i in range(0, len(bits), 8):
        out.append(_from_bits(bits[i:i+8]))

    return bytes(out)


# ---- basic shift encryption based on image size ----

def encrypt(message, width_shift, height_shift):
    encrypted_message = ""

    for char in message:
        if char.isupper():
            encrypted_message += chr((ord(char) + width_shift + height_shift - 65) % 26 + 65)
        elif char.islower():
            encrypted_message += chr((ord(char) + width_shift + height_shift - 97) % 26 + 97)
        else:
            encrypted_message += char

    return encrypted_message


def decrypt(encrypted_message, width_shift, height_shift):
    decrypted_message = ""

    for char in encrypted_message:
        if char.isupper():
            decrypted_message += chr((ord(char) - width_shift - height_shift - 65) % 26 + 65)
        elif char.islower():
            decrypted_message += chr((ord(char) - width_shift - height_shift - 97) % 26 + 97)
        else:
            decrypted_message += char

    return decrypted_message


# these were from prev grey colour version, keeping them here just in case 
def char_to_hex(char):
    ascii_value = ord(char)
    hex_color = f"#{ascii_value:02x}{ascii_value:02x}{ascii_value:02x}"
    return hex_color


def hex_to_char(hex_color):
    r = int(hex_color[1:3], 16)
    return chr(r)


# ---- encoding ----

def encode_message_in_image(path, message):

    image = Image.open(path).convert("RGB")
    width, height = image.size
    pixels = image.load()

    # encrypt first
    encrypted_message = encrypt(message, width, height)

    message_bytes = encrypted_message.encode("utf-8")
    message_length = len(message_bytes)

    # length stored at 16 bits on the first 16 rgb channels
    if message_length > 65535:
        raise ValueError("Message too long. Max length is 65535 bytes.")

    length_bits = _to_bits(message_length, 16)
    message_bits = _bytes_to_bits(message_bytes)
    all_bits = length_bits + message_bits

    coords = _border_coords(width, height)
    capacity_bits = len(coords) * 3

    if len(all_bits) > capacity_bits:
        raise ValueError(
            f"Message too long for this image border. "
            f"Need {len(all_bits)} bits, have {capacity_bits} bits."
        )

    bit_index = 0

    for x, y in coords:

        if bit_index >= len(all_bits):
            break

        r, g, b = pixels[x, y]

        # change only the LSB for each colour value (be it r, g or b)
        if bit_index < len(all_bits):
            r = (r & ~1) | all_bits[bit_index]
            bit_index += 1

        if bit_index < len(all_bits):
            g = (g & ~1) | all_bits[bit_index]
            bit_index += 1

        if bit_index < len(all_bits):
            b = (b & ~1) | all_bits[bit_index]
            bit_index += 1

        pixels[x, y] = (r, g, b)

    encoded_image_path = "encoded_image.png"
    image.save(encoded_image_path)

    print(f"Message encoded in image border and saved as {encoded_image_path}")


# ---- decoding ----

def decode_message_from_image(path):

    image = Image.open(path).convert("RGB")
    width, height = image.size
    pixels = image.load()

    coords = _border_coords(width, height)

    bits = []

    for x, y in coords:
        r, g, b = pixels[x, y]
        bits.append(r & 1)
        bits.append(g & 1)
        bits.append(b & 1)

    if len(bits) < 16:
        print("Not enough data to read message length.")
        return None

    length_bits = bits[:16]
    message_length = _from_bits(length_bits)

    total_bits_needed = 16 + message_length * 8

    if len(bits) < total_bits_needed:
        print("Not enough data in border to decode full message.")
        return None

    message_bits = bits[16:total_bits_needed]
    message_bytes = _bits_to_bytes(message_bits)

    encrypted_message = message_bytes.decode("utf-8", errors="replace")

    decrypted_message = decrypt(encrypted_message, width, height)

    return decrypted_message


# ---- basic menu ----

choice = input("Would you like to encode or decode a message? (encode/decode): ").strip().lower()

if choice == "encode":
    path = input("Enter the path to the image: ").strip()
    message = input("Enter the message to encode: ").strip()
    encode_message_in_image(path, message)

elif choice == "decode":
    path = input("Enter the path to the encoded image: ").strip()
    decoded_message = decode_message_from_image(path)
    print("Decoded message:", decoded_message)

else:
    print("Invalid choice. Please enter 'encode' or 'decode'.")