# GannonPOS
# General info
GannonPOSServer - A client server hybrid acting as a host for all auxiliary systems - referred to as "server main"\
GannonPOSClient - A client running on all auxiliary systems - referred to as "client main"\
product.db - Required in the same running directory as server main. Will be created and configured on first run. Contains all products and details.\
lists/ and sales/ - Required in the same running directory of server main. Will be created on first run. Contains archive lists holding details about out of stock items and all sales.

GannonPOS runs on Mac, Windows and (presumably) Linux - releases have only been built for Windows, so other OSs will require manual building or just running source code. Client server connection requires all systems being on the same network. The program uses port 2106 by default. This can be changed in the config file but typically 2106 will be available.

The system uses a simple client and server model to connect multiple points of service.\
The client main should only be used on auxiliary computers and should only be booted when the server main is running.\
Only one server main should be running per network.\
The client main can be duplicated on multiple auxiliary computers all connected to one server.\
The server main can be used without any clients at all as a single point of service system.\
This project should not be used if the sales are confidential in anyway as the data is not encrypted at all during transfer.

# Connecting one client
Run the server main on a computer with a known IP address on a LAN (typically on the same Wi-Fi connection or connected to the same router) with the client. Open command prompt and type "ipconfig" to get IP on Windows systems - any listed address next to "IPv4 Address" should work.\
Edit the client config on the auxiliary system - set host setting to the known IP address.\
Set the name of the auxiliary client using config file clientid - ensure this is different to the server's config file clientid.\
Run the client main - this should automatically connect to the server main and act as a separate point of service.

# Connecting multiple clients
This is the same process as connecting one client - ensure all clients (including the server itself) have a different ID. The amount of clients that can be connected to a server is untested past 2 clients and one server, so mileage may vary.

# Config file
ClientID - Unique identifier of the server and all clients. Ensure all are different. Can be any string.
Port - Port on the computer running server main. Usually 2106 which should work fine. can be any number 0 through 65535, but Google the chosen port first to avoid commonly reserved ports.
Host - IP address of computer running server main. Should be set to 0.0.0.0 on the server config file. Takes any string but will crash if string is not a valid IP address (int.int.int.int). See connecting one client to find IP.
TerminateScan - The signal inputted at the end of a barcode being scanned - usually return for most USB scanners but may differ. Takes keyboard input names surrounded by < and >.
ScanTime - The max amount of time a scan can take before the field is cleared to avoid misinputs. Usually 0.5 but will take any decimal or whole number. Use large number such as 99999 to disable.

# How to use
There are 9 main functions of GannonPOS - Scan, Clear, Check, Search, Edit, New, Sale, Stock and Total\
Scan - Clicking the field under "Click below to scan item" will allow you to scan an item. USB barcode scanners should read a barcode, input the data and input a signal which will emulate the enter key on a keyboard. This will cause the barcode ID to be added to the "SCANNED" queue on the bottom of the app. Scanned barcodes will join this queue and any actions that take one item at a time will take one item from the queue. Actions that take all items will clear the queue upon executing.\
Clear - If an item is not scanned properly, or data is inputted by mistake, the whole item queue can be cleared using the ESC key on a keyboard.\
Check - This process is run automatically. If a scanned item appears red in the item queue, this item does not exist in the products database. It can be added using the New function.\
Search - This process takes one item at a time. The details of the item at the front of the queue will be placed in the "Product name", "Company", "Price", "Quantity in stock", and the item will be removed from the queue. Searching an item that does not exist will produce an error message.\
Edit - This process takes one item at a time. After searching, the 4 previously mentioned fields can be edited. Following this the "Edit / new item" button will attribute these details to the next item in the queue, so to edit the searched item it must be scanned again, and the item will be removed from the queue. The price should be any number (including decimals) and the quantity can only be whole numbers. Anything else will produce an error message.\
New - This process takes one item at a time. Adding a new item to the database uses the same process as editing an item. Input data into the 4 boxes and press "Edit / new item" to attribute to values to the next item in the queue. The price should be any number (including decimals) and the quantity can only be whole numbers. Anything else will produce an info message.\
Sale - This process clears the queue. Pressing "Make sale" will clear the queue and update the stock of all the cleared items. Making a sale on an item that does not exist will produce an error message.\
Stock - This process clears the queue. This is the same process as Sale, but the stock change is additive instead of subtractive. Scan all new items and press "Add stock" to update stock of all items in the queue. Adding stock on an item that does not exist will produce an error message.\
Total - The price value of all items in the queue will be added to the total displayed above the item queue. This avoids manual calculation.\
Items that do not exist in the database will contribute nothing to the total.

GannonPOS also keeps two dated list systems - these are stored in subdirectories "lists" and "sales"\
Lists - These store lists of products that are out of stock. When a sale is made, if the stock value of the item sold is less than or equal to zero, the item will be added to the list along with the product details.\
Sales - These store lists of products sold using the Sell function. All sales made will add the products to these lists, along with the product details.

# Console info
All console info comes with a time on the left. Server consoles typically contain more messages due to client requests.\
All requests made by clients will appear in GREEN. These are mostly for debugging and all can be safely ignored. They include the operation and the client ID that requested it.\
Info messages will appear in BLUE. These all contain explanations of what went wrong during execution - usually data input is invalid or no items are in the queue.\
Error messages will appear in RED. These appear when an action is carried out on an item that does not exist in the product database. An ID will be given for the missing item. Refer to New function to add a new item to the product database.\
All other info will appear in WHITE. This includes an introductory message stating the client ID and a description of all successful operations.
