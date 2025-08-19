# zpl_generator.py
# This file contains the core logic for generating ZPL (Zebra Programming Language) strings.

def generate_zpl_string(product_name, part_number, serial_numbers,
                        qr_x_offset, qr_y_offset, sn_x_offset, sn_y_offset,
                        include_product=True, include_pn=True):
    """
    Generates a ZPL II string for a label with multiple DataMatrix codes.

    Args:
        product_name (str): The product name to display.
        part_number (str): The part number to display.
        serial_numbers (list): A list of serial numbers to be printed.
        qr_x_offset (int): X offset for the QR code.
        qr_y_offset (int): Y offset for the QR code.
        sn_x_offset (int): X offset for the serial number text.
        sn_y_offset (int): Y offset for the serial number text.
        include_product (bool): Whether to include the product name.
        include_pn (bool): Whether to include the part number.

    Returns:
        str: A complete ZPL II string.
    """
    if not serial_numbers or len(serial_numbers) > 12:
        raise ValueError("Serial numbers must contain 1-12 items.")

    zpl_commands = ["^XA"]
    label_width = 800
    label_center = label_width // 2
    zpl_commands.append("^PW800")
    zpl_commands.append("^LL1200")  # label length
    header_y_pos = 30

    # Product Name
    if include_product:
        zpl_commands.append(f"^FO20,{header_y_pos}^A0N,30,30^FD{product_name}^FS")

    # Part Number + Barcode 128
    pn_text_y = header_y_pos + 28
    if include_pn:
        pn_barcode_y = pn_text_y + 30
        barcode_width = 200  # approximate barcode width in dots
        pn_barcode_x = label_center - (barcode_width // 2)

        # PN text on left
        pn_text_x = pn_barcode_x - 80
        zpl_commands.append(f"^FO{pn_text_x},{pn_barcode_y+5}^A0N,50,50^FDPN^FS")

        # Barcode
        zpl_commands.append(f"^FO{pn_barcode_x},{pn_barcode_y}^BY2^BCN,40,N,N,N^FD{part_number}^FS")

        # Part Number text centered below barcode
        text_x = pn_barcode_x + (barcode_width // 2) - (len(part_number)*3)
        text_y = pn_barcode_y + 45
        zpl_commands.append(f"^FO{text_x},{text_y}^A0N,30,30^FD{part_number}^FS")

        # Qty text to right (larger)
        qty_x = label_width - 190  # move a bit to the left
        qty_y = pn_barcode_y + 5
        zpl_commands.append(f"^FO{qty_x},{qty_y}^A0N,50,50^FDQty: {len(serial_numbers)}^FS")
    else:
        pn_barcode_y = pn_text_y

    # DataMatrix serial numbers grid
    grid_start_y = pn_barcode_y + 100
    x_start = 20
    y_start = grid_start_y
    spacing_x = 180
    spacing_y = 120  # reduced spacing

    for i, sn in enumerate(serial_numbers):
        row = i // 4
        col = i % 4
        current_x = x_start + col * spacing_x
        current_y = y_start + row * spacing_y
        # DataMatrix
        zpl_commands.append(f"^FO{current_x + qr_x_offset},{current_y + qr_y_offset}^BXN,3,80^FD{sn}^FS")
        # Serial number text
        zpl_commands.append(f"^FO{current_x + sn_x_offset},{current_y + sn_y_offset}^A0N,20,20^FD{sn}^FS")

    # Big QR code bottom-left with all serials in column
    qr_text = "\n".join(serial_numbers)  # column-style
    zpl_commands.append(f"^FO20,550^BQN,1,4^FDMA {qr_text}^FS")

    zpl_commands.append("^XZ")
    return "\n".join(zpl_commands)
