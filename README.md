Zebra Serial Number Printer
<img width="2320" height="1997" alt="Picture2" src="https://github.com/user-attachments/assets/66fb3fbd-e95c-47fc-a6cb-7c9909634502" />

**Features**
- USB Printing Support (via pywin32)
- Product Information: Add Product Name and Part Number (optional)
  Barcode & DataMatrix Support:
- Part Number printed as Code128 barcode
- Up to 12 serial numbers per batch, each with DataMatrix + text
- Big QR Code at bottom-left containing all serials (column format)
- Position Offsets: Fine-tune label element positions (X/Y offsets for QR and text)
- CSV Logging: Automatically logs printed serials with batch number, date, and time
- Reprint Last Batch option
- Auto-Print Mode when 12 serial numbers are scanned
<img width="436" height="720" alt="2" src="https://github.com/user-attachments/assets/a844983a-3bb7-47d2-b13f-3072637f96f7" />

**Label Layout**
- Top: Product Name (optional)
- Center: Part Number + Code128 Barcode + Quantity
- Middle: 1–12 serial numbers with DataMatrix + text arranged in a grid
- Bottom Left: One large QR code containing all serial numbers in a list

**Installation**
Requirements:
1. Python 3.8+
2. Zebra printer (ZPL-compatible, e.g., ZD421)
3. Windows with USB driver installed

