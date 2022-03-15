# Import FPDF class
import copy

import serial
import codecs
from fpdf import FPDF
from tkinter import *
from tkinter import messagebox, Tk
from datetime import date
from datetime import datetime
from distutils.core import setup
from Cython.Build import cythonize
import serial.tools.list_ports



ser = serial.Serial("COM4", baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2, xonxoff=False, rtscts=True)



sum = 0
count = 0
sum_0_8 = 0
sum_8_16 = 0
ADC = []
U_wy = []
U_wy_2 = []
max_val_ADC = 4096
U_ref = 2.5
PD = 3

while True:

    if ser.inWaiting():
        packet = ser.readline()
        count = count + 1
        hex = codecs.encode(packet, "hex")
        sum = sum + int(hex[:-2], 16)
        print(int(hex[:-2], 16))
        ADC.append(int(hex[:-2], 16))

        if count == 10:
           sum_0_8 = sum-255-16


        if count == 18:
            sum_8_16 = sum - 255 - 16 -sum_0_8

        if count == 21:

            print(int(sum_0_8))
            print(int(sum_8_16))
            break


for x in ADC:
    U_wy.append(round((x/max_val_ADC)*U_ref*PD, 2))
    U_wy_2.append(round((x/max_val_ADC)*U_ref*PD, 2))


print(U_wy_2)

file_read = open("readme.txt", "r+")
file_read.truncate(0)
file_read.close()

with open("options.txt", "r") as file:
    options = [[str(x) for x in line.split()] for line in file]


# creating our root
root: Tk = Tk()
root.geometry("350x150")
root.title('Data')

# textbox
e = Entry(root)
e.get()
e.insert(0, "Enter serial number: ")

today = date.today()
now = datetime.now()
current_time = now.strftime("%H:%M:%S")

name_entry = Entry(root)
name_entry.get()
name_entry.insert(0, "Enter name: ")

newWindow = None
new_name = None


# adding DropMenu choice to a textfile
def callback(selection):
    name_e = name_entry.get()
    with open('readme.txt', 'r+') as f:
        data = f.read()
        f.seek(0, 0)
        selection = str(selection).replace("[", "")
        selection = str(selection).replace("]", "")
        selection = str(selection).replace(",", "")
        selection = str(selection).replace("'", "")
        f.write(str(selection) + '\n' + str(data))




# Yes or No button
def popup():
    response = messagebox.askyesno("Info", "Data received. Do you want to exit?")
    ser.write(bytes(b'c'))
    if response == 0:
        Label(root, text="Data receied").pack()
    else:
        root.destroy()


# view serial number and add to a textfile
def myClick():
    myLabel = Label(root, text="Serial number: " + e.get())

    entry = e.get()
    with open('readme.txt', 'r+') as f:
        data = f.read()
        f.seek(0, 0)
        f.write(entry + '\n' + data)
    with open('readme.txt', 'r+') as f:
        data = f.read()
        f.seek(0, 0)
        f.write(str(today) + '\n' + data)

    myLabel.pack()


def create_secondwindow_button():
    with open('options.txt', 'r+') as f:
        data = f.read()
        f.seek(0, 0)
        f.write(str(new_name.get()) + "\n" + data)
        Tk.update(root)

    with open('readme.txt', 'r+') as f:
        data = f.read()
        f.seek(0, 0)
        f.write(str(new_name.get()) + '\n' + str(data))

    newWindow.destroy()


def OpenNewWindow():
    global newWindow
    global new_name
    newWindow = Toplevel(root)
    newWindow.title("New Window")
    newWindow.geometry("100x100")
    button = Button(newWindow, text="Submit", command=create_secondwindow_button)
    new_name = Entry(newWindow)
    new_name.get()
    new_name.insert(0, "Entry name: ")
    new_name.pack()
    button.pack()
    options.append(new_name.get())


# options for a DropMenu
# options = [
#    "Ola Maslak",
#    "Maria Zakolska",
#    "Andrzej Kwasniewski",
# ]


clicked = StringVar()
# clicked.set(options[0])
clicked.set(" ")

SerialLabel = Label(root, text="Serial number: ", padx=5, pady=5)
myButton = Button(root, text="Submit", command=myClick, fg="white", bg="green")
myLabel = Label(root, text="Contractor: ", padx=5, pady=5)
myCheckLabel = Label(root, text="Approval: ")
button_newWindow = Button(root, text="Add new person", command=OpenNewWindow)

drop = OptionMenu(root, clicked, *options, command=callback)
button_quit = Button(root, text="EXIT", command=root.quit)
button_info = Button(root, text="Connecting to device", command=popup)

# Pack to root

SerialLabel.grid(row=0, column=0)
e.grid(row=0, column=1)
myLabel.grid(row=1, column=0)
drop.grid(row=1, column=1)
button_newWindow.grid(row=1, column=2)
myCheckLabel.grid(row=2, column=0)
myButton.grid(row=2, column=1)
button_info.grid(row=3, column=0, columnspan=5) #connect to devive

button_quit.grid(row=4, column=0, columnspan=3)

root.mainloop()


# Create instance of FPDF class
# Letter size paper, use inches as unit of measure

class PDF(FPDF):
    def header(self):
        self.image('biale_tlo.png', 1, 1, 6)
        self.set_font('Times', 'BI', 10)
        self.cell(0, 2, 'Wersja 1.3 z dn. 14.02.2022 r.', align='R')

    def footer(self):
        self.set_y(-7)
        self.set_font('', 'I', 12)
        self.image('stopka.png', 1, 23, 20)
        self.cell(0, 10, f'Strona {self.page_no()}' + '/{nb}', align='C')


pdf = PDF(format='A4', unit='cm')
pdf.alias_nb_pages()
# Add new page. Without this you cannot create the document.
pdf.add_page()
th = pdf.font_size

# matrix initialization with preliminary data
data_info = [
    ['0'],
    ['0'],
    ['0'],
    ['0']
]

file_info = open('readme.txt', 'r').read()
lines_info = file_info.split('\n')

z = 0
for line_i in lines_info:
    data_info[z][0] = str(line_i)
    z = z + 1

    pdf.ln(th)

# Effective page width, or just epw
# epw - area between the left and right margin of the document
epw = pdf.w - 2 * pdf.l_margin

pdf.ln(3)
pdf.set_font('Arial', 'B', 20)
pdf.cell(epw, 0, 'Pomiary elektryczne wyrobu', align='C')
pdf.ln(1)
pdf.cell(epw, 0, 'Plasma Fission', align='C')
pdf.ln(2)
pdf.set_font('Arial', '', 13)
pdf.cell(epw, 0, 'Data generacji dokumentu: ' + str(data_info[0][0]) + "; " + current_time, align='L')
pdf.ln(1)
pdf.cell(epw, 0, 'Imie i nazwisko osoby wykonujacej pomiary: ' + str(data_info[2][0]), align='L')
pdf.ln(1)
pdf.cell(epw, 0, 'Numer identyfikacyjny przyrzadu pomiarowego: ' + str(data_info[1][0]), align='L')
pdf.ln(1)
pdf.cell(epw, 0, 'Numer seryjny urzadzenia: ' + str(data_info[1][0]), align='L')
pdf.ln(1)
pdf.cell(epw, 0, 'Sygnal odniesienia:     GND ', align='L')
pdf.ln(2)
pdf.set_font('', 'B', 13)
pdf.cell(epw, 0, 'Opis sygnalow:  ', align='L')
pdf.ln(1)
pdf.set_font('', '', 10)
pdf.cell(epw, 0, ' ', align='L')
pdf.ln(1)
pdf.cell(epw, 0, '12V DC - Napiecie wejsciowe ladowania akumulatora z zewnetrznej ladowarki ', align='L')
pdf.ln(0.5)
pdf.cell(epw, 0, 'Uload - Napiecie ladowania akumulatora(wyjscie ukladu ladowania)', align='L')
pdf.ln(0.5)
pdf.cell(epw, 0, 'Ubat - Napiecie akumulatora', align='L')
pdf.ln(0.5)
pdf.cell(epw, 0, '3V3 - Napiecie zasilania logiki sterujacej', align='L')
pdf.ln(0.5)
pdf.cell(epw, 0, 'Uzas - Napiecie zasilania za ukladem zalaczania', align='L')
pdf.ln(0.5)
pdf.cell(epw, 0, 'Oled_in - Napiecie zasilania przetwornicy do wyswietlacza OLED', align='L')
pdf.ln(0.5)
pdf.cell(epw, 0, 'Oled_out - Napiecie zasilania wyswietlacza OLED(na zlaczu)', align='L')
pdf.ln(0.5)
pdf.cell(epw, 0, 'Ugen - Napiecie zasilania generatora', align='L')
pdf.ln(0.5)
pdf.cell(epw, 0, 'Uster - Napiecie sterowania generatora HV DC', align='L')

# Set column width to 1/x of effective page width to distribute content
# evenly across table and page
# columns width change
col_width = epw / 6
col_width1 = epw / 7

data_name = [
    ['Punkt pomiarowy', 'Min. wartosc [V DC]', 'Max. wartosc [V DC]',
     'Zmierzona wartosc [V DC]', 'Uwagi']
]

data = [
    ['12V DC', '11.0 ', '12.6', ' ', ' '],
    ['Uload', '5.0 ', '8.5 ', ' ', ' '],
    ['Ubat', '5.4 ', '8.35 ', ' ', ' '],
    ['3V3', '3.25 ', '3.35 ', ' ', ' '],
    ['Uzas', 'Ubat - 0.15', 'Ubat', ' ', ' '],
    ['Oled_in', 'Uzas - 0.1', 'Uzas', ' ', ' '],
    ['Oled_out', '13.5', '14.5', ' ', ' '],
    ['Utantal', '3.8', '4.5', ' ', ' '],
    ['FB', '1.18', '1.28', ' ', ' '],
    ['1cell', '2.5', '4.25', ' ', ' ']
]

data_final = [
    ['LVL1', '2.40 ', '2.50 ', ' ', ' '],
    ['LVL2', '2.69 ', '2.79 ', ' ', ' '],
    ['LVL3', '2.99 ', '3.09 ', ' ', ' '],
    ['LVL4', '3.29 ', '3.39 ', ' ', ' '],
    ['LVL5', '3.58 ', '3.68 ', ' ', ' '],
    ['LVL6', '3.89 ', '3.99 ', ' ', ' '],
    ['LVL7', '4.21 ', '4.31 ', ' ', ' '],
    ['LVL8', '4.47 ', '4.57 ', ' ', ' '],
    ['LVL9', '4.77 ', '4.87 ', ' ', ' '],
    ['LVL10', '5.19 ', '5.29 ', ' ', ' '],  # new table
    ['LVL1', '2.45 ', '2.55 ', ' ', ' '],
    ['LVL2', '2.76 ', '2.86 ', ' ', ' '],
    ['LVL3', '3.07 ', '3.17 ', ' ', ' '],
    ['LVL4', '3.38 ', '3.48 ', ' ', ' '],
    ['LVL5', '3.70 ', '3.80 ', ' ', ' '],
    ['LVL6', '4.01 ', '4.11 ', ' ', ' '],
    ['LVL7', '4.32 ', '4.42 ', ' ', ' '],
    ['LVL8', '4.63 ', '4.73 ', ' ', ' '],
    ['LVL9', '4.95 ', '5.05 ', ' ', ' '],
    ['LVL10', '5.45 ', '5.53 ', ' ', ' ']

]

th = pdf.font_size

pdf.set_font('Times', '', 10)
pdf.ln(0.5)

file = open('do_testu.txt', 'r').read()
lines = file.split('\n')

#i = 0
#for line in lines:
#    data[i][3] = str(line)
#    i = i + 1


del U_wy[11:21]
del U_wy[0:1]

print(U_wy)

i = 0
for x in U_wy:
    data[i][3] = str(x)
    i = i + 1


    pdf.ln(th)

# zmiana Ubat i Uzas
data[4][1] = str(round(float(data[2][3]) - 0.15, 2))
data[4][2] = str(data[2][3])
data[5][1] = str(float(data[4][3]) - 0.1)
data[5][2] = str(data[4][3])

pdf.ln(2 * th)

pdf.set_font('Times', 'B', 9)
pdf.ln(0.2)

pdf.add_page()
pdf.ln(5)
pdf.cell(70, 10, ' ')
pdf.ln(0.2)

# Naglowki kolumn

count3 = 0
for row in data_name:
    for datum in row:
        # Enter data in colums

        if count3 == 4:
            pdf.cell(col_width - 0.5, 3 * th, str(datum), border=1, align='C')
        if count3 == 3:
            pdf.cell(col_width + 0.9, 3 * th, str(datum), border=1, align='C')
        if count3 < 3:
            pdf.cell(col_width + 1.12, 3 * th, str(datum), border=1, align='C')

        count3 += 1

    pdf.ln(3 * th)

pdf.set_font('Times', '', 10)

count = 0

# Kolumny pojedyncze
for row in data:
    count4 = 0
    for datum in row:
        # Enter data in colums

        if (data[count][1] < data[count][3]) & (data[count][3] < data[count][2]):
            pdf.set_fill_color(153, 255, 153)
            if count4 == 4:
                pdf.cell(col_width - 0.5, 3 * th, str(datum), border=1, align='C', fill=True)

            if count4 == 3:
                pdf.cell(col_width + 0.9, 3 * th, str(datum), border=1, align='C', fill=True)

            if count4 < 3:
                pdf.cell(col_width + 1.12, 3 * th, str(datum), border=1, align='C', fill=True)
            count4 += 1

        else:

            pdf.set_fill_color(255, 128, 128)
            if count4 == 4:
                pdf.cell(col_width - 0.5, 3 * th, str(datum), border=1, align='C', fill=True)

            if count4 == 3:
                pdf.cell(col_width + 0.9, 3 * th, str(datum), border=1, align='C', fill=True)

            if count4 < 3:
                pdf.cell(col_width + 1.12, 3 * th, str(datum), border=1, align='C', fill=True)
            count4 += 1

    count += 1
    pdf.ln(3 * th)

# Rozpoczecie pracy nad druga tabela

file1 = open('readme1.txt', 'r').read()
lines1 = file1.split('\n')

j = 0
for line1 in lines1:
    data_final[j][3] = str(line1)
    j = j + 1

    pdf.ln(th)

data_final[0][3] = str(U_wy_2[11])
data_final[10][3] = str(U_wy_2[12])


pdf.set_font('Times', '', 10)
pdf.ln(0.5)
pdf.multi_cell(0, 4, '\n')
pdf.cell(col_width1, 30 * th, 'Ugen', border=1, align='C')

pdf.set_fill_color(255, 255, 255)

k = 0
count2 = 0
for row in data_final:

    if (k > 0) & (k < 10):
        pdf.cell(col_width1, 10 * th, ' ', border=0, align='C')

    if k == 10:
        pdf.add_page()
        pdf.multi_cell(0, 3, '\n')
        pdf.cell(col_width1, 30 * th, 'Uster', border=1, align='C')

    if (k > 10) & (k < 20):
        pdf.cell(col_width1, 10 * th, ' ', border=0, align='C')

    k = k + 1

    for datum in row:
        # Enter data in colums

        if (data_final[count2][1] < data_final[count2][3]) & (data_final[count2][3] < data_final[count2][2]):
            pdf.set_fill_color(153, 255, 153)
            pdf.cell(col_width1 + 0.5, 3 * th, str(datum), border=1, align='C', fill=True)
        else:
            pdf.set_fill_color(255, 128, 128)
            pdf.cell(col_width1 + 0.5, 3 * th, str(datum), border=1, align='C', fill=True)

    count2 += 1
    pdf.ln(3 * th)

pdf.output('pdf_1.pdf', 'F')
