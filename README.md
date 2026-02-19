# LSB-Border-Steganography
A small Python project that hides encrypted text inside the border pixels of an image using Least Significant Bit (LSB) steganography.

The message is first encrypted using a shift based on the image dimensions, then embedded into the LSBs of the RGB values along the image border.   

The encrypted message is converted into bytes.

The length of the message (16 bits) is stored first.

The message bits are written into the least significant bits of the border pixels:

1 bit in Red

1 bit in Green

1 bit in Blue

During decoding:

The first 16 bits are read to determine the message length.

The next bits are extracted.

The message is decrypted back to the original text.

Only border pixels are modified, and each color channel changes by at most ±1, so the visual difference is almost impossible to notice.

REQUIREMENTS:
Python 13.x
Pillow Library