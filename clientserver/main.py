import tkinter as tk
import time
from datetime import date
from app import *
import os
import json
import sqlite3
import socket, threading
with open('config.json', 'r') as f:
   config = json.load(f)

clientid = config["clientid"]

#Database code
#Data base of product is stored as table of name, price, quantity, company, barcodeid
dbexists = os.path.exists("product.db")
product = sqlite3.connect("product.db")
cur = product.cursor()
if not dbexists:
    cur.execute("CREATE TABLE product (name, price float, quantity int, company, barcodeid)")

#Ensure folders available
os.makedirs("sales", exist_ok=True)
os.makedirs("lists", exist_ok=True)

def makesale(data):
    get = cur.execute("SELECT * FROM product WHERE barcodeid=?", (data[0],))
    row = get.fetchone()
    if row:
        cur.execute("UPDATE product SET quantity = quantity - ? WHERE barcodeid = ?", (data[1], data[0],))
        get = cur.execute("SELECT name, company, quantity, price FROM product WHERE barcodeid=? AND quantity < 1", (data[0],))
        product.commit()
        row = get.fetchone()
        if row is not None:
            with open(f"lists/{date.today()}.txt", "a") as o:
                o.write(str(row)[1:-1].replace("\'","") + "\n")

        get = cur.execute("SELECT name, company, price FROM product WHERE barcodeid=?", (data[0],))
        row = get.fetchone()
        with open(f"sales/{date.today()}.txt", "a") as o:
            o.write(str(row)[1:-1].replace("\'", "") + f" ({data[1]})" + "\n")
        return True

    else:
        return False

def item(data):
    global itemqueue
    get = cur.execute("SELECT * FROM product WHERE barcodeid=?", (data[4],))

    if get.fetchone() is None:

        cur.execute(
            "INSERT INTO product VALUES (?, ?, ?, ?, ?)",
                data
        )
        product.commit()
        return data, False
    else:
        data.append(data[-1])
        cur.execute(
            "UPDATE product SET name=?, price=?, quantity=?, company=?, barcodeid=? WHERE barcodeid=?",
            data
        )
        product.commit()
        return data, True

def addstock(data):
    get = cur.execute("SELECT * FROM product WHERE barcodeid=?", (data[0],))
    row = get.fetchone()
    if row:
        cur.execute("UPDATE product SET quantity = quantity + ? WHERE barcodeid = ?", (data[1], data[0],))
        product.commit()
        return True
    else:
        return False

def searchitem(data):
    get = cur.execute("SELECT * FROM product WHERE barcodeid=?", (data,))
    row = get.fetchone()
    return row

def checkitem(data):
    get = cur.execute("SELECT price FROM product WHERE barcodeid=?", (data,))
    row = get.fetchone()
    return bool(row), row

#Client code
#Under a TCP connection can run independently of main code, adding items to event queue over connection

scantime = config["scantime"]
keytime = time.time()
newitemdata = []
itemqueue = []

def onmakesale():
    global itemqueue, eventqueue
    done = []
    if len(itemqueue) == 0:
        log(f"{time.strftime("%H:%M:%S")} | INFO | No items have been scanned\n","info")
        return

    for i in itemqueue[::-1]:
        if i not in done:
            num = itemqueue.count(i)
            done.append(i)
            eventqueue.append({
                "clientid": clientid,
                "id": "sale",
                "data": (i[0], num),
            })
    itemqueue = []

def onitem():
    global values, eventqueue, itemqueue, writable

    if not writable:
        log(f"{time.strftime("%H:%M:%S")} | INFO | Provided data is invalid\n","info")
        return

    elif not searchable:
        log(f"{time.strftime("%H:%M:%S")} | INFO | No items have been scanned\n","info")
        return

    values.append(itemqueue[-1][0])

    eventqueue.append({
        "clientid": clientid,
        "id": "item",
        "data": values,
    })
    itemqueue = itemqueue[:-1]
    nameentry.delete(0, tk.END)
    priceentry.delete(0, tk.END)
    quantityentry.delete(0, tk.END)
    companyentry.delete(0, tk.END)

def onaddstock():
    global itemqueue, eventqueue
    done = []
    if not searchable:
        log(f"{time.strftime("%H:%M:%S")} | INFO | No items have been scanned\n","info")
        return

    for i in itemqueue[::-1]:
        if i not in done:
            num = itemqueue.count(i)
            done.append(i)
            eventqueue.append({
                "clientid": clientid,
                "id": "stock",
                "data": (i[0], num),
            })
    itemqueue = []

def onsearchitem():
    global itemqueue, searchable
    if not searchable:
        log(f"{time.strftime("%H:%M:%S")} | INFO | No items have been scanned\n", "info")
        return
    eventqueue.append({
        "clientid": clientid,
        "id": "search",
        "data": itemqueue[-1][0],
    })
    itemqueue = itemqueue[:-1]

def onscan(event):
    global currentitem, itemqueue, barcodeentry
    barcode = barcodeentry.get()
    if barcode.replace(" ", "") == "":
        return
    check = checkitem(barcode)
    itemqueue.insert(0, (barcode, check[1]))
    barcodeentry.delete(0, tk.END)

def startscan(event):
    global keytime
    keytime = time.time()

def clearqueue(event):
    global itemqueue
    itemqueue = []

def log(message, tag = None):
    logwindow.insert(tk.END, message, tag)
    logwindow.see(tk.END)

root.title(f"GannonPOS ClientServer Hybrid")
logtext = f"{time.strftime("%H:%M:%S")} | GannonPOS terminal | Server session identifier = {clientid}\n"
barcodeentry.bind(config["terminatescan"], onscan)
root.bind("<Escape>", clearqueue)
root.bind('<Key>', startscan)

makesalebutton.configure(command = onmakesale)
additembutton.configure(command = onitem)
addstockbutton.configure(command = onaddstock)
searchitembutton.configure(command = onsearchitem)

log(logtext)

#Server code
#Event queue follows clientid, id, data in FIFO system
HOST = config["host"]
PORT = config["port"]
eventqueue = []
lock = threading.Lock()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
response = {}
response_events = {}

def listen():
    global response, response_events, searchable, writable
    while True:
        try:
            conn, addr = server.accept()
            data = conn.recv(1024).decode()

            if data:
                newevent = json.loads(data)

                with lock:
                    client = newevent["clientid"]

                    response[client] = None
                    response_events[client] = threading.Event()

                    eventqueue.append(newevent)

                if newevent["return"]:
                    response_events[client].wait()

                    with lock:
                        conn.send(json.dumps(response[client]).encode())
                        response_events[client].clear()
                        response[client] = None

            conn.close()

        except BlockingIOError:
            pass

def returntoserver(event, out):
    with lock:
        response[event["clientid"]] = out
        if event["clientid"] in response_events:
            response_events[event["clientid"]].set()

(listener := threading.Thread(target=listen, daemon=True)).start()

def update_loop():
    global searchable, writable, eventqueue, response, response_events, values
    scanned.delete(0.0, tk.END)
    price = 0.0

    if itemqueue:
        scanned.insert(0.0, "SCANNED: ")
        done = []
        for i in itemqueue:
            if i[1]:
                price += i[1][0]

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

    with lock:
        events_to_process = eventqueue[:]
        eventqueue.clear()

    for event in events_to_process:
        if (event["clientid"] != clientid) and (event["id"] not in ["connect", "disconnect"]):
            log(f"{time.strftime("%H:%M:%S")} | CLIENT | Client {event["clientid"]} made a {str(event["id"]).upper()} request\n","client")

        match event["id"]:
            case "check":
                out = checkitem(event["data"])
                returntoserver(event, out)

            case "sale":
                #Takes "data", barcode id to decrement by one
                #Decrements by one, adding to list if stock is 0
                out = makesale(event["data"])
                if event["clientid"] == clientid:
                    if out:
                        log(f"{time.strftime("%H:%M:%S")} | SALE | Sold {event["data"][1]} of item {event["data"][0]}\n")
                    else:
                        log(f"{time.strftime("%H:%M:%S")} | ERROR | Item {event["data"][0]} not found in database\n","error")
                else:
                    returntoserver(event, out)

            case "item":
                #Takes "data", consisting of a list of all attributes of new / updated entry
                out = item(event["data"])
                if out[1]:
                    if event["clientid"] == clientid:
                        log(f"{time.strftime("%H:%M:%S")} | ITEM | Updated item {out[0][-1]}: {list(out[0][:-2])}\n")
                    else:
                        returntoserver(event, out)
                else:
                    if event["clientid"] == clientid:
                        log(f"{time.strftime("%H:%M:%S")} | ITEM | Created new item {out[0][-1]}: {list(out[0][:-1])}\n")
                    else:
                        returntoserver(event, out)

            case "stock":
                # Takes "data", barcode id to increment by one
                # Increments by one
                out = addstock(event["data"])
                if event["clientid"] == clientid:
                    if out:
                        log(f"{time.strftime("%H:%M:%S")} | STOCK | Added {event["data"][1]} of item {event["data"][0]}\n")
                    else:
                       log(f"{time.strftime("%H:%M:%S")} | ERROR | Item {event["data"][0]} not found in database\n", "error")
                else:
                    returntoserver(event, out)

            case "search":
                #Takes "data" as a barcode id, returning info on the product
                result = searchitem(event["data"])
                if event["clientid"] == clientid:
                    if result:
                        nameentry.delete(0, tk.END)
                        priceentry.delete(0, tk.END)
                        quantityentry.delete(0, tk.END)
                        companyentry.delete(0, tk.END)

                        nameentry.insert(0, result[0])
                        priceentry.insert(0, result[1])
                        quantityentry.insert(0, result[2])
                        companyentry.insert(0, result[3])

                        log(f"{time.strftime("%H:%M:%S")} | SEARCH | Fetched item {event["data"]}: {list(result[:-1])}\n")
                    else:
                        log(f"{time.strftime("%H:%M:%S")} | ERROR | Item {event["data"]} not found in database\n", "error")
                else:
                    returntoserver(event, result)

            case "connect":
                log(f"{time.strftime("%H:%M:%S")} | CLIENT | Client connected | Client identifier {event["clientid"]}\n", "client")
                returntoserver(event, [True, clientid])

            case "disconnect":
                log(f"{time.strftime("%H:%M:%S")} | CLIENT | Client disconnected | Client identifier {event["clientid"]}\n","client")

    root.after(50, update_loop)

update_loop()
root.mainloop()