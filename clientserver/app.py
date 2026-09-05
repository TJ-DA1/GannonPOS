import tkinter as tk
root = tk.Tk()
root.configure(background="gray18")

barcodeentry = tk.Entry(root)
scanned = tk.Text(root, bg="gray18", fg="white")
scanned.tag_config('found', foreground="white")
scanned.tag_config('notfound', foreground="red")
barcodeinfo = tk.Label(root, text="Click below to scan item", bg="gray18", fg="white")

root.geometry("800x420")
root.minsize(800, 420)
root.maxsize(800, 420)

makesalebutton = tk.Button(root, text="Make sale", bg="pink1")
additembutton = tk.Button(root, text="Edit / new item", bg="steelblue1")
addstockbutton = tk.Button(root, text="Add stock", bg="yellow green")
searchitembutton = tk.Button(root, text="Search item", bg="orange2")

namein = tk.StringVar()
pricein = tk.StringVar()
quantityin = tk.StringVar()
companyin = tk.StringVar()

nameentry = tk.Entry(root, textvariable=namein, highlightcolor="gray18")
priceentry = tk.Entry(root, textvariable=pricein, highlightcolor="gray18")
quantityentry = tk.Entry(root, textvariable=quantityin, highlightcolor="gray18")
companyentry = tk.Entry(root, textvariable=companyin, highlightcolor="gray18")

nameentryinfo = tk.Label(root, text="Product name", bg="gray18", fg="white")
priceentryinfo = tk.Label(root, text="Price", bg="gray18", fg="white")
quantityentryinfo = tk.Label(root, text="Quantity in stock", bg="gray18", fg="white")
companyentryinfo = tk.Label(root, text="Company", bg="gray18", fg="white")

logwindow = tk.Text(root, bg="black", fg="white", highlightcolor="gray18", insertbackground="white")
logwindow.tag_config('error', foreground="red")
logwindow.tag_config('client', foreground="green")
logwindow.tag_config('info', foreground="blue")

pricetotal = tk.Label(root, text="Total: 0.00", bg="gray18", fg="white")
pricetotal.place(x=200, y=360, height=20)

logwindow.place(x=200 ,y=50, width= 600, height = 310)

makesalebutton.place(x=0, y=0, width=100, height=190)
additembutton.place(x=100, y=0, width=100, height=190)
addstockbutton.place(x=0, y=190, width=100, height=190)
searchitembutton.place(x=100, y=190, width=100, height=190)

nameentryinfo.place(x=200, y=0, width=180)
companyentryinfo.place(x=380, y=0, width=180)
priceentryinfo.place(x=560, y=0, width=120)
quantityentryinfo.place(x=680, y=0, width=120)

nameentry.place(x=200, y=20, width=180)
companyentry.place(x=380, y=20, width=180)
priceentry.place(x=560, y=20, width=120)
quantityentry.place(x=680, y=20, width=120)

barcodeinfo.place(x=650, y=360)
barcodeentry.place(x=650, y=380, height=35, width=145)
scanned.place(x= 0, y=381, height=34)