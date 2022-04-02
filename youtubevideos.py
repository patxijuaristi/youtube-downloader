# -*- coding: utf-8 -*-
'''
Created on 27 mar. 2021

@author: Patxi Juaristi
'''
from tkinter import IntVar, Radiobutton, Tk, Frame, Text, Scrollbar, Label, Button, filedialog, \
    PhotoImage, StringVar, Entry, messagebox
from tkinter.constants import END
from threading import Thread, Lock
import utils
from youtube_scraper import YoutubeScraper
import youtube_downloader
import webbrowser
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
s=Service(ChromeDriverManager().install())
initChrome = webdriver.Chrome(service=s, options=chrome_options)
initChrome.quit()

raiz = Tk()
icono = PhotoImage(file=utils.resource_path("youtube.png"))
raiz.iconphoto(False, icono)
raiz.title("Youtube Downloader JuarisTech")

miFrame = Frame(raiz, width=1200, height=700)
miFrame.pack()

rutaCarpeta = StringVar()
directorioPath = StringVar()
subtSelect=True
inputKeywords=True
queDescargar = 'mp4'
listaV = []
hilos = 5

lockLista = Lock()
lockHilos = Lock()

####################################
subtitulosFrame=Frame(miFrame)
subtitulosFrame.grid(row=1, column=0, columnspan=5, padx=20, pady=7)

def selecSubt():
    global subtSelect
    if(opcionSubt.get()==2):
        subtSelect = False
    else:
        subtSelect = True

opcionSubt = IntVar()
opcionSubt.set(1)
monitor = Label(subtitulosFrame, text='Subtitles', font=('Arial', 12 ))
monitor.pack(side='left')

subtSi = Radiobutton(subtitulosFrame, text="Yes", variable=opcionSubt, value=1, command=selecSubt, font=('Arial', 12 )).pack(side='left')
subtNo = Radiobutton(subtitulosFrame, text="No", variable=opcionSubt, value=2, command=selecSubt, font=('Arial', 12 )).pack(side='left')

####################################
tipoInputFrame=Frame(miFrame)
tipoInputFrame.grid(row=3, column=0, columnspan=5, padx=20, pady=7)

def selecTipoInput():
    global inputKeywords
    if(opciontipoInput.get()==2):
        inputKeywords = False
    else:
        inputKeywords = True

opciontipoInput = IntVar()
opciontipoInput.set(1)
monitor = Label(tipoInputFrame, text='Input', font=('Arial', 12 ))
monitor.pack(side='left')

keyword= Radiobutton(tipoInputFrame, text="Keyword", variable=opciontipoInput, value=1, command=selecTipoInput, font=('Arial', 12 )).pack(side='left')
url = Radiobutton(tipoInputFrame, text="URL", variable=opciontipoInput, value=2, command=selecTipoInput, font=('Arial', 12 )).pack(side='left')

####################################
formatoFrame=Frame(miFrame)
formatoFrame.grid(row=2, column=0, columnspan=5, padx=20, pady=7)

def selecF():
    global queDescargar
    if(opcionFormato.get()==2):
        queDescargar = 'mp3'
    elif(opcionFormato.get()==3):
        queDescargar = 'subtitulos'
    else:
        queDescargar = 'jpg'

opcionFormato = IntVar()
opcionFormato.set(1)
formatoLabel = Label(formatoFrame, text='Download: ', font=('Arial', 12 ))
formatoLabel.pack(side='left')

jpgRadio = Radiobutton(formatoFrame, text="MP4", variable=opcionFormato, value=1, command=selecF, font=('Arial', 12 )).pack(side='left')
pngRadio = Radiobutton(formatoFrame, text="MP3", variable=opcionFormato, value=2, command=selecF, font=('Arial', 12 )).pack(side='left')
gifRadio = Radiobutton(formatoFrame, text="Only Subtitles", variable=opcionFormato, value=3, command=selecF, font=('Arial', 12 )).pack(side='left')

####

textResults = Text(miFrame, width=50, height=15)
textResults.grid(row=4, column=4, padx=5, pady=5)

scrollResults = Scrollbar(miFrame, command=textResults.yview)
scrollResults.grid(row=4, column=5, sticky="nsew")

textResults.config(yscrollcommand=scrollResults.set)

resultsLabel = Label(miFrame, text="Result: ", font=('Arial', 12))
resultsLabel.grid(row=4, column=3, padx=5, pady=5)

####

textKeywords = Text(miFrame, width=50, height=15)
textKeywords.grid(row=4, column=1, padx=5, pady=5)

scrollKws = Scrollbar(miFrame, command=textKeywords.yview)
scrollKws.grid(row=4, column=2, sticky="nsew")

textKeywords.config(yscrollcommand=scrollKws.set)

keywordsLabel = Label(miFrame, text="Input: ", font=('Arial', 12))
keywordsLabel.grid(row=4, column=0, padx=5, pady=5)

####


def split_list(a, n):
    k, m = divmod(len(a), n)
    lista =  list((a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)))
    listaSinVacios = []
    for i in lista:
        if len(i) > 0:
            listaSinVacios.append(i)
    return listaSinVacios


def scrapearYT(kwList):
    scraper = YoutubeScraper(directorioPath.get()+'/')
    i = 1
    if(scraper.initDriver()):
        for kw in kwList:
            result = scraper.scrapearVideo(kw)
            if(result != None):
                lockLista.acquire()
                listaV.append(result)
                lockLista.release()
            i += 1
    else:
        messagebox.showwarning(
            title='Chrome Driver Error', message='Error with the Chrome Driver. Probably you should need to update it')
    scraper.endDriver()
    lockHilos.acquire()
    global hilos
    hilos = hilos - 1
    if(hilos == 0):
        descargarContenido()
    lockHilos.release()


def empezarScraping():
    global hilos
    hilos = 5
    texto = textKeywords.get("1.0", END)
    kwList = texto.split('\n')
    kwList = list(filter(('').__ne__, kwList))
    textResults.delete(1.0, "end")

    if(len(kwList) == 0):
        messagebox.showwarning(
            title='Empty Keywords', message='You need to introduce the keywords to download from youtube')
        return

    if(directorioPath.get() != ''):        
        if(inputKeywords == False):
            descargarContenidoDeUrl(kwList)
            return
        divididos = split_list(kwList, hilos)
        if(len(divididos) < hilos):
            hilos = len(divididos)

        listaHilos = []
        for i in range(hilos):
            t = Thread(target = scrapearYT, args=(divididos[i],))
            listaHilos.append(t)
        
        for hil in listaHilos:
            hil.start()
        
    else:
        textResults.delete(1.0, "end")
        messagebox.showwarning(
            title='Path Not Set', message='Set the path to storage the output videos/audios/files')


def establecerDirectorio():
    path = filedialog.askdirectory(initialdir="/", title="Select file")
    if(path != ''):
        if(path[len(path) - 1] != '/' and path[len(path) - 1] != '\\'):
            path = path + '/'
    directorioPath.set(path)
    rutaCarpeta.set(path)

def descargarContenido():
    cont = 1
    for v in listaV:
        youtube_downloader.descargarVideo(v.url, v.keyword, queDescargar, subtSelect, directorioPath.get())
        textResults.insert(float(cont), str(cont) + ' /' +str(len(listaV)) + ' ' + v.keyword + ' OK\n')
        raiz.update()
        cont += 1

def descargarContenidoDeUrl(kwList):
    cont = 1
    for url in kwList:
        youtube_downloader.descargarVideo(url, '', queDescargar, subtSelect, directorioPath.get())
        textResults.insert(float(cont), str(cont) + ' /' +str(len(listaV)) + ' ' + url.replace('https://www.youtube.com/watch?v=','') + ' OK\n')
        raiz.update()
        cont += 1


ficheroFrame = Frame(miFrame)
ficheroFrame.grid(row=0, column=0, columnspan=5, padx=20, pady=(20, 5))

nameCarpeta = Label(ficheroFrame, text="Output folder", font=('Arial', 12)).pack(side='left')

nameCarpetaEntry = Entry(ficheroFrame, textvariable=rutaCarpeta, width=70)
nameCarpetaEntry.config(fg="red", justify="center", font=('Arial', 12))
nameCarpetaEntry.pack(side='left')

botonDir = Button(ficheroFrame, text="Folder", command=establecerDirectorio, bg='white', fg='black', font=('Arial', 12)).pack(side='left')

botonBuscar = Button(miFrame, text="Download", command=empezarScraping, bg='red', fg='white', font=('Arial', 14))
botonBuscar.grid(row=6, column=0, columnspan=5, pady=(15, 15))

def abrirWeb(url):
   webbrowser.open_new_tab(url)

link = Label(raiz, text="JuarisTech.com",font=('Helveticabold', 12), fg="blue", cursor="hand2")
link.pack(side='right')
link.bind("<Button-1>", lambda e:
abrirWeb("https://juaristech.com"))

raiz.mainloop()
