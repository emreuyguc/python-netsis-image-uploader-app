import os
import configparser
from os import listdir
from os import path

from os.path import isfile, join
from pathlib import Path
from tkinter import * 
from tkinter import messagebox
import pyodbc
from configparser import *
from datetime import datetime



config = ConfigParser()
config_filename = 'ayar.ini'

if not path.isfile(config_filename):
    with open(config_filename, 'w') as configfile:
        pass

config.read(config_filename)

if len(config.sections()) < 1:
    with open(config_filename, 'w') as configfile:
        config.add_section('MSSQL')
        config['MSSQL']['server'] = 'SERVER'
        config['MSSQL']['user'] = 'SA'
        config['MSSQL']['password'] = '123'
        config['MSSQL']['db'] = 'MY2021'
        config['MSSQL']['port'] = '1433'
        config.write(configfile)


driver = '{SQL Server}'
selectImageQuery= """SELECT KAYITNO,KOD,DOSYAADI,BILGIBOYUT FROM TBLEVRAK WHERE KOD = ? AND DOSYAADI = ? AND BILGIBOYUT = ?"""
updateImageQuery = """UPDATE TBLEVRAK SET BILGIBOYUT = ? , BILGI = ? , DOSYAADI = ? WHERE KOD = ? """
deleteImageQuery = """DELETE FROM TBLEVRAK WHERE KOD = ?"""
insertImageQuery = """
INSERT INTO [dbo].[TBLEVRAK]
           ([TABLOTIPI]
           ,[KOD]
           ,[EVRAKTIPI]
           ,[ACIKLAMA]
           ,[KAYITTAR]
           ,[DUZELTTAR]
           ,[KULID]
          ,[DOSYAADI]
           ,[BILGIBOYUT]
          ,[BILGI]
           ,[OBJECTID]
           ,[EVRAKGRUPID]
           ,[STORAGETYPE]
           ,[FILETYPE]
           ,[EVRAKPATH]
           ,[EVRAKEDITPATH]
           ,[DUZELTMEYAPANKUL]
           ,[EVRAKTARIHI]
           ,[EVRAKGUID])
     VALUES
           (1
            ,?
           ,0
           ,?
           ,?
           ,NULL
           ,1
           ,?
           ,?
           ,?
           ,NULL
           ,NULL
           ,0
           ,NULL
           ,NULL
           ,NULL
           ,NULL
           ,?
           ,NULL)"""

def baglantiKontrol(server,database,username,password,port):
    with open(config_filename, 'w') as configfile:
        config['MSSQL']['server'] = serverBox.get()
        config['MSSQL']['user'] = userBox.get()
        config['MSSQL']['password'] = passBox.get()
        config['MSSQL']['db'] = databaseBox.get()
        config['MSSQL']['port'] = portBox.get()
        config.write(configfile)
    global conn
    try:
        conn = pyodbc.connect('DRIVER='+driver+';PORT=port;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+password)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        messagebox.showinfo("Title", "BAĞLANTI VAR")
        cursor.close()
        procButton.grid(row=5,column=1)
        logList.grid(row=0,column=2,rowspan=6)
        imageCheckBox.grid(row=6,column=0,columnspan=2)
    except:
        messagebox.showinfo("Title", "BAĞLANTI HATASI")

def resimYukle():
    global conn
    
    logList.delete(0,END)
    imageDir = 'resimler'
    if ((path.exists(imageDir))) != False:
        images = [f for f in listdir(imageDir) if isfile(join(imageDir, f))]
        try:
            cursor = conn.cursor()
            stocks = []
            if(imageOverride.get()):
                for fileName in images:
                    DOSYA_AD = fileName.split('.')[0]
                    STOK_KOD = DOSYA_AD.split('_')[0]
                    if STOK_KOD not in stocks:
                        stocks.append(STOK_KOD)
                for STOK_KOD in stocks:
                    cursor.execute(deleteImageQuery,(STOK_KOD))
                    logList.insert(END,(STOK_KOD,'-->ONCEKİ RESİMLER SİLİNDİ !'))
                cursor.close()
                cursor = conn.cursor()
            
            for fileName in images:
                try:
                    DOSYA_AD = fileName.split('.')[0]
                    STOK_KOD = DOSYA_AD.split('_')[0]
                    RESIM_YOL= str(Path(imageDir).resolve()) +'\\'+ fileName 
                    RESIM_DATA_SIZE= str(os.stat(imageDir+'\\'+fileName).st_size)
                    
                    cursor.execute(selectImageQuery,(STOK_KOD,RESIM_YOL,RESIM_DATA_SIZE))
                    cek = cursor.fetchall()
                    

 
                    
                    if(len(cek) < 1):
                        RESIM_DATA = (convertToBinaryData(imageDir+'\\'+fileName))
                        cursor.execute(insertImageQuery , (STOK_KOD,fileName,datetime.now(),RESIM_YOL,RESIM_DATA_SIZE,RESIM_DATA,datetime.now()))
                        logList.insert(END,(fileName,'-->RESİM EKLENDİ'))
                    else:
                        logList.insert(END,(fileName,'-->RESİM MEVCUT!!'))
                    
                    
                    """
                    if(len(cek) < 1):
                        cursor.execute(insertImageQuery , (STOK_KOD,RESIM_YOL,RESIM_DATA_SIZE,RESIM_DATA))
                        logList.insert(END,(STOK_KOD,'-->RESİM EKLENDİ'))
                    else:
                        cursor.execute(updateImageQuery, (RESIM_DATA_SIZE, RESIM_DATA, RESIM_YOL, STOK_KOD))
                        logList.insert(END,(STOK_KOD,'-->RESİM GÜNCELLENDİ!!!'))
                    """
                    
                    conn.commit()
                except Exception as hata:
                    logList.insert(END,(STOK_KOD,'-->HATA!!!',hata))
            cursor.close()
            conn.close()
        except Exception as hata:
            logList.insert(END,('-->BAĞLANTI HATASI! KONTROL ÇALIŞTIR.',hata))
    else:
        logList.insert(END,('-->RESİMLER KLASÖRÜ BULUNAMADI'))
    logFileName = (str(datetime.now()).replace('-','_').replace(' ','_').replace(':','_')).split('.')[0]
    logFile = open(logFileName+'.log','w')
    for log in logList.get(0,END):    
        logFile.write(str(log)+'\n')
    logFile.close()

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

window = Tk()
# Gets the requested values of the height and widht.
windowWidth = window.winfo_reqwidth()
windowHeight = window.winfo_reqheight()
 
# Gets both half the screen width/height and window width/height
positionRight = int(window.winfo_screenwidth()/2.3 - windowWidth/1.8)
positionDown = int(window.winfo_screenheight()/2.1- windowHeight/1.8)
 
# Positions the window in the center of the page.
window.geometry("+{}+{}".format(positionRight, positionDown))
 

imageOverride = IntVar()

serverLabel = Label(text='SERVER')
serverBox = Entry()
serverBox.insert(END,config['MSSQL']['server'])

databaseLabel = Label(text='DATABASE')
databaseBox = Entry()
databaseBox.insert(END,config['MSSQL']['db'])

userLabel = Label(text='USER')
userBox = Entry()
userBox.insert(END,config['MSSQL']['user'])

passLabel = Label(text='PASSWORD')
passBox = Entry()
passBox.insert(END,config['MSSQL']['password'])

portLabel = Label(text='PORT')
portBox = Entry()
portBox.insert(END,config['MSSQL']['port'])


logList = Listbox(width=50)


checkButton = Button(text="KONTROL",command = lambda: baglantiKontrol(serverBox.get(),databaseBox.get(),userBox.get(),passBox.get(),portBox.get()))
procButton = Button(text="İŞLEME BAŞLA",command = lambda: resimYukle())

imageCheckBox = Checkbutton(text='ESKİ RESİMLER SİLİNSİN',variable=imageOverride, onvalue=1, offvalue=0)

serverLabel.grid(row=0,column=0)
serverBox.grid(row=0,column=1)

databaseLabel.grid(row=1,column=0)
databaseBox.grid(row=1,column=1)

userLabel.grid(row=2,column=0)
userBox.grid(row=2,column=1)

passLabel.grid(row=3,column=0)
passBox.grid(row=3,column=1)

portLabel.grid(row=4,column=0)
portBox.grid(row=4,column=1)

checkButton.grid(row=5,column=0)






window.mainloop()
