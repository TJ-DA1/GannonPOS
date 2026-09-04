import tkinter as tk
import time
import socket
import json
from app import *
clientid = "SHOP2"

SERVER_IP = "0.0.0.0"
PORT = 0000

def send_to_server(event):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER_IP, PORT))

        client.send(json.dumps(event).encode())

        if event["return"]:
            response = client.recv(1024).decode()
            client.close()
            return json.loads(response)

        return None

    except Exception as e:
        print("Connection error:", e)
        return None

#Client code
#Under a TCP connection can run independently of main code, adding items to event queue over connection

scantime = 0.5
keytime = time.time()
newitemdata = []
itemqueue = []

def onmakesale():
    global itemqueue
    done = []
    if not searchable:
        logwindow.insert(tk.END, f"{time.strftime("%H %M %S").replace(' ', ':')} | INFO | No items have been scanned\n","info")
        logwindow.see(tk.END)
        return

    for i in itemqueue[::-1]:
        if i not in done:
            num = itemqueue.count(i)
            done.append(i)
            response = send_to_server({
                "clientid": clientid,
                "id": "sale",
                "data": (i[0], num),
                "return": True
            })

            if response:
                logwindow.insert(tk.END, f"{time.strftime("%H %M %S").replace(' ', ':')} | SALE | Sold {num} of item {i[0]}\n")
                logwindow.see(tk.END)
            else:
                logwindow.insert(tk.END,f"{time.strftime("%H %M %S").replace(' ', ':')} | ERROR | Item {i[0]} not found in database\n","error")
                logwindow.see(tk.END)
    itemqueue = []

def onitem():
    global values, eventqueue, itemqueue, writable

    if not writable:
        logwindow.insert(tk.END, f"{time.strftime("%H %M %S").replace(' ', ':')} | INFO | Provided data is invalid\n","info")
        logwindow.see(tk.END)
        return

    elif not searchable:
        logwindow.insert(tk.END, f"{time.strftime("%H %M %S").replace(' ', ':')} | INFO | No items have been scanned\n","info")
        logwindow.see(tk.END)
        return

    values.append(itemqueue[-1][0])

    response = send_to_server({
        "clientid": clientid,
        "id": "item",
        "data": values,
        "return": True
    })
    if response[1]:
        logwindow.insert(tk.END,f"{time.strftime("%H %M %S").replace(' ', ':')} | ITEM | Updated item {response[0][-1]}: {tuple(response[0][:-2])}\n")
        logwindow.see(tk.END)
    else:
        logwindow.insert(tk.END,f"{time.strftime("%H %M %S").replace(' ', ':')} | ITEM | Created new item {response[0][-1]}: {tuple(response[0][:-1])}\n")
        logwindow.see(tk.END)
        
    itemqueue = itemqueue[:-1]
    nameentry.delete(0, tk.END)
    priceentry.delete(0, tk.END)
    quantityentry.delete(0, tk.END)
    companyentry.delete(0, tk.END)

def onaddstock():
    global itemqueue
    done = []
    if not searchable:
        logwindow.insert(tk.END, f"{time.strftime("%H %M %S").replace(' ', ':')} | INFO | No items have been scanned\n","info")
        logwindow.see(tk.END)
        return

    for i in itemqueue[::-1]:
        if i not in done:
            num = itemqueue.count(i)
            done.append(i)
            response = send_to_server({
                "clientid": clientid,
                "id": "stock",
                "data": (i[0], num),
                "return": True
            })

            if response:
                logwindow.insert(tk.END, f"{time.strftime("%H %M %S").replace(' ', ':')} | STOCK | Added {num} of item {i[0]}\n")
                logwindow.see(tk.END)
            else:
                logwindow.insert(tk.END,f"{time.strftime("%H %M %S").replace(' ', ':')} | ERROR | Item {i[0]} not found in database\n","error")
                logwindow.see(tk.END)
    itemqueue = []

def onsearchitem():
    global itemqueue

    if not searchable:
        logwindow.insert(tk.END, f"{time.strftime("%H %M %S").replace(' ', ':')} | INFO | No items have been scanned\n","info")
        logwindow.see(tk.END)
        return

    response = send_to_server({
        "clientid": clientid,
        "id": "search",
        "data": itemqueue[-1][0],
        "return": True
    })

    if response[1]:  # response[1] is the product tuple
        nameentry.delete(0, tk.END)
        priceentry.delete(0, tk.END)
        quantityentry.delete(0, tk.END)
        companyentry.delete(0, tk.END)

        nameentry.insert(0, response[1][0])
        priceentry.insert(0, response[1][1])
        quantityentry.insert(0, response[1][2])
        companyentry.insert(0, response[1][3])
        logwindow.insert(tk.END,f"{time.strftime("%H %M %S").replace(' ', ':')} | SEARCH | Fetched item {itemqueue[-1][0]}: {tuple(response[1][:-1])}\n")
        logwindow.see(tk.END)
    else:
        logwindow.insert(tk.END,f"{time.strftime("%H %M %S").replace(' ', ':')} | ERROR | Item {itemqueue[-1][0]} not found in database\n", "error")
        logwindow.see(tk.END)
    itemqueue = itemqueue[:-1]

def onscan(event):
    global currentitem, itemqueue, barcodeentry
    barcode = barcodeentry.get()
    if barcode.replace(" ", "") == "":
        return
    itemqueue.insert(0, (barcode, *send_to_server({
        "clientid": clientid,
        "id": "check",
        "data": barcode,
        "return": True
    })))
    barcodeentry.delete(0, tk.END)

def startscan(event):
    global keytime
    keytime = time.time()

def clearqueue(event):
    global itemqueue
    itemqueue = []

logtext = f"{time.strftime("%H %M %S").replace(' ', ':')} | Welcome to GannonPOS terminal | Session identifier = {clientid}\n"
root.title(f"GannonPOS Client")
barcodeentry.bind("<Return>", onscan)
root.bind("<Escape>", clearqueue)
root.bind('<Key>', startscan)

makesalebutton.configure(command = onmakesale)
additembutton.configure(command = onitem)
addstockbutton.configure(command = onaddstock)
searchitembutton.configure(command = onsearchitem)

logwindow.insert(tk.END, logtext)

def update_loop():
    global searchable, writable, values
    scanned.delete(0.0, tk.END)
    if ("", False) in itemqueue:
        itemqueue.remove(("", False))

    scanned.delete(0.0, tk.END)
    if ("", False) in itemqueue:
        itemqueue.remove(("", False))
    price = 0.0

    if itemqueue:
        scanned.insert(0.0, "SCANNED: ")
        done = []
        for i in itemqueue:
            if i[1]:
                price += i[2][0]

            if i not in done:
                num = itemqueue.count(i)
                done.append(i)
                scanned.insert(tk.END, f"{str(i[0])} ({num}), ", "found" if i[1] else "notfound")

        scanned.delete("end-3c", "end-2c")
        scanned.insert(tk.END, "|| PRESS ESC TO CLEAR")
    else:
        scanned.insert(0.0, f"SCANNED: NONE || PRESS ESC TO CLEAR")

    pricetotal.config(text=f"Total: {price}")
    values = [namein.get(), pricein.get(), quantityin.get(), companyin.get()]

    try:
        values[1], values[2] = float(values[1]), int(values[2])
        writable = bool(values[0] and values[3])
    except:
        writable = False

    searchable = bool(itemqueue)

    if time.time() - keytime > scantime:
        barcodeentry.delete(0, tk.END)

    root.after(50, update_loop)

update_loop()
root.mainloop()