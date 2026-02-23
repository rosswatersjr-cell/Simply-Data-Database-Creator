import sqlcipher3.dbapi2 as sqlcipher
import hashlib
import tkinter as tk
from tkinter import *
from tkinter import font, Menu, colorchooser
from tkinter.filedialog import askopenfile
from win32api import GetMonitorInfo, MonitorFromPoint
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
from urllib.parse import urlparse
from email_validator import validate_email, EmailNotValidError
import webbrowser
import pyperclip# System ClipBoard
import subprocess
import webbrowser
import json
import shutil
import os
import sys
import re
version="2026.02.21"

def select_language(restart):
    with open('Config.json', 'r') as json_file:
        data = json.load(json_file)
    json_file.close()    
    if data['0']=="":change_language(restart)
    populate_menus()
    set_menu_defaults()
    color_menu.delete(0,END)
    populate_color_menu()
def change_password():
    read_config()
    if Language.get()=="English":
        title="Reset Password"
        msg="Please Enter The Present Login Password."
    elif Language.get()=="Spanish":
        title="Restablecer Contraseña"
        msg="Por favor, Introduzca la Contraseña de Inicio de Sesión Actual." 
    while True:
        old_password=my_askstring(title,msg, "")
        if old_password==None:return
        old_hashed_password=hash_password(old_password)
        if old_hashed_password==My_Pass.get():break
        else:
            if Language.get()=="English":
                title="< Incorrect password Entered! >"
                msg="Please Try And Enter The Password Again."
            elif Language.get()=="Spanish":
                title="< ¡Contraseña Incorrecta Introducida! >"
                msg="Por favor, Intenta Ingresar la Contraseña de Nuevo."
    if Language.get()=="English":
        title="Enter New Password"
        msg="Please Enter A New Login Password."
    elif Language.get()=="Spanish":
        title="Introduce una Nueva Contraseña"
        msg="Por favor, introduzca una nueva contraseña de inicio de sesión." 
    new_password=my_askstring(title,msg)
    if new_password==None:return
    My_Pass.set(hash_password(new_password))
    key=new_password
    key=key[::-1]
    Encryption_key.set(key)
    write_config(False)
    if Language.get()=="English":msg="Password Reset Completed!"
    elif Language.get()=="Spanish":msg="¡Restablecimiento de Contraseña Completado!"
    messagebox.showinfo(title,msg)
    DB.clear_data_view()
def change_language(restart=False):
    languages=["English","Spanish"]
    if Language.get()=="English":
        title="You Are Here → Select Program Language"
        msg1="Please Select The Desired Program Language.\n"
        msg2="This Program Will Restart In The Selected Language!"
        msg=msg1+msg2
    elif Language.get()=="Spanish": 
        title="Usted Está Aquí → Seleccione el Idioma del Programa"
        msg1="Seleccione el Idioma del Programa Ddeseado.\n"
        msg2="¡Este Programa se Reiniciará en el Idioma Seleccionado!"
        msg=msg1+msg2
    elif Language.get()=="":    
        title="You Are Here → Select Program Language"
        msg="Please Select The Desired Program Language.\n"
    lang=my_askstring(title, msg, languages)
    if lang=="" or lang==None:return
    Language.set(lang)
    write_config(True)
def read_config():
    try:
        with open('Config.json', 'r') as json_file:
            data = json.load(json_file)
            json_file.close()
        for key, value in data.items():
            if key=="0":Language.set(value)
            elif key=="1":width=float(value)
            elif key=="2":height=float(value)
            elif key=="3":x=float(value)
            elif key=="4":y=float(value)
            elif key=="5":Window_Color.set(value)
            elif key=="6":Heading_Text_Color.set(value)
            elif key=="7":Header_Bg_Color.set(value)
            elif key=="8":Odd_Text_Color.set(value)
            elif key=="9":Odd_Bg_Color.set(value)
            elif key=="10":Even_Text_Color.set(value)
            elif key=="11":Even_Bg_Color.set(value)
            elif key=="12":My_Pass.set(value)
            elif key=="13":Encryption_key.set(value)
        root.geometry('%dx%d+%d+%d' % (width, height, x, y))
        root.update()
    except Exception as e:
        if Language.get()=="English":
            title="< Reading Config.json File >"
            msg1=f'Error Reading Config.json:\n'
        else:    
            title="< Leyendo el Archivo Config.json >"
            msg1=f'Error al Leer el Archivo Config.json:\n'
        msg2= repr(e)
        msg=msg1+msg2
        messagebox.showerror(title,msg)
        root.geometry('%dx%d+%d+%d' % (root_width, root_height, root_x, root_y))
        pass
def write_config(restart=False):
    temp_dict={}
    sc=json.load(open("Config.json", "r"))
    json.dump(sc,open("Config.json", "w"),indent=4)
    temp_dict[0]=Language.get()
    temp_dict[1]=str(root.winfo_width())
    temp_dict[2]=str(root.winfo_height())
    temp_dict[3]=str(root.winfo_x())
    temp_dict[4]=str(root.winfo_y())
    temp_dict[5]=Window_Color.get()
    temp_dict[6]=Heading_Text_Color.get()
    temp_dict[7]=Header_Bg_Color.get()
    temp_dict[8]=Odd_Text_Color.get()
    temp_dict[9]=Odd_Bg_Color.get()
    temp_dict[10]=Even_Text_Color.get()
    temp_dict[11]=Even_Bg_Color.get()
    temp_dict[12]=My_Pass.get()
    temp_dict[13]=Encryption_key.get()
    with open("Config.json", "w") as outfile:json.dump(temp_dict, outfile)
    outfile.close()
    temp_dict.clear()
    if restart:restart_program()# Restart Program
def set_geometry():
    data={}
    try:
        with open('Config.json', 'r') as json_file:
            data = json.load(json_file)
            json_file.close()
        Language.set(data["Language"])    
        root.geometry('%dx%d+%d+%d' % (float(data["1"]), float(data["2"]), int(data["3"]), int(data["4"])))
        root.update()
    except:
        pass
class SQL3_Database():
    def __init__(self,parent):
        self.Data_Widgets={}# Collection Of Data View Widgets
        self.Edit_Widgets={}# Collection Of Edit View Widgets
        self.Column_Data=[]# Text Variables For Row_Widgets
        self.Column_Headers=[]# Text Variables For Header_Widgets
        self.Row_Widgets=[]# Data Row Widgets
        self.Header_Widgets=[]# Header Row Widgets
        self.Widget_Index=None# Selected Row Widgets Index Or Header Widgets Index
        self.Last_Row_Index=None# Previously Selected Row Index 
        self.Last_Header_Index=None# Previously Selected Header Index  
        self.Tree_View=None# Database View Window
        self.Edit_View=None# Database Edit Window
        self.Data_Frame=None#Data View Frame
        self.Edit_Frame=None# Edit View Frame
        self.Canvas=None
        self.Scrollbar=None
        self.Searching=False
    def validate_entries(self,string):
        regex=re.compile(r'[(0-9)(a-zA-Z)( )]*$') # Allow
        result=regex.match(string)
        return (string == "" 
        # Prevent duplicates
        or (string.count("'") == 0
            and string.count("(") == 0
            and string.count(")") == 0
            and result is not None
            and result.group(0) != ""))
    def on_validate_entries(self,P):
        return self.validate_entries(P) 
    def database_exist(self,db_name):
        try:
            conn=sqlcipher.connect('file:'+db_name+'?mode=ro', uri=True)
            exist=True
            conn.close()
            if Language.get()=="English":
                title="Create New Database"
                msg1=f"The Database Name You Selected {os.path.basename(db_name)} Already Exist!\n"
                msg2="Please Select A Different Name And Try Again."
            elif Language.get()=="Spanish":    
                title="Crear Nueva Base de Datos"
                msg1=f"¡El Nombre de Base de Datos que Seleccionaste {os.path.basename(db_name)} ya Existe!\n"
                msg2="Por favor, Elija un Nombre Diferente y Vuelva a Intentarlo."
            msg=msg1+msg2
            messagebox.showinfo(title,msg)
        except sqlcipher.DatabaseError:
            exist=False
        return exist
    def create_data_view(self):
        self.destroy_edit_view()
        self.Data_Widgets={}
        self.Data_Frame=ttk.Frame(root, style='My.TFrame')
        self.Data_Frame.pack(side=TOP, fill=BOTH, anchor=NW, expand=True)
        self.Data_Widgets[len(self.Data_Widgets)+1]=self.Data_Frame
        self.Tree_View=ttk.Treeview(self.Data_Frame, show="headings")
        self.Data_Widgets[len(self.Data_Widgets)+1]=self.Tree_View
        vsb=ttk.Scrollbar(self.Data_Frame, orient="vertical", command=self.Tree_View.yview)
        hsb=ttk.Scrollbar(self.Data_Frame, orient="horizontal", command=self.Tree_View.xview)
        self.Tree_View.configure(yscrollcommand=vsb.set)
        self.Tree_View.configure(xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.Data_Widgets[len(self.Data_Widgets)+1]=vsb
        self.Data_Widgets[len(self.Data_Widgets)+1]=hsb
        self.Tree_View.pack(side=TOP, expand=True, anchor=NW, fill=BOTH)
        self.Tree_View.bind("<Button-1>", self.on_treeview_clicked)
        self.Tree_View.bind("<Button-3>", self.sum_column)
        root.protocol("WM_DELETE_WINDOW", destroy)
        root.update()
    def sum_column(self,event):
        try:
            total=0.0
            col_index=self.Tree_View.identify_column(event.x)
            heading_text=self.Tree_View.heading(col_index, 'text')
            col_index=int(col_index.replace("#",""))-1
            for child in self.Tree_View.get_children():
                check_value=self.Tree_View.item(child)["values"][col_index]
                try:
                    float(check_value)
                except ValueError:
                    continue
                value= float(self.Tree_View.item(child)["values"][col_index])
                total += value
            if total>0.0:
                if Language.get()=="English":
                    title=f'< Get {heading_text} Summation  >'
                    msg=f'The Sum Of Column "{heading_text}" = {round(total,3)}'
                else:
                    title=f'< Obtener {heading_text} Suma  >'
                    msg=f'La Suma de la Columna "{heading_text}" = {round(total,3)}'
                messagebox.showinfo(title, msg)
        except:
            pass
    def cancel_edit_view(self,item=None):
        self.destroy_edit_view()
        Edit_Definitions.set(False)
        if item:
            if Language.get()=="Spanish":title='Estás Aquí → '+DB_Name.get()+' de Base de Ddatos → Crear Nueva Tabla Cancelada'
            else:title="You Are Here → Database: "+DB_Name.get()+" → Create New Table Cancelled"
            root.title(title)
        self.create_data_view()
        if Active_Table.get()!="":
            self.select_table(Active_Table.get())# Populate Table With New Entry
            enable_menubar("all")
        config_menu(None)
    def grid_edit_view(self,row):
        # Create Window Resizing Configuration
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.Edit_Frame.columnconfigure(0, weight=1)
        self.Edit_Frame.rowconfigure(0, weight=1)
        self.Canvas.create_window((0, 0), window=self.Edit_View, anchor="nw")# Window Grid For Widgets 
        self.Canvas.grid(row=0, column=0, sticky="nsew")
        self.Scrollbar.grid(row=row+1, column=0, sticky="ew")
    def create_edit_view(self):
        self.destroy_data_view()
        self.Edit_Widgets={}
        self.Header_Widgets=[]
        self.Row_Widgets=[]
        self.Last_Row_Index=None 
        self.Last_Header_Index=None 
        style.configure('Custom.TFrame', background="#e7e7e7")        
        self.Edit_Frame = ttk.Frame(root,style='Custom.TFrame')
        self.Edit_Frame.grid(row=0, column=0, sticky=NSEW)
        self.Edit_Widgets[len(self.Edit_Widgets)+1]=self.Edit_Frame
        self.Canvas = tk.Canvas(self.Edit_Frame, bg="#e7e7e7")
        self.Canvas.grid(row=0, column=0, sticky=NSEW)
        self.Edit_Widgets[len(self.Edit_Widgets)+1]=self.Canvas
        self.Scrollbar = ttk.Scrollbar(self.Edit_Frame, orient="horizontal", command=self.Canvas.xview)
        self.Canvas.configure(xscrollcommand=self.Scrollbar.set)
        self.Edit_Widgets[len(self.Edit_Widgets)+1]=self.Scrollbar
        self.Edit_View = ttk.Frame(self.Canvas, style='Custom.TFrame')
        self.Edit_View.bind("<Configure>", lambda e:self.Canvas.configure(scrollregion=self.Canvas.bbox(ALL)))
        self.Edit_View.grid(row=0, column=0, sticky=NSEW)
        self.Edit_Widgets[len(self.Edit_Widgets)+1]=self.Edit_View
        root.protocol("WM_DELETE_WINDOW", go_back)
        root.update()
    def validate_email(self,address):
        try:
            validated_email = validate_email(address, check_deliverability=True)
            return validated_email 
        except EmailNotValidError as e:
            return False
    def validate_url(self,url_to_validate):
        try:
            result = urlparse(url_to_validate)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
    def validate_ext_type(self,path):
        audio_exts=['.mp3','.wma','.wav','.mp2','.ac3','.aac','.eac3','.m4a','.wmav1','.wmav2','.opus','.ogg','.aiff','.alac','.ape','.flac']
        video_exts=['.mp4','.avi','.mov','.mkv','.mpg','.mpeg','.wmv','.webm','.flv','.mj2','.3gp','.3g2']
        image_exts=['.bmp','.jpg','.jpeg','.gif','.png','.ppm','.dib']
        url_exts=[".com",".net",".org",".gov",".info",".biz",".io",".co",".ai",".ca",".dev",".me",".de",".app",".in",".is",
                  ".ec",".com.ec",".info.ec",".med.ec",".pro.ec",".eu",".gg",".to",".ph",".us",".store",".nl",".id",".inc",
                  ".website",".xyz",".club",".online",".info",".best",".live",".tech",".pw",".pro",".uk",".tv",".cx",".mx",
                  ".fm",".cc",".world",".space",".vip",".life",".shop",".host",".fun",".icu",".design",".art",".coop"]
        email=self.validate_email(path)
        if email:return"email"
        ext=os.path.splitext(path)
        ext=ext[1]
        if ext==".pdf" or ext==".txt":return ext
        elif ext in audio_exts:return "audio"
        elif ext in video_exts:return "video"
        elif ext in image_exts:return "image"
        elif ext.isnumeric() or ext=="":return None
        else:
            try:
                found_ext=[e for e in url_exts if e in path]
                if found_ext:
                    is_url=self.validate_url(path)
                    if is_url:return "url"
                    else:return None
            except Exception as e:
                return None
    def play_avi(self,path):
        wmp_path = r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"#64-bit systems
        if not os.path.exists(wmp_path):
            wmp_path = r"C:\Program Files\Windows Media Player\wmplayer.exe"#32-bit systems
            if not os.path.exists(wmp_path):
                if Language.get()=="English":
                    title="< Windows Media Player >"
                    msg="Windows Media Player Not Found!"
                else:
                    title="< Reproductor de Windows Media >"
                    msg="¡Reproductor de Windows Media no Encontrado!"
                messagebox.showerror(title,msg)
                return
        try:
            subprocess.Popen([wmp_path, "/play", path])
        except Exception as e:
            if Language.get()=="English":
                title="< Windows Media Player >"
                msg1=f'Error Playing {path}\n'
            else:    
                title="< Reproductor de Windows Media >"
                msg1=f'Error al Reproducir {path}\n'
            msg2= repr(e)
            msg=msg1+msg2
            messagebox.showerror(title,msg)
    def get_row_values(self,row_id):
        try:
            encrypted=self.is_encrypted(Active_DB.get())
            conn = sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            cursor=conn.execute(f"SELECT * FROM {Active_Table.get()} WHERE id = {row_id}")
            row_data = cursor.fetchone()
        except sqlcipher.DatabaseError as e:
            if Language.get()=="Spanish":title,msg1='<Recuperar Fila de Tabla>','¡No se pudo recuperar la Fila de la Tabla!\n'
            else:title,msg1="<Fetch Table Row>","Failed to Retrieve Table Row!\n" 
            msg2=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2)
            row_data=None
        finally:
            if conn:conn.close()
        return row_data
    def edit_cell_data(self,original_data,column_id,cell_data):
        try:
            id=column_id-1
            data_list=list(original_data)
            data_list[id]=cell_data
            colm_names=self.get_main_columns()
            names=[]
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            cursor=conn.cursor()
            for c in range(len(colm_names)):
                names.append(colm_names[c].replace(" ","_"))
                if c>=1:
                    query=f"UPDATE {Active_Table.get()} SET {names[c]} = ? Where id = ?"
                    data=(data_list[c], data_list[0])
                    cursor.execute(query, data)
            conn.commit()
            if Language.get()=='Spanish':
                title='< Guardar Entrada Editada >'
                msg='¡Cambios de Entrada Editados Guardados!'
            else:    
                title='< Save Edited Entry >'
                msg="Edited Entry Changes Saved!"
            messagebox.showinfo(title, msg)
            enable_menubar("all")
            config_menu(None)
        except sqlcipher.DatabaseError as e:
            if Language.get()=='Spanish':
                title='< Guardar Entrada Eeditada >'
                msg1='Tabla = '+Active_Table.get()+'\n'
                msg2='¡Guardar ID de Entrada Editado = '+data_list[0]+' Falló!\n'
            else:    
                title='< Save Edited Entry >'
                msg1='Table = '+Active_Table.get()+'\n'
                msg2='Save Edited Entry ID = '+data_list[0]+' Failed!\n'
            msg3=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2+msg3)
            enable_menubar("all")
            config_menu(None)
        finally:
            if conn:conn.close()
            self.select_table(Active_Table.get())# Populate Table With New Edited Entries
    def on_treeview_clicked(self,event):
        try:# Identify What was clicked (Heading Or Cell)
            region=self.Tree_View.identify_region(event.x, event.y)# Returns'heading', 'cell'
            if region=="nothing":return
            if region=="heading":
                heading=self.Tree_View.identify_column(event.x)
                heading_text=self.Tree_View.heading(heading, 'text')
                if heading_text=="ID":return # ID Not Editable
                if Language.get()=="Spanish":
                    title="< Cambiar Nombre/Eliminar Columna >"
                    msg1="Seleccione la Acción a Realizar, luego haga\n "
                    msg2="Clic en OK para Continuar o Cancel para Salir."
                    choices=["Renombrar Columna", "Eliminar Columna"]
                else:      
                    title="< Rename/Delete Column >"
                    msg1='Select The Action To Perform, Then\n'
                    msg2="Click OK To Proceed Or Cancel To Exit!'"
                    choices=["Rename Column", "Delete Column"]
                msg=msg1+msg2    
                selection=my_askstring(title, msg, choices)
                if selection==choices[0]:
                    self.rename_column(heading_text)
                elif selection==choices[1]:
                    self.drop_column(heading_text)
            elif region=="cell":# Identify which Column and Row was clicked        
                if self.Searching:# Entry Clicked By Search Results
                    self.Searching=False
                    return
                row_data=self.Tree_View.identify_row(event.y)
                column_id=self.Tree_View.identify_column(event.x)
                column_id= int(column_id.replace("#",""))
                entry_data=list(self.Tree_View.item(row_data, 'values'))  # Get the values of the selected item
                row_id=entry_data[0]
                displayed_data=os.path.splitext(entry_data[column_id-1])
                heading=self.Tree_View.identify_column(event.x)
                heading_text=self.Tree_View.heading(heading, 'text')# Remove Extension For Viewing
                real_data=self.get_row_values(row_id)# Returns Complete Row Data  
                if heading_text=="ID":#ID Column was Clicked
                    if Language.get()=="Spanish":
                        title="< Editar/Eliminar Entrada de Tabla >"
                        msg1="Seleccione la Acción a Realizar, luego haga\n "
                        msg2="Clic en OK para Continuar o Cancel para Salir."
                        choices=[f"Editar {heading_text} {row_id} Fila", f"Eliminar {heading_text} {row_id} Fila"]
                    else:      
                        title="< Edit/Delete Table Entry >"
                        msg1='Select The Action To Perform, Then\n'
                        msg2="Click OK To Proceed Or Cancel To Exit!'"
                        choices=[f"Edit {heading_text} {row_id} Row", f"Delete {heading_text} {row_id} Row"]
                    msg=msg1+msg2    
                    selection=my_askstring(title, msg, choices)
                    if selection==choices[0]:
                        self.edit_table_row(real_data)
                    elif selection==choices[1]:
                        self.delete_selected_entry(real_data)
                else:# Examine Data and Determine Type, Then Execute
                    if not isinstance(real_data[column_id-1], str):value=str(real_data[column_id-1])# Convert Integer, Float To Str For Len
                    else:value=real_data[column_id-1]   
                    ext_type=self.validate_ext_type(value)
                    if ext_type==None:
                        if Language.get()=='English':choices=["Edit Cell Value"]
                        else:choices=["Editar Valor de la Celda"]
                        txt=""
                    elif ext_type=="url":
                        if Language.get()=='English':txt="Go To: "
                        else:txt="Ir a: "
                    elif ext_type=="email":
                        if Language.get()=='English':txt="Send Email To: "
                        else:txt="Enviar correo electrónico a: "
                    elif ext_type=="audio" or ext_type=="video":
                        if Language.get()=='English':txt="Play: "
                        else:txt="Reproducir: "
                    elif ext_type=="image":
                        if Language.get()=='English':txt="View: "
                        else:txt="Ver: "
                    elif ext_type==".pdf" or ext_type==".txt":
                        if Language.get()=='English':txt="Open: "
                        else:txt="Abrir: "
                    if txt!="":
                        if Language.get()=='English':
                            choices=[f"Edit Cell Value", f"{txt} {os.path.basename(displayed_data[0])}"]
                        else:
                            choices=[f"Editar Valor de la Celda", f"{txt} {os.path.basename(displayed_data[0])}"]    
                    if Language.get()=="Spanish":
                        title="< Editar/Ejecutar Archivo >"
                        msg1="Seleccione la Acción a Realizar, luego haga\n "
                        msg2="Clic en OK para Continuar o Cancel para Salir."
                    else:      
                        title="< Edit/Execute File >"
                        msg1='Select The Action To Perform, Then\n'
                        msg2="Click OK To Proceed Or Cancel To Exit!'"
                    msg=msg1+msg2    
                    selection=my_askstring(title, msg, choices)
                    if selection==None:return
                    if selection==choices[0]:
                        init_txt=real_data[column_id-1]
                        if Language.get()=='English':
                            msg1='Enter A New Cell Value, Then Click\n'
                            msg2="OK To Proceed Or Cancel To Exit!'"
                            title="Edit Cell Value"
                        else:
                            msg1='Ingrese un Nuevo Valor de Celda, luego haga Clic\n' 
                            msg2='en OK para Continuar o en Cancel para Salir.'    
                            title="Editar Valor de la Celda"
                        msg=msg1+msg2
                        selection=my_askstring(title, msg, init_txt)
                        if selection!=init_txt and selection!=None:
                            self.edit_cell_data(real_data,column_id,selection)
                        else:return    
                    elif selection==choices[1]:
                        if ext_type=="url":
                            webbrowser.open(real_data[column_id-1])
                        elif ext_type=="pdf":
                            if os.path.exists(real_data[column_id-1]):subprocess.Popen([real_data[column_id-1]], shell=True)
                        elif ext_type=="txt":
                            if os.path.exists(real_data[column_id-1]):subprocess.Popen(["notepad.exe", real_data[column_id-1]])
                            else:raise Exception()
                        elif ext_type=="audio" or ext_type=="video" or ext_type=="image":
                            if os.path.exists(real_data[column_id-1]):self.play_avi(real_data[column_id-1])
                            else:raise Exception()
                        elif ext_type=="email":
                            webbrowser.open(f'mailto:{value}')
                        else:return    
        except Exception as e:
            if Language.get()=="English":
                title="< Database Field Clicked >"
                msg1=f'Error Executing {displayed_data[0]}\n'
            else:    
                title="< Campo de Base de Datos Clicado >"
                msg1=f'Error al Ejecutar {displayed_data[0]}\n'
            msg2= repr(e)
            msg=msg1+msg2
            messagebox.showerror(title,msg)
    def create_new_database(self,db_type):
        if Language.get()=="Spanish":
            title,msg='Estás aquí → Crear Nueva Base de Datos','Ingrese un Nombre para esta Nuevo Base de Datos, luego haga clic en OK.' 
        else:
            title,msg="You Are Here → Create New Database",'Enter a Name For This New Database, Then Click OK.'        
        new_db=my_askstring(title, msg)
        if new_db=="" or new_db==None:return
        new_db=new_db.replace(" ","_")
        DB_Name.set(new_db)
        tbl_menu.delete(0,END)
        Active_Table.set("")
        db_file=os.path.join(DB_Path.get(), str(new_db+".db3"))
        if not self.database_exist(db_file):
            try:
                conn=sqlcipher.connect(db_file)
                if db_type=="encrypted":
                    conn.execute("PRAGMA cipher_default_kdf_iter = 256000;")
                    conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
                if Language.get()=="Spanish":title=f"Estás aquí → Nueva Base de Datos Creada → {new_db}"
                else:title=f"You Are Here → New Database Created → {new_db}"    
                Active_DB.set(db_file)
                conn.close()
                root.title(title)
                root.update()
                populate_db_menu()
                config_menu(None)
                self.create_new_table(db_type,None)
            except sqlcipher.DatabaseError as e:
                self.delete_selected_db(db_file,False)
                if Language.get()=="Spanish":title,msg1,msg2='<Crear Nueva Base de Datos>','¡'+new_db+' No Fue Creado!\n',f"Error: '{e}'"
                else:title,msg1,msg2='<Create New Database>',new_db+' Was Not Created!\n',f"Error: '{e}'"
                messagebox.showerror(title, msg1+msg2)
            finally:
                if conn:conn.close()
    def select_database(self,db_path,db_name):
        self.clear_data_view()
        DB_Path.set(db_path)
        Active_DB.set(os.path.join(db_path, db_name))
        DB_Name.set(os.path.splitext(db_name)[0])# Remove File Extension
        last_tbl=Active_Table.get()
        Active_Table.set('')
        if Language.get()=="Spanish":title='ESTÁ AQUÍ → '+DB_Name.get()+' de Base de Datos → Seleccione una Tabla'
        else:title="You Are Here → Database: "+DB_Name.get() +" → Select A Table"    
        root.title(title)
        root.update()
        tbl_menu.delete(0, END)
        tbls=self.fetch_tables()
        if tbls==None:return
        num_tbls=0
        if Language.get()=="English":
            txt1='Create New Table'
            txt2='Tables'
        else:
            txt1='Crear Nueva Tabla'
            txt2='Tablas'
        tbl_menu.add_command(label=txt1,command=self.create_new_table)
        tbl_menu.add_separator()
        arrow_label=str('↓ '+txt2+' ↓')
        tbl_menu.add_command(label=arrow_label)
        tbl_menu.entryconfig(arrow_label, state="disabled")
        tbl_menu.add_separator()
        for name in tbls:
            if name[0]!="sqlite_sequence":
                tbl_menu.add_command(label=name[0],command=lambda a=name[0]:self.select_table(a))
                tbl_menu.add_separator()
                first_tbl=name[0]
                if num_tbls==0:first_tbl=name[0]# 1st Table
                num_tbls+=1
        if num_tbls==0:
            if Language.get()=="English":
                menubar.entryconfig('     Create/Select Table     ', state="normal")
                tbl_menu.entryconfig("Create New Table", state="normal")
                modify_tbl_menu.entryconfig("Delete Table", state="disabled")
                modify_tbl_menu.entryconfig("Search Table", state="disabled")
            elif Language.get()=="Spanish":    
                menubar.entryconfig('     Crear/Seleccionar Tabla     ', state="normal")
                tbl_menu.entryconfig("Crear Nueva Tabla", state="normal")
                modify_tbl_menu.entryconfig("Eliminar Tabla", state="disabled")
                modify_tbl_menu.entryconfig("Tabla de Búsqueda", state="disabled")
        else:
            if Language.get()=="English":
                menubar.entryconfig('     Create/Select Table     ', state="normal")
                modify_tbl_menu.entryconfig("Delete Table", state="normal")
                modify_tbl_menu.entryconfig("Search Table", state="normal")
            elif Language.get()=="Spanish":    
                menubar.entryconfig('     Crear/Seleccionar Tabla     ', state="normal")
                modify_tbl_menu.entryconfig("Eliminar Tabla", state="normal")
                modify_tbl_menu.entryconfig("Tabla de Búsqueda", state="normal")
        config_menu('db_selected')
        if num_tbls!=0:# Display 1st Table or Previous Table When Database Selected
            for name in tbls:
                if name[0]!="sqlite_sequence":
                    if last_tbl==name[0]:first_tbl=name[0]
                    break
            self.select_table(first_tbl)
    def delete_selected_db(self,db_name,show=True):
        try:
            db_file=os.path.join(DB_Path.get(), db_name)
            if os.path.exists(db_file):os.remove(db_file)# Delete The Database File
            db_name=db_name.split(".")[0]# Remove The File Extension
            if db_file==Active_DB.get():
                Active_DB.set("")
                DB_Name.set("")
                Active_Table.set("")
                self.clear_data_view()
            populate_db_menu()
            tbl_menu.delete(0,"end")
            config_menu('db_deleted')
            if show:
                if Language.get()=="Spanish":title,msg='<Eliminar la base de datos> '+db_name,db_name+' eliminado con éxito!'
                else:title,msg='<Delete Database> '+db_name,db_name+' Deleted Successfully!' 
                messagebox.showinfo(title, msg)
        except Exception as ex:
            if Language.get()=="Spanish":title,msg1='<Eliminar la Base de Datos Seleccionada> '+db_name,'Error de eliminar la Base de Datos '+ db_name+'\n'
            else:title,msg1='<Delete Selected Database> '+db_name,db_name+' Error Deleting Database '+db_name+'\n'
            msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
    def import_database(self):
        try:
            if Language.get()=="English":txt="Sqlite Database Files"
            else:txt="Archivos de Base de Datos Sqlite"
            types=[(txt, DB_Extensions)]
            path=askopenfile(mode='r',initialdir="C:/",defaultextension="*.*",filetypes=types)
            if path is None:return
            encrypted=self.is_encrypted(path.name)
            if encrypted:
                if Language.get()=="English":
                    title,msg="Import Database","Database Is Encrypted And Cannot Be Imported!"
                else:
                    title,msg="Importar Base de Datos","¡La Base de Datos está Cifrada y no se Puede Importar!"
                messagebox.showerror(title,msg)
                return
            file_name=os.path.basename(path.name)
            file_ext=os.path.splitext(file_name)[1]
            if file_ext not in DB_Extensions:
                if Language.get()=="English":
                    title="<Import Database>"
                    msg1=f"The File Extension Is Not Recognized By {sqlcipher.sqlite_version}."
                    msg2="The Database File May Not Be Compatable!"
                    msg3="To Continue Press OK Or Cancel To Exit Import."
                else:    
                    title="<Importar Base de Datos>"
                    msg1=f"La extensión de archivo no es reconocida por {sqlcipher.sqlite_version}."
                    msg2="¡Es posible que el Archivo de la Base de Datos no sea Compatible!"
                    msg3="Para Continuar, presione OK o Cancel para Salir de la Importación."
                msg=msg1+msg2+msg3     
                messagebox.askokcancel(title, msg)
            if os.path.isfile(path.name):
                src=path.name
                dst_path=str(Path(__file__).parent.absolute())
                dst=os.path.join( dst_path,file_name)
            if not os.path.isfile(dst):# Copy File To Database Directory
                shutil.copy(src, dst)
                file_name=os.path.splitext(dst)[0]
                new_path=file_name+".db3"
                Active_DB.set(new_path)
                new_file_name=os.path.basename(new_path)
                new_name=os.path.splitext(new_file_name)[0]
                DB_Name.set(new_name)
                os.rename(dst, new_path)
                DB_Path.set(dst_path)
            if Language.get()=="Spanish":title,msg=='< Importar Base de Datos >','La Importación de la Base de Datos se realizó Correctamente.'
            else:title,msg="< Import Database >","Importing Database Was Successful!"
            messagebox.showinfo(title, msg)
            Active_Table.set("")
            populate_db_menu()
            Active_Table.set("")
        except Exception:
            pass    
    def delete_database(self):
        db_files=[file for file in os.listdir(DB_Path.get()) if os.path.splitext(file)[1] in DB_Extensions]# Retrieve All Databases In Folder
        if len(db_files)==0:
            if Language.get()=="Spanish":title,msg='<Eliminar la Base de Datos>','¡No se Encuentran Archivos de Base de Datos!'
            else:title,msg="<Delete Database>","No Database Files Found!"
            messagebox.showerror(title, msg)
            return
        if Language.get()=="Spanish":title,msg='Estás Aquí → Eliminar Base de Datos →','Seleccione la Base de Datos para Eliminar, luego haga clic en OK.'
        else:title,msg="You Are Here → Delete Database →",'Select The Database To Delete, Then Click OK.'
        root.title(title)
        root.update()
        selected=my_askstring(title, msg, db_files)
        if selected=="" or selected==None:return
        else: self.delete_selected_db(selected)
    def sort_table(self,order):
        colm_names=self.retrieve_column_names()
        if Language.get()=="English":
            title="Sort Column"
            msg1='Select The Column You Wish To Sort.\n'
            msg2='Click OK To Continue.'
        else:    
            title="Búsqueda por Palabra Clave"
            msg1='Introduce una Palabra Clave para Buscar.\n'
            msg2='Haga Clic en OK para Continuar.'
        msg=msg1+msg2
        colm_name=my_askstring(title, msg,colm_names)
        if colm_name==None or colm_name=="":return
        colm_name=colm_name.replace(" ","_")
        conn = None
        try:
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            cursor=conn.cursor()
            if order=="ASC":cursor.execute(f"SELECT * FROM {Active_Table.get()} ORDER BY {colm_name} ASC;")
            elif order=="DESC":cursor.execute(f"SELECT * FROM {Active_Table.get()} ORDER BY {colm_name} DESC;")
            sorted_rows=cursor.fetchall()
            self.clear_data_view()
            style.configure("Treeview", fieldbackground=Window_Color.get(), font=('Arial', 10, 'bold'))# Unused Porsion            
            style.configure("Treeview.Heading", background=Header_Bg_Color.get(), foreground=Heading_Text_Color.get(), font=('Arial', 10, 'bold'))
            style.map("Treeview.Heading", background=[('active', 'aqua'),('selected', 'aqua')])
            self.Tree_View.tag_configure('oddrow', background=Odd_Bg_Color.get(), foreground=Odd_Text_Color.get(), font=('Arial', 10, 'normal'))
            self.Tree_View.tag_configure('evenrow', background=Even_Bg_Color.get(), foreground=Even_Text_Color.get(), font=('Arial', 10, 'normal'))
            self.Tree_View.column('#0', width=0, stretch=False)# Hide Tree Structure
            columns = [description[0] for description in cursor.description]# Define columns
            self.Tree_View['columns'] = columns
            headings=[]
            for col in columns:# Set Column Headings Text into Treeview
                col_txt=col.replace("_"," ")
                self.Tree_View.heading(col, text=col_txt)
            c=0
            for row in sorted_rows:# Set Data Text into Treeview
                if c % 2 != 0:# Even Color
                    self.Tree_View.insert("", tk.END, values=row, tags = ("evenrow"))
                else:# Odd Color    
                    self.Tree_View.insert("", tk.END, values=row, tags = ("oddrow"))
                c+=1
            headings = {}
            self.Tree_View.pack(side='left', expand=True, fill='both')
            headings = {}
            for col in self.Tree_View['columns']:# Resize Column Widths To Max Size Of Text
                if col=="ID": multiplier=3
                else:multiplier=1.2
                heading_width=int(my_font.measure(col) * multiplier)
                col_txt=col.replace("_"," ")
                self.Tree_View.column(col, anchor='center', stretch=False, width=my_font.measure(self.Tree_View.heading(col)['text']))
                for row in self.Tree_View.get_children(''):
                    data_width = int(my_font.measure(self.Tree_View.set(row, col)) * 1.2)
                    headings[col] = int(self.Tree_View.column(col, width=None))
                    if data_width>=heading_width:width=data_width# Use Largest Width Heading vs Data
                    else:width=heading_width
                    self.Tree_View.column(col, width=max(self.Tree_View.column(col, 'width'), width))
            self.Tree_View.pack(side='left', expand=True, fill='both')
            root.update()
        except sqlcipher.DatabaseError as e:
            if Language.get()=="English":
                title=f"< Sort Table {order} >"
                msg1=f"Error Sorting Table {Active_Table.get()}"
            else:    
                title=f"< Ordenar Tabla {order} >"
                msg1=f"Error al Ordenar la Tabla {Active_Table.get()}"
                msg2=f"Error: {e}"
            msg=msg1+msg2    
            messagebox.showerror(title,msg)    
        finally:
            if conn:
                conn.close()
    def search_table(self):
        if Language.get()=="English":
            title="Keyword Search"
            msg1='Enter A Keyword To Search For.\n'
            msg2='Click OK To Continue.'
        else:    
            title="Búsqueda por Palabra Clave"
            msg1='Introduce una Palabra Clave para Buscar.\n'
            msg2='Haga Clic en OK para Continuar.'
        msg=msg1+msg2
        keyword=my_askstring(title, msg)
        if keyword==None or keyword=="":return
        query=str(keyword).lower()
        selections=[]
        row_ids=[]
        for c, child in enumerate(self.Tree_View.get_children()):
            lowercase_list = [str(item).lower() for item in self.Tree_View.item(child)['values']]
            if any(query in s for s in lowercase_list):# compare strings in lower cases.
                selections.append(child)
                row_ids.append(lowercase_list[0])# Row ID
                self.Tree_View.yview_moveto((1/len(self.Tree_View.get_children()))*(c))        
        self.Searching=True
        self.Tree_View.selection_set(selections)
        if len(selections)==0:
            if Language.get()=="English":
                title='< Search Results >'
                msg=f'No Search Results Found For "{keyword}"!'
            else:
                title='< Resultados de Búsqueda >'
                msg= f'¡No se Encontraron Resultados de Búsqueda para "{keyword}"!'   
        else:
            if Language.get()=="English":
                title='< Search Results >'
                msg=f'Search Results Found At ID Locations {row_ids}'    
            else:
                title='< Resultados de Búsqueda >'
                msg= f'Resultados de Búsqueda Encontrados en Ubicaciones de ID {row_ids}'   
        messagebox.showinfo(title, msg)
    def create_new_table(self,db_type=None,tbl_name=None):
        if Active_DB.get()=="":
            if Language.get()=="Spanish":
                title='<No se selecciona la Base de Datos>'
                msg='Se debe seleccionar una Base de Datos para continuar.\n¡Seleccione una Base de Datos y vuelva a intentarlo!'
            else:
                title='<No Database Selected>'
                msg='A Database Must Be Selected To Continue.\nPlease Select A Database And Try Again!'
            messagebox.showerror(title, msg)
            return
        colm_names=[]
        colm_data=[]
        colm_defs=[]
        colm_widths=[]
        if Edit_Definitions.get()==False:
            if Language.get()=="Spanish":
                title='Base de datos '+DB_Name.get()+' <Nuevo Nombre de la Tabla>'
                msg='Ingrese un Nombre para la Nueva Tabla y Luego haga Clic en OK Cuando esté Listo.'
            else:
                title="Database "+DB_Name.get()+" <New Table Name>"
                msg='Enter A Name For The New Table Then Click OK When Ready.'
            new_tbl=my_askstring(title, msg)
            if new_tbl=="" or new_tbl==None:return
            tbl_name=new_tbl
            new_tbl=new_tbl.replace(" ","_")
            tables=self.fetch_tables()
            for name in tables:# Check For Table Already Exist
                if name[0]==new_tbl:
                    if Language.get()=="Spanish":title,msg='<Tabla existe>','Tabla '+tbl_name+' ¡Ya existe!\nCancelando Crear nueva Tabla!'
                    else:title,msg="<Table Exist>",'Table ' + tbl_name+ ' Already Exist!\nCancelling Create New Table!'
                    messagebox.showerror(title, msg)
                    return
            if Language.get()=="Spanish":
                title=tbl_name+" Número de Columnas"
                msg1="Ingrese el Número de Columnas para la Nueva Tabla '"+tbl_name+"'.\n"
                msg2='Nota: La columna ID se incluye automáticamente.'
            else:    
                title=tbl_name+" Number Of Columns"
                msg1="Enter The Number Of Columns For New Table '"+tbl_name+"'.\n"
                msg2="Note: The ID Column Is Included Automatically."
            msg=msg1+msg2
            num_colms=my_askinteger(title, msg, 5, 2, 100)# Initial Value. Min Value, Max Value
            if num_colms!=None:num_colms+=1# Add ID Column
            else:return
            for c in range(num_colms):
                if c==0:    
                    colm_names.append("ID")
                    colm_data.append(1)
                else:    
                    if Language.get()=="Spanish":
                        txt="Nombre de Encabezado "+str(c)
                        entry_txt="Datos "+ str(c) 
                    else:
                        txt="Heading Name "+str(c)
                        entry_txt="Data "+str(c)
                    colm_names.append(txt)
                    colm_data.append(entry_txt)
        else:
            colm_names,colm_defs=self.get_table_schema()
            colm_data=self.get_row_values("1")
            num_colms=len(colm_names)
            for c in range(num_colms):
                colm_names[c]=colm_names[c].replace("_"," ")
            new_tbl=Active_Table.get()
        for c in range(num_colms):
            if c==0:colm_widths.append(5)
            else:colm_widths.append(25)
        try:
            self.create_edit_view()
            self.Header_Widgets=[]
            self.Column_Headers=[]# StringVars
            for c, columns in enumerate(colm_names):# Default Names
                row=0
                name_var=tk.StringVar()
                self.Column_Headers.append(name_var)
                if c==0:self.Column_Headers[c].set("ID")
                else:self.Column_Headers[c].set(colm_names[c])
                self.Header_Widgets.append(c)
                self.Header_Widgets[c]=Entry(self.Edit_View,font=my_font,textvariable=self.Column_Headers[c],
                    width=colm_widths[c],highlightthickness=1,bg="#bfffff", fg='#000000',justify='center',relief='flat') 
                self.Header_Widgets[c].delete(0,END)
                self.Header_Widgets[c].insert(0,columns)
                self.Header_Widgets[c]['validatecommand']=(self.Header_Widgets[c].register(self.validate_entries),'%P','%d')
                val_cmd=(self.Header_Widgets[c].register(self.on_validate_entries), '%P')
                self.Header_Widgets[c].config(validate="key", validatecommand=val_cmd)
                self.Header_Widgets[c].configure(highlightbackground='#000000', highlightcolor='#000000')
                self.Edit_Widgets[len(self.Edit_Widgets)+1]=self.Header_Widgets[c]
                self.Header_Widgets[c].grid(row=row, column=c, columnspan=1)
                if Edit_Definitions.get()==True:self.Header_Widgets[c].config(state='disabled')
                if c==0:self.Header_Widgets[c].config(state= "disabled")
                else:
                    self.Header_Widgets[c].config(state= "normal")
                    self.Header_Widgets[c].bind("<Button-3>", self.get_header_index_clicked)
                    self.header_menu = tk.Menu(self.Header_Widgets[c], tearoff=False)
                    self.header_menu.add_command(label="Paste", command=lambda: self.clipboard_to_header(self.Header_Widgets[c]))
            root.update()
        except Exception as ex:
            if Language.get()=="Spanish":title,msg1="< Crear Nueva Tabla >","¡Crear Nueva Tabla Falló!\n"
            else:title,msg1='< Create New Table >','Create New Table Failed!\n'
            msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
            return
        try:
            if Language.get()=="Spanish":
                def_zero="Tipo de Dato"
            else:def_zero="Data Type"    
            definitions=[def_zero,"INTEGER","INTEGER NOT NULL","NUMERIC","NUMERIC NOT NULL",
                         "REAL","REAL NOT NULL","TEXT","TEXT NOT NULL"]
            define_cbo=[]
            self.Row_Widgets=[]
            self.Column_Data=[]
            column_defines=[]
            for c in range(len(colm_names)):
                row=1
                txt_var=tk.StringVar()
                self.Column_Data.append(txt_var)
                self.Row_Widgets.append(c)
                self.Row_Widgets[c]=Entry(self.Edit_View,textvariable=self.Column_Data[c],bg= '#c8ffff',fg='#000000', 
                    font=my_font,width=colm_widths[c],highlightthickness=1,justify='center',relief='sunken')
                self.Row_Widgets[c].configure(highlightbackground='red', highlightcolor='red')
                self.Row_Widgets[c].grid(row=row, column=c, columnspan=1)
                if c==0:
                    self.Column_Data[c].set("")
                    self.Row_Widgets[c].config(state= "disabled")
                elif c>0:    
                    self.Column_Data[c].set(colm_data[c])
                    self.Row_Widgets[c].bind("<Button-3>", self.get_row_index_clicked)
                    self.row_menu = tk.Menu(self.Row_Widgets[c], tearoff=False)
                    self.row_menu.add_command(label="Paste", command=lambda: self.clipboard_to_row(self.Row_Widgets[c]))
                self.Edit_Widgets[len(self.Edit_Widgets)+1]=self.Row_Widgets[c]
                row=2# Column Definitions 
                define_var=tk.StringVar()
                column_defines.append(define_var)
                define_cbo.append(c)
                if c==0:column_defines[c].set("ID INTEGER PRIMARY KEY AUTOINCREMENT, ")
                else:
                    define_cbo[c]=ttk.Combobox(self.Edit_View,textvariable=column_defines[c],
                                                state = "readonly",justify="center",font=my_font)
                    define_cbo[c]['values']=definitions
                    if Edit_Definitions.get()==False:define_cbo[c].current(0)
                    else:define_cbo[c].set(colm_defs[c])
                    define_cbo[c].grid(row=row, pady=(5,0),column=c, columnspan=1)
                    self.Edit_Widgets[len(self.Edit_Widgets)+1]=define_cbo[c]
            root.update()        
            row=4
            row_space1=Label(self.Edit_View,text="",font=my_font,fg="#000000",
                       bg= "#e7e7e7",anchor="w",justify='left')
            row_space1.grid_rowconfigure(row, minsize=100)
            row_space1.grid(row=row, column=2, columnspan=num_colms,sticky=SW)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=row_space1
            if Edit_Definitions.get()==False:
                if Language.get()=="Spanish":title="Usted está aquí → Base de Datos "+DB_Name.get()+ " → Crear Nueva Tabla → "+new_tbl
                else:title=str("You Are Here → Database: "+DB_Name.get()+" → Create New Table → "+new_tbl) 
                root.title(title)
                config_menu(None)
                root.update()
                if Language.get()=="Spanish":
                    msg1="¡Los encabezados y los primeros campos de entrada deben estar presentes para\n" 
                    msg2="crear una nueva tabla! Reemplace los nombres de los encabezados y los campos\n" 
                    msg3="de datos arriba con sus datos. Asegúrese de seleccionar el tipo de datos para\n" 
                    msg4="cada columna. Cuando haya terminado, haga clic en Guardar o Cancelar tabla."
                    msg=msg1+msg2+msg3+msg4
                elif Language.get()=="English":
                    msg1="The Headings And First Entry Fields Must Be Present To\n"
                    msg2="Create A New Table! Replace The Heading Names And Data\n"
                    msg3="Fields Above With Your Data. Make Sure To Select The Data Type\n"
                    msg4="For Each Column. When Finished, Click Save Or Cancel Table."
                    msg=msg1+msg2+msg3+msg4
            else:
                if Language.get()=="Spanish":title="Usted está aquí → Base de Datos "+DB_Name.get()+ " → Editar Definiciones de Columna → "+new_tbl
                else:title=str("You Are Here → Database: "+DB_Name.get()+" → Edit Column Definitions → "+new_tbl) 
                root.title(title)
                config_menu(None)
                root.update()
                if Language.get()=="Spanish":
                    msg1="Cambie las Definiciones de Entrada como desee, luego presione Guardar para \n"
                    msg2="continuar o Cancelar. Nota: Se Muestran las Definiciones de las Columnas Actuales."
                elif Language.get()=="English":
                    msg1="Change The Entry Definitions As Desired, Then Press Save To \n"
                    msg2="Continue Or Cancel. Note: Present Column Definitions Are Shown."
                msg=msg1+msg2  
            row=7
            lbl1=Label(self.Edit_View,text=msg,font=my_font,fg="#000000",
                       bg="#e7e7e7",anchor="w",justify='left')
            lbl1.grid_rowconfigure(row, minsize=100)
            lbl1.grid(row=row, column=2, columnspan=num_colms,sticky=SW)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=lbl1
            row=8
            root.update()
            row_space2=Label(self.Edit_View,text="",font=my_font,fg="#000000",
                       bg="#e7e7e7",anchor="w",justify='left')
            row_space2.grid_rowconfigure(row, minsize=100)
            row_space2.grid(row=row, column=2, columnspan=num_colms,sticky=SW)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=row_space2
            if Language.get()=="Spanish":txt='Cancelar'
            else:txt="Cancel"
            row=12    
            cancel=Button(self.Edit_View, text=txt,font=my_font,fg='#000000',bg='#dcdcdc',
                    command=lambda:self.cancel_edit_view("Cancel Table"))
            cancel.grid_rowconfigure(row, minsize=10)
            cancel.grid(row=row, column=2, padx=(0,5), columnspan=1,sticky=SE)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=cancel
            if Language.get()=="Spanish":txt="Guardar"
            else:txt="Save"    
            save=Button(self.Edit_View, text=txt,font=my_font,fg='#000000', bg='#dcdcdc',
                command=lambda:self.save_new_table(db_type,new_tbl, self.Column_Headers, self.Column_Data, column_defines))
            save.grid_rowconfigure(row, minsize=10)
            save.grid(row=row, column=3, padx=(0,5), columnspan=1,sticky=SE)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=save
            self.grid_edit_view(12)
            disable_menubar("all")
        except Exception as ex:
            if Language.get()=="Spanish":title,msg1,msg2="<Crear Nueva Tabla>","¡Crear Nueva Tabla Falló!\n",f"Error: '{ex}'"
            else:title,msg1,msg2='<Create New Table>','Create New Table Failed!\n',f"Error: '{ex}'" 
            msg=msg1+msg2
            messagebox.showerror(title, msg)
            enable_menubar("all")
            config_menu(None)
    def delete_selected_tbl(self,tbl):
        try:
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            conn.execute("DROP TABLE "+tbl)
            tbl_menu.delete(0, END)
            tbls=self.fetch_tables()
            if Language.get()=="English":
                txt1='Create New Table'
                txt2='Tables'
            else:
                txt1='Crear Nueva Tabla'
                txt2='Tablas'
            tbl_menu.add_command(label=txt1,command=self.create_new_table)
            tbl_menu.add_separator()
            arrow_label=str('↓ '+txt2+' ↓')
            tbl_menu.add_command(label=arrow_label)
            tbl_menu.entryconfig(arrow_label, state="disabled")
            tbl_menu.add_separator()
            for name in tbls:
                if name[0]!="sqlite_sequence":
                    tbl_menu.add_command(label=name[0],command=lambda a=name[0]:self.select_table(a))
                    tbl_menu.add_separator()
            conn.commit()
            if tbl==Active_Table.get():
                self.clear_data_view()
                Active_Table.set("")
            if Language.get()=="Spanish":
                msg='¡Tabla '+tbl+' eliminada con éxito!'
                title1='<Eliminar tabla> '+tbl
                title2='Estás Aquí → '+DB_Name.get()+' de Base de Datos → '+'Eliminar tabla '+tbl
            else:
                msg=tbl+' Table Deleted Successfully!'
                title1='<Delete Table> '+tbl
                title2="You Are Here → Database: "+DB_Name.get()+" → Delete Table "+tbl    
            messagebox.showinfo(title1, msg)
            root.title(title2)
            root.update()
            config_menu(None)
        except sqlcipher.DatabaseError as e:
            if Language.get()=="Spanish":title,msg1='<Eliminar tabla seleccionada> '+tbl,'Error de eliminación de la Tabla '+tbl+'\n'
            else:title,msg1='<Delete Selected Table> '+tbl,'Error Deleting Table '+tbl+'\n'
            msg2=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
    def delete_table(self):
        try:# Retrieve The Tables And Populate Combobox With Choices
            num_tbls=self.get_num_tbls()
            if num_tbls==0:return
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            cursor=conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables=[]
            for name in sorted(cursor.fetchall()):
                if name[0]!="sqlite_sequence":tables.append(name[0])
            conn.commit()    
            if len(tables)==0:
                return
        except sqlcipher.DatabaseError as e:
            if Language.get()=="Spanish":
                title='<Eliminar tabla>'
                msg1='¡No se pudo recuperar los nombres de las Tabla!'
            else:
                title="<Delete Table>"
                msg1="Failed to retrieve Table Names!\n"    
            msg2=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
        if Language.get()=="Spanish":
            title='Estás Aquí → '+DB_Name.get()+' de Base de Datos → Eliminar tabla → '
            msg='Seleccione la Tabla que desea Eliminar, luego haga clic en OK.'
        else:
            title="You Are Here → Database: "+DB_Name.get()+" → Delete Table →"
            msg='Select The Table You Wish To Delete, Then Click OK.'    
        selected=my_askstring(title, msg, tables)
        if selected=="" or selected==None:return
        else: self.delete_selected_tbl(selected)
        if selected==Active_Table.get():
            Active_Table.set("")
    def rename_table(self):
        if Active_Table.get()=="":
            if Language.get()=="Spanish":
                title='<'+DB_Name.get()+' / sin tabla seleccionada>'
                msg1='Se debe seleccionar una tabla para continuar.'
                msg2='¡Seleccione una tabla y vuelva a intentarlo!'
            else:    
                title="<"+DB_Name.get()+" / No Table Selected>"
                msg1='A Table Must Be Selected To Continue.\n'
                msg2='Please Select A Table And Try Again!'
            messagebox.showerror(title, msg1+msg2)
            return
        else:
            old_name=Active_Table.get().replace("_"," ")
            if Language.get()=="Spanish":
                title='Estás aquí → '+DB_Name.get()+' de Base de Datos → Cambiar el Nombre de la Tabla → '+old_name
                ask_title='<Cambiar la Tabla '+old_name+'>'
                ask_prompt="Introduzca un Nuevo Nombre para "+old_name+"."
            else:
                title="You Are Here → Database: "+DB_Name.get()+" → Rename Table → "+old_name
                ask_title="<Rename Table "+ old_name+">"
                ask_prompt="Enter A New Name For "+old_name+"."
            root.title(title)
            root.update()
            new_name=my_askstring(ask_title, ask_prompt)
            if new_name=="" or new_name==None:return
        try:
            new_name=new_name.replace(" ","_")    
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            cursor = conn.execute("SELECT * FROM sqlite_master")
            tables=cursor.fetchall()
            if len(tables)!=0:
                cursor.execute("ALTER TABLE "+ Active_Table.get()+ " RENAME TO " + new_name)# Rename Table In Database
                conn.commit()
            else:
                return
            if DB_Name.get()!="" and Active_Table.get()!="":  
                Active_Table.set(new_name)
                self.select_database(DB_Path.get(),DB_Name.get()+".db3")                
                self.select_table(new_name)# Populate Table With New Entry
            if Language.get()=="Spanish":
                title='<Renombrar Tabla> '+Active_Table.get()
                msg='Cambiar el Nombre a '+Active_Table.get()+' Exitoso'
            else:
                title='<Rename Table> '+Active_Table.get()
                msg="Rename To "+Active_Table.get()+' Successful'
            messagebox.showinfo(title, msg)
        except sqlcipher.DatabaseError as e:
            if Language.get()=="Spanish":
                title='<Renombrar Tabla> '+Active_Table.get()
                msg1='No se pudo cambiar el Nombre de '+Active_Table.get()
            else:
                title='<Rename Table> '+Active_Table.get()
                msg1="Failed To Rename "+Active_Table.get()+'\n'    
            msg2=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
    def is_encrypted(self,database_path):
        try:
            # Connect to the database without providing a key
            conn = sqlcipher.connect(database_path)
            cursor = conn.cursor()
            # Attempt to execute a simple query
            cursor.execute("SELECT count(*) FROM sqlite_master;")
            cursor.fetchone()
            # If the query succeeds, the database is not encrypted
            conn.close()
            return False
        except sqlcipher.DatabaseError as e:
            # If an error occurs, it might be encrypted
            if "file is not a database" in str(e).lower():
                return True
            else:
                raise e  # Raise other unexpected errors
    def fetch_tables(self):
        try:
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables=sorted(cursor.fetchall())
            conn.close()
            return tables
        except sqlcipher.DatabaseError as e:
            if Language.get()=="Spanish":
                title='<Tablas de busca>'
                msg1='No se pudo recuperar tablas de '+DB_Name.get()+'\n'
                msg3="¡O Clave de Encriptación Incorrecta Ingresada!"
            else:
                title='<Fetch Tables>'
                msg1="Failed To Retrieve "+DB_Name.get()+" Tables\n"  
            msg2=f"Error: '{e}'\n"
            msg3="Or Incorrect Encryption Key Entered!"
            messagebox.showerror(title, msg1+msg2+msg3)
        finally:
            if conn:conn.close()
    def delete_selected_entry(self,entry):
        if Language.get()=='Spanish':
            title="Eliminar Entrada Seleccionada"
            msg1='¿Estás seguro de que quieres Eliminar esta Entrada?\n'
            msg2='Haga Clic en Sí para Continuar o No para Salir.'
        else:    
            title="< Delete Selected Entry >"
            msg1='Are You Sure You Want To Delete This Entry?\n'
            msg2="Click Yes To Continue Or No To Exit!"
            response=messagebox.askyesno(title, msg1+msg2)
            if not response:return
        try:
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            conn.execute(f"DELETE FROM {Active_Table.get()} WHERE id={entry[0]}")
            conn.commit()
            self.select_table(Active_Table.get())# Populate Table With New Entry
            if Language.get()=="Spanish":
                title=f"< Eliminar {Active_Table.get()}, ID = {entry[0]} >"
                msg=f"Entrada de Tabla {Active_Table.get()} ID = {entry[0]} Eliminado Correctamente!"
            else:    
                title=f"< Delete {Active_Table.get()}, ID = {entry[0]} >"
                msg=f"Table Entry {Active_Table.get()}, ID = {entry[0]} Deleted Successfully!"
            messagebox.showinfo(title, msg)
        except sqlcipher.DatabaseError as e:
            if Language.get()=="Spanish":
                title="< Deleccionar Entrada Seleccionada >"
                msg1=f"No se pudo Eliminar el {DB_Name.get()} ID = {entry[0]}\n"
            else:    
                title="< Delect Selected Entry >"
                msg1=f"Failed to Delete {DB_Name.get()} ID = {entry[0]}\n"
            msg2=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
    def save_new_column(self,name,data,define,id,new_index=None):
        if Language.get()=="Spanish":
            if name=="":
                msg1="¡Nombre de la Columna No Puede Estar en Blanco!\n"
                msg2="¡Por Favor, Inténtelo de Nuevo!"
                msg=msg1+msg2
                messagebox.showerror("Falta Nombre de la Columna", msg)
                return
            if define=="Tipo de Dato":
                msg1="¡Nombre de la Columna "+name+" Tipo de Datos No Está Seleccionado!\n"
                msg2="¡Por Favor, Inténtelo de Nuevo!"
                msg=msg1+msg2
                messagebox.showerror("Tipo de Datos Faltante "+name, msg)
                return
        else:# English        
            if name=="":
                msg="Column Name Cannot Be Blank. Please Try Again!"
                messagebox.showerror("Missing Column Name "+name, msg)
                return
            if define=="Data Type":
                msg="Column Name "+name+" Data Type Is Not Selected. Please Try Again!"
                messagebox.showerror("Missing Data Type "+name, msg)
                return
        try:
            if data=="":data="None"
            name=name.replace(" ","_")
            colm_defined=name+" "+define
            encrypted=self.is_encrypted(Active_DB.get())
            conn = sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            if new_index==None:# Column Created On End
                conn.execute(f"ALTER TABLE {Active_Table.get()}  ADD COLUMN  {colm_defined}")
                conn.commit()
                query=f"UPDATE {Active_Table.get()} SET {name} = ? Where id = ?"
                colm_data=(data, id)
                conn.execute(query, colm_data)
                conn.commit()
            else:# Column Not Created On End 
                colm_names,colm_definitions=self.get_table_schema()
                old_colm_names=colm_names.copy()
                old_num_columns=len(old_colm_names)
                colm_names.insert(new_index, name)
                colm_definitions.insert(new_index, define)
                num_columns=len(colm_names)
                defined_types=""
                names=""
                for c in range(len(old_colm_names)):
                    if c==0:names+=old_colm_names[c]+", "
                    elif c==old_num_columns-1: names+=old_colm_names[c]
                    else:names+=old_colm_names[c]+", "
                for c in range(len(colm_names)):
                    if c==0:defined_types="ID INTEGER PRIMARY KEY AUTOINCREMENT, "
                    elif c==num_columns-1:defined_types+=colm_names[c]+" "+colm_definitions[c]
                    else:defined_types+=colm_names[c]+" "+colm_definitions[c]+", "
                tbl_name="temp_table"
                # Step 1: Create a new table with the desired column order
                conn.execute(f"CREATE TABLE IF NOT EXISTS {tbl_name} ({defined_types})")
                # Step 2: Copy data from the old table to the new table
                conn.execute(f"INSERT INTO  {tbl_name} ({names}) SELECT {names} FROM {Active_Table.get()}")
                # Step 3: Drop the old table
                conn.execute(f"DROP TABLE {Active_Table.get()}")
                # Step 4: Rename the new table to the old table's name
                conn.execute(f"ALTER TABLE {tbl_name} RENAME TO {Active_Table.get()}")
                conn.commit()
                # Update The New Column With Initial Data
                query="UPDATE "+Active_Table.get()+" SET "+name+" = ? Where id = ?"
                data=(data, id)
                conn.execute(query, data)
                conn.commit()
            if Language.get()=="English":messagebox.showinfo("New Table Column", "New Column Created Sucessfully.")
            else:messagebox.showinfo("Crear nueva columna", "Nueva columna creada con éxito.")
        except sqlcipher.DatabaseError as e:
            if Language.get()=="Spanish":
                title='<Agregar nueva columna>'
                msg1='Error al agregar la columna '+DB_Name.get()+' ID = '+str(id)+'\n'
            else:    
                title='<New Table Column>'
                msg1='Failed to Add Column '+DB_Name.get()+' ID = '+str(id)+'\n'
            msg2=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2)
            return
        finally:
            if conn:conn.close()
            self.create_data_view()                
            self.select_table(Active_Table.get())# Populate Table With New Entry
    def new_table_column(self):
        add_to_end=False
        colm_names,_=self.get_table_schema()
        if Language.get()=="Spanish":    
            title="Cambiar el Nombre de la Columna"
            msg1='Seleccione la Columna después de la cual se "insertará la Nueva Columna"\n'
            msg2='Haga Clic en OK para Continuar.'
        else:
            title="New Table Column"
            msg1='Select The Heading That The New Heading Will Be "Inserted After".\n'
            msg2='Click OK To Continue.'
        msg=msg1+msg2
        add_index=-1
        after_name=my_askstring(title, msg, colm_names)
        if after_name==None or after_name=="":return
        for i, column in enumerate(colm_names):
            if column==after_name:
                if i==len(colm_names)-1:
                    add_to_end=True
                    add_index=i+1
                else:add_to_end=False    
                add_index=i+1
                break
        if add_to_end:add_index=None
        if Language.get()=="Spanish":colm_name="Nombre del Encabezado"+str(add_index)
        else:colm_name="Heading Name "+str(add_index)
        self.create_edit_view()    
        row=0
        try:
            # ID Heading
            id=Entry(self.Edit_View,bg= "#e7e7e7",fg="#000000", 
                font=my_font,width=5,highlightthickness=1,justify='center',relief='sunken')
            id.configure(highlightbackground='#000000', highlightcolor='#000000')
            id.insert(0,"ID")
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=id
            id.grid(row=row, column=1, columnspan=1)
            id.config(state="disabled")
            self.Header_Widgets=[]
            self.Column_Headers=[]
            name_var=tk.StringVar()
            self.Column_Headers.append(name_var)
            self.Header_Widgets.append(0)
            # New Heading Name
            self.Header_Widgets[0]=Entry(self.Edit_View,font=my_font,textvariable=self.Column_Headers[0],
                width=30,highlightthickness=1,bg="#c8ffff", fg='#000000',justify='center',relief='flat') 
            self.Header_Widgets[0].insert(0,colm_name)
            self.Header_Widgets[0]['validatecommand']=(self.Header_Widgets[0].register(self.validate_entries),'%P','%d')
            val_cmd=(self.Header_Widgets[0].register(self.on_validate_entries), '%P')
            self.Header_Widgets[0].config(validate="key", validatecommand=val_cmd)
            self.Header_Widgets[0].configure(highlightbackground='#000000', highlightcolor='#000000')
            self.Header_Widgets[0].bind("<Button-3>", self.get_header_index_clicked)
            self.header_menu = tk.Menu(self.Header_Widgets[0], tearoff=False)
            self.header_menu.add_command(label="Paste", command=lambda: self.clipboard_to_header(self.Header_Widgets[0]))
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=self.Header_Widgets[0]
            self.Header_Widgets[0].grid(row=row, column=2, columnspan=1)
            root.update()
        except Exception as ex:
            if Language.get()=="Spanish":
                title="< Agregar Nueva Columna >"
                msg1=Active_Table.get()+" ¡Crear Nueva Tabla Falló!\n"
                msg2=f"Error: '{ex}'"
            else:
                title='< New Table Column >'    
                msg1=Active_Table.get()+' Create New Table Failed!\n'
                msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
            Active_Table.set("")
            return
        try:
            if Language.get()=="Spanish":
                cancel_txt="Cancelar"
                save_txt="Save"
                definitions=["Tipo de Dato","INTEGER","NUMERIC","REAL","TEXT"]
                entry_txt="Entrada "+str(add_index)
                title="Usted está aquí → Base de Datos: "+DB_Name.get()+" → Tabla: "+Active_Table.get()+" → Agregar Nueva Columna"
            else:
                cancel_txt="Cancel"    
                save_txt="Save"
                definitions=["Data Type","INTEGER","NUMERIC","REAL","TEXT"]
                entry_txt="Entry "+str(add_index)
                title=str("You Are Here → Database: "+DB_Name.get()+" → Table: "+Active_Table.get()+ " → New Table Column")
            row=1
            # 1st ID
            encrypted=self.is_encrypted(Active_DB.get())
            conn = sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            cursor=conn.execute(f"SELECT id FROM {Active_Table.get()} ORDER BY id ASC LIMIT 1")
            first_id = cursor.fetchone()
            conn.close()
            id_entry=Entry(self.Edit_View,bg='#dddddd',fg="#000000", 
                font=my_font,width=5,highlightthickness=1,justify='center',relief='sunken')
            id_entry.configure(highlightbackground='#000000', highlightcolor='#000000')
            id_entry.insert(0,str(first_id[0]))
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=id_entry
            id_entry.grid(row=row, column=1, columnspan=1)
            id_entry.config(state="disabled")
            # New Column Data
            self.Row_Widgets=[]
            self.Column_Data=[]# StringVars
            name_var=tk.StringVar()
            self.Column_Data.append(name_var)
            self.Row_Widgets.append(0)
            self.Row_Widgets[0]=Entry(self.Edit_View,textvariable=self.Column_Data[0],bg='#c8ffff',fg='#000000', 
                font=my_font,width=30,highlightthickness=1,justify='center',relief='sunken')
            self.Row_Widgets[0].configure(highlightbackground='#000000', highlightcolor='#000000')
            self.Row_Widgets[0].insert(0,entry_txt)
            self.Row_Widgets[0].bind("<Button-3>", self.get_row_index_clicked)
            self.row_menu = tk.Menu(self.Row_Widgets[0], tearoff=False)
            self.row_menu.add_command(label="Paste", command=lambda: self.clipboard_to_row(self.Row_Widgets[0]))
            self.Row_Widgets[0].grid(row=row, column=2, columnspan=1)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=self.Row_Widgets[0]
            # New Column Definition    
            row=2
            define_var=tk.StringVar()
            defined=ttk.Combobox(self.Edit_View,textvariable=define_var,state = "readonly",justify="center",font=my_font, background="#c8ffff")
            defined['values']=definitions
            if Language.get()=="English":defined.set("Data Type")
            else:defined.set("Tipo de Dato")
            defined.grid(row=row, pady=(5,0),column=2, columnspan=1)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=defined
            row=3
            row_space=Label(self.Edit_View,text="",font=my_font,fg="#000000",
                    bg= '#dddddd',anchor="w",justify='left')
            row_space.grid_rowconfigure(row, minsize=100)
            row_space.grid(row=row, column=2, columnspan=5,sticky=SW)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=row_space
            row=4
            row_space1=Label(self.Edit_View,text="",font=my_font,fg="#000000",
                       bg= '#dddddd',anchor="w",justify='left')
            row_space1.grid_rowconfigure(row, minsize=100)
            row_space1.grid(row=row, column=1, columnspan=5,sticky=SW)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=row_space1
            root.title(title)
            config_menu(None)
            row=4
            if Language.get()=="Spanish":
                msg1= "Rellene el Encabezado de la Columna y\n"
                msg2= "Campo de Entrada con su Información.\n"
                msg3= "Cuando Termine, Seleccione Guardar o Cancelar."
            else:        
                msg1= "Fill In The Column Heading And\n"
                msg2= "Entry Field With Your Information.\n"
                msg3= "When Finished, Select Save Or Cancel."
            msg=msg1+msg2+msg3
            lbl1=Label(self.Edit_View,text=msg,font=my_font,fg="#000000",
                       bg="#e7e7e7",anchor="w",justify='left')
            lbl1.grid_rowconfigure(row, minsize=100)
            lbl1.grid(row=row, column=2, columnspan=3,sticky=SW)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=lbl1
            row=8
            row_space2=Label(self.Edit_View,text="",font=my_font,fg="#000000",
                       bg= '#dddddd',anchor="w",justify='left')
            row_space2.grid_rowconfigure(row, minsize=100)
            row_space2.grid(row=row, column=1, columnspan=5,sticky=SW)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=row_space2
            row=9
            cancel=Button(self.Edit_View, text=cancel_txt,font=my_font,fg='#000000',bg='#dcdcdc',
                    command=lambda:self.cancel_edit_view("Cancel Table"))
            cancel.grid_rowconfigure(row, minsize=100)
            cancel.grid(row=row, column=2, padx=(40,0), columnspan=1,sticky=SW)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=cancel
            save=Button(self.Edit_View, text=save_txt,font=my_font,fg='#000000', bg='#dcdcdc',
                    command=lambda:self.save_new_column(self.Column_Headers[0].get(),self.Column_Data[0].get(),define_var.get(),first_id[0],add_index))
            save.grid_rowconfigure(row, minsize=100)
            save.grid(row=row, column=2, padx=(0,40), columnspan=1,sticky=SE)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=save
            disable_menubar("all")
            self.grid_edit_view(row)    
            root.update()
        except sqlcipher.DatabaseError as e:
            if Language.get()=="Spanish":
                title="< Agregar Nueva Columna >"
                msg1=Active_Table.get()+" ¡Crear Nueva Columna Falló!\n"
                msg2=f"Error: '{e}'"
            else:
                title='< New Table Column >'    
                msg1=Active_Table.get()+' New Table Column Failed!\n'
                msg2=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2)
            self.destroy_edit_view()
            enable_menubar("all")
            config_menu(None)
        finally:
            if conn:conn.close()
    def drop_column(self,header):
        header=header.replace('_', ' ')
        if Language.get()=="Spanish":    
            title="< Eliminar Columna >"
            msg='¿Está Seguro de que desea Eliminar el Columna "{header}"?'
        else:
            title="< Delete Table Column >"
            msg=f'Are You Sure You Want To Delete Column "{header}"? '
        response=messagebox.askyesno(title, msg)
        if not response:return
        header=header.replace(" ","_")
        try:
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            conn.execute("ALTER TABLE "+Active_Table.get()+" DROP COLUMN "+header)
            conn.commit()
        except sqlcipher.DatabaseError as e:
            if Language.get()=="Spanish":
                title='< Eliminar Columna >'
                msg1='¡Error en la Eliminación de Columnas!'
            else:    
                title='< Delete Table Column >'
                msg1='Delete Table Column Failed!\n'
            msg2=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
            self.select_table(Active_Table.get())# Populate Table With New Entry
            if Language.get()=="English":messagebox.showinfo("Delete Table Column", f"Column {header} Deletion Sucessfully.")
            else:messagebox.showinfo("Eliminar Columna", "Eliminación de Columna {header} con éxito.")
    def rename_column(self,header):
        if header!=None:old_name=header.replace(" ","_")
        if Language.get()=="Spanish":    
            title=f'< Cambiar el Nombre de la Columna de la Tabla "{header}" >'
            msg1=f'Introduzca un Nuevo Nombre para "{header}". A Continuación\n' 
            msg2='Haga Clic en Aceptar para Continuar o Cancelar para Salir.'
        else:
            title=f'< Rename Table Column "{header}" >'
            msg1=f'Enter A New Name For "{header}". Then\n'
            msg2='Click OK To Continue Or Cancel To Exit.'
        msg=msg1+msg2
        new_name=my_askstring(title, msg, header)
        if new_name==None or new_name=="":return
        new_name=new_name.replace(" ","_")
        try:
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            conn.execute(f"ALTER TABLE {Active_Table.get()} RENAME COLUMN {old_name} TO {new_name}")
            conn.commit()
            self.select_table(Active_Table.get())# Populate Table With New Entry
            if Language.get()=="Spanish":
                messagebox.showinfo(f'Cambiar el Nombre de la Columna "{header}"', "¡El cambio de Nombre de Columna se ha realizado correctamente!")
            else:
                messagebox.showinfo(f'Rename Table Column "{header}"', "Column Heading Renamed Successful!")
        except sqlcipher.DatabaseError as e:
            if Language.get()=="Spanish":
                title='< Cambiar el Nombre de la Columna >'
                msg1='¡Error al cambiar el nombre de la columna!'
            else:    
                title='< Rename Table Column >'
                msg1='Rename Table Column Failed!\n'
            msg2=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
    def insert_into_table(self,tbl_name, headings, new_data):
        if tbl_name=="":
            if Language.get()=="Spanish":
                title=f"< {DB_Name.get()} / sin Tabla Seleccionada >"
                msg1='Se debe Seleccionar una Tabla para Continuar.'
                msg2='¡Seleccione una Tabla y vuelva a intentarlo!'
            else:    
                title=f"< {DB_Name.get()} / No Table Selected >"
                msg1='A Table Must Be Selected To Continue.\n'
                msg2='Please Select A Table And Try Again!'
            messagebox.showerror(title, msg1+msg2)
            return
        tbl_name=tbl_name.replace(' ','_')
        if new_data[1].get()=="" and new_data[2].get()=="":
            if Language.get()=="Spanish":
                title=f"< Insertar en la Tabla {tbl_name} >"
                msg1='Columna 1 y Columna 2\n'
                msg2='¡Debe completarse para continuar!\n'
                msg3='¡Complete los campos faltantes!'
            else:    
                title=f"< Insert Into {tbl_name} Table >"
                msg1='Column 1 and Column 2\n'
                msg2='Must Be Filled Out To Continue!\n'
                msg3='Please Fill Out The Missing Fields!'
            messagebox.showerror(title, msg1+msg2+msg3)
            return
        header=[]
        data=[]
        num_columns=len(headings)
        try:
            for c in range(1,len(headings)):
                name=str(headings[c]).replace(" ","_") 
                header.append(name)
            data=[]
            for d in range(1,len(headings)):
                if new_data[d].get()=="":new_data[d].set("None")
                data.append(new_data[d].get())
                names=""
                values=""
                for s in range(len(headings)-1):
                    if s==1:
                        names+=header[s]+", "
                        values+='?, '
                    elif s==num_columns-2:
                        names+=header[s]
                        values+='?'
                    else:    
                        values+='?, '
                        names+=header[s]+", "
                values=values.replace("'","")    
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            conn.execute(f"INSERT INTO {tbl_name} ({names}) VALUES({values})", (data))
            conn.commit()
            Active_Table.set(tbl_name)
            tbl_menu.delete(0,END)
            if Language.get()=="Spanish":
                title='< Agregar Nueva Fila >'
                msg=f"¡Nueva Fila de {tbl_name} creada con éxito!"
            else:    
                title='< New Table Row >'
                msg=f"Table {tbl_name} New Entry Created Successfully!"
            messagebox.showinfo(title, msg)
        except sqlcipher.DatabaseError as e:
            if Language.get()=="Spanish":
                title='< Agregar Nueva Fila >'
                msg1='Table = '+tbl_name+'\n'
                msg2='¡Nueva Fila de Tabla Falló!\n'
            else:    
                title='< New Table Row >'
                msg1='Table = '+tbl_name+'\n'
                msg2='New Table Row Failed!\n'
            msg3=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2+msg3)
            enable_menubar("all")
            config_menu(None)
        finally:
            if conn:conn.close()
            self.create_data_view()                
            enable_menubar("all")
            config_menu(None)
            Active_DB
            self.select_database(DB_Path.get(),DB_Name.get()+".db3")  
            self.select_table(tbl_name)
    def save_new_table(self,db_type, tbl_name, colm_names, colm_data, colm_defines):
        # Check For Missing Fields, Data Types
        if Language.get()=="Spanish":
            for c in range(1, len(colm_names)):
                if colm_names[c].get()=="":
                    msg1="¡Nombre de la Columna "+str(c)+" No Puede Estar en Blanco!\n"
                    msg2="¡Por Favor, Inténtelo de Nuevo!"
                    msg=msg1+msg2
                    messagebox.showerror("Falta Nombre de la Columna "+str(c+1), msg)
                    return
                if colm_defines[c].get()=="Tipo de Dato":
                    msg1="¡Nombre de la Columna "+str(c)+" Tipo de Datos No Está Seleccionado!\n"
                    msg2="¡Por Favor, Inténtelo de Nuevo!"
                    msg=msg1+msg2
                    messagebox.showerror("Tipo de Datos Faltante "+str(c+1), msg)
                    return
                if "NOT NULL" in colm_defines[c].get() and colm_data[c].get()=="":
                    msg1="¡Datos de Columna "+str(c)+" No puede estar en blanco!\n"
                    msg2="¡Por Favor, Inténtelo de Nuevo!"
                    msg=msg1+msg2
                    messagebox.showerror("Tipo de Datos Seleccionado "+colm_defines[c].get(), msg)
                    return
        else:# English        
            for c in range(1, len(colm_names)):
                if colm_names[c].get()=="":
                    msg="Column Name "+str(c)+" Cannot Be Blank. Please Try Again!"
                    messagebox.showerror("Missing Column Name "+str(c+1), msg)
                    return
                if colm_defines[c].get()=="Data Type":
                    msg="Column "+str(c)+" Data Type Is Not Selected. Please Try Again!"
                    messagebox.showerror("Missing Data Type "+str(c+1), msg)
                    return
                if "NOT NULL" in colm_defines[c].get() and colm_data[c].get()=="":
                    msg="Column Data "+str(c)+" Cannot Be Blank. Please Try Again!"
                    messagebox.showerror("Selected Data Type "+colm_defines[c].get(), msg)
                    return
        defined_types=""
        column_names=""
        queries=""
        null_queries=""
        header=[]
        data=[]
        num_columns=len(colm_names)
        header.append(colm_names[0].get().replace(" ","_"))# ID
        defined_types=colm_defines[0].get()# ID Definition
        for c in range(1, len(colm_names)):
            if colm_data[c].get()=="":colm_data[c].set("None") 
            data.append(colm_data[c].get())
            if colm_names[c].get()=="":colm_names[c].set("None") 
            header.append(colm_names[c].get().replace(" ","_"))#Spaces Not Allowed In Column Names
            if c==len(colm_names)-1:
                column_names+=header[c]
                queries+='?'
                null_queries+='NULL'
            else:    
                queries+='?, '
                null_queries+='NULL, '
                column_names+=header[c]+", "
            if c==num_columns-1:defined_types+=header[c]+" "+colm_defines[c].get() 
            else:defined_types+=header[c]+" "+colm_defines[c].get()+", "
        queries=queries.replace("'","")    
        null_queries=null_queries.replace("'","")    
        tbl_name=tbl_name.replace(' ','_')
        try:
            conn=sqlcipher.connect(Active_DB.get())
            if db_type=="encrypted":conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            conn.execute(f"CREATE TABLE IF NOT EXISTS {tbl_name} ({defined_types})")
            if Edit_Definitions.get()==False:
                conn.execute(f"INSERT OR REPLACE INTO {tbl_name} ({column_names}) VALUES({queries})", data)
                conn.commit()
                conn.close()
                Active_Table.set(tbl_name)
                tbl_menu.delete(0,END)
                if DB_Name.get()!="" and tbl_name!="":  
                    self.cancel_edit_view()
                    self.select_database(DB_Path.get(),DB_Name.get()+".db3")                
                    self.select_table(tbl_name)# Populate Table With New Entry
                    self.display_table()
                if Language.get()=="Spanish":
                    title='< Guardar nueva tabla >'
                    msg1='Tabla de '+DB_Name.get()+' de Base de Datos '+tbl_name+'\n'
                    msg2='¡Nueva Tabla Creada con éxito!.'
                else:    
                    title='< Save New Table >'
                    msg1='Database '+DB_Name.get()+' Table '+tbl_name+'\n'
                    msg2='New Table Created Successfully!.'
                messagebox.showinfo(title, msg1+msg2)
                enable_menubar("all")
                config_menu(None)
            else:# Edit Table Definitions
                # This Section will rename our 'original' table to old_table. 
                # Then recreate a new 'original' table with the new data types.
                # Delete Row 1 Which Is Only Used To Create New Table. Gets Reinserted Next Step.
                # Then insert all of the data from the old_table into the new 'original' table.
                # Then delete the old_table once verified ok.
                encrypted=self.is_encrypted(Active_DB.get())
                conn=sqlcipher.connect(Active_DB.get())
                conn.execute("PRAGMA foreign_keys = OFF")
                if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
                conn.execute(f"ALTER TABLE {tbl_name} RENAME TO old_table")
                conn.execute(f"CREATE TABLE IF NOT EXISTS {tbl_name} ({defined_types})")
                conn.execute(f"INSERT OR REPLACE INTO {tbl_name} ({column_names}) VALUES({queries})", data)
                conn.execute(f"DELETE FROM {tbl_name} WHERE id=1")
                conn.execute(f"INSERT OR IGNORE INTO {tbl_name} SELECT * FROM old_table")
                conn.execute("DROP TABLE old_table")
                conn.execute("PRAGMA foreign_keys = ON")
                conn.commit()
                conn.close()
                Edit_Definitions.set(False)    
                if DB_Name.get()!="" and tbl_name!="":  
                    self.create_data_view()                
                    self.select_database(DB_Path.get(),DB_Name.get()+".db3")
                    self.select_table(tbl_name)# Populate Table With New Entry
                if Language.get()=="English":
                    title='< Edit Column Definitions >'
                    msg='Editing Column Definitions Succeeded!'
                else:    
                    title='< Editar Definiciones de Columna >'
                    msg='¡La Edición de Definiciones de Columna se realizó Correctamente!'
                messagebox.showinfo(title, msg)
            return
        except sqlcipher.DatabaseError as e:
            if Language.get()=="Spanish":
                title='< Guardar Nueva Tabla >'
                msg1='Tabla = '+tbl_name+'\n'
                msg2='¡Falló la Creación o Guardado de la Nueva Tabla!'
            else:    
                title='< Save New Table >'
                msg1='Table = '+tbl_name+'\n'
                msg2='Creating or Saving New Table Failed.\n'
            msg3=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2+msg3)
            enable_menubar("all")
            config_menu(None)
        finally:
            if conn:conn.close()
    def new_table_row(self):
        if Active_Table.get()=="":
            if Language.get()=="Spanish":
                title=f"< {DB_Name.get()} / Sin Tabla Seleccionada >"
                msg1='Se debe Seleccionar una Tabla para Continuar.'
                msg2='¡Seleccione una Tabla y Vuelva a Intentarlo!'
            else:    
                title=f"< {DB_Name.get()} / No Table Selected >"
                msg1='A Table Must Be Selected To Continue.\n'
                msg2='Please Select A Table And Try Again!'
            messagebox.showerror(title, msg1+msg2)
            return
        try:
            if Language.get()=='Spanish':
                menubar.entryconfig('     Buscar/Ordenar/Modificar Tabla     ', state="disabled")
                menubar.entryconfig('     Nueva Fila/Columna de Tabla     ', state="normal")
                save_txt='Guardar'
                cancel_txt='Cancelar'
            else:    
                menubar.entryconfig('     Search/Sort/Modify Table     ', state="disabled")
                menubar.entryconfig('     New Table Row/Column     ', state="normal")
                save_txt='Save'
                cancel_txt='Cancel'
            colm_names=self.retrieve_column_names()
            num_columns=(len(colm_names))
            colms=len(colm_names)
            self.Header_Widgets=[]
            wid=[]
            row=0
            for c in range(colms):
                if c==0:wid.append(5)
                else:wid.append(25)
            self.create_edit_view()
            for c, columns in enumerate(colm_names):# Default Names
                self.Header_Widgets.append(c)
                self.Header_Widgets[c]=Entry(self.Edit_View,font=my_font,width=wid[c],
                    bg=Header_Bg_Color.get(), fg=Heading_Text_Color.get(),justify='center',relief='flat') 
                self.Header_Widgets[c].delete(0,END)
                self.Header_Widgets[c].insert(0,columns)
                self.Edit_Widgets[len(self.Edit_Widgets)+1]=self.Header_Widgets[c]
                self.Header_Widgets[c].grid(row=0, column=c, columnspan=1)
                self.Header_Widgets[c].config(state= "disabled")
            root.update()
            row+=1
            self.Column_Data=[]
            self.Row_Widgets=[]
            for c in range(len(colm_names)):
                txt_var=tk.StringVar()
                self.Column_Data.append(txt_var)
                self.Row_Widgets.append(c)
                self.Row_Widgets[c]=Entry(self.Edit_View,textvariable=self.Column_Data[c],bg= '#c8ffff',fg='#000000', 
                    font=my_font,width=wid[c],highlightthickness=1,justify='center',relief='sunken')
                self.Row_Widgets[c].configure(highlightbackground='red', highlightcolor='red')
                self.Row_Widgets[c].grid(row=row, column=c, columnspan=1)
                if c==0:
                    self.Column_Data[c].set("")
                    self.Row_Widgets[c].config(state= "disabled")
                elif c>0:    
                    self.Row_Widgets[c].bind("<Button-3>", self.get_row_index_clicked)
                    self.row_menu = tk.Menu(self.Row_Widgets[c], tearoff=False)
                    self.row_menu.add_command(label="Paste", command=lambda: self.clipboard_to_row(self.Row_Widgets[c]))
                self.Edit_Widgets[len(self.Edit_Widgets)+1]=self.Row_Widgets[c]
            root.update()
            row+=2
            row_space1=Label(self.Edit_View,text="",font=my_font,fg="#000000",
                       bg= "#e7e7e7",anchor="w",justify='left')
            row_space1.grid_rowconfigure(row, minsize=100)
            row_space1.grid(row=row, column=2, columnspan=num_columns,sticky=SW)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=row_space1
            row+=1
            row_space2=Label(self.Edit_View, text="",fg="#000000",bg= "#e7e7e7",justify='left')
            row_space2.grid_rowconfigure(row, minsize=100)
            row_space2.grid(row=row, column=0, columnspan=num_columns,sticky=SW)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=row_space2
            row+=1
            cancel=Button(self.Edit_View, text=cancel_txt,font=my_font,fg='#000000',bg='#dcdcdc',
                    command=lambda:self.cancel_edit_view())
            cancel.grid_rowconfigure(row, minsize=100)
            cancel.grid(row=row, column=2, padx=(0,5), columnspan=1,sticky=SE)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=cancel
            save=Button(self.Edit_View, text=save_txt,font=my_font,fg='#000000', bg='#dcdcdc',
                command=lambda:self.insert_into_table(Active_Table.get(),colm_names, self.Column_Data))
            save.grid_rowconfigure(row, minsize=100)
            save.grid(row=row, column=3, padx=(0,5), columnspan=1,sticky=SE)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=save
            if Language.get()=="Spanish":
                title1='Estás Aquí → '+DB_Name.get()+' de Base de Datos → Nueva Fila de Tabla → '+ Active_Table.get()
                title='< Nueva Fila de Tabla >'
                msg1='Complete los Campos de Entrada que faltan y luego\n'
                msg2='Seleccione Guardar Entrada o Cancelar Entrada.'
            else:    
                title1="You Are Here → Database: "+DB_Name.get()+" → New Table Row → "+ Active_Table.get()
                title='< New Table Row >'
                msg1='Fill In The Missing Entry Fields And Then\n'
                msg2='Select Save Entry Or Cancel Entry.'
            row+=1    
            self.grid_edit_view(row)    
            root.title(title1)
            root.update()
            messagebox.showinfo(title, msg1+msg2)
            disable_menubar("all")
            self.Row_Widgets[1].focus_force()
        except Exception as ex:
            if Language.get()=="Spanish":
                title='< Nuevas Entradas de Tabla >'
                msg1='¡Falló la Nueva Fila de la Tabla '+Active_Table.get()+'!\n'
            else:    
                title='< New Table Entries >'
                msg1=Active_Table.get()+' New Table Row Failed!\n'
            msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
            self.destroy_edit_view()
            enable_menubar("all")
            config_menu(None)
        finally:    
            enable_menubar("all")
            config_menu(None)
    def get_header_index_clicked(self,event):
        if self.Last_Row_Index!=None:self.Row_Widgets[self.Last_Row_Index].config(bg="#bfffff")
        if self.Last_Header_Index!=None:self.Header_Widgets[self.Last_Header_Index].config(bg="#bfffff")
        clicked_widget=event.widget
        self.Widget_Index=self.Header_Widgets.index(clicked_widget)
        self.Header_Widgets[self.Widget_Index].focus()
        self.Header_Widgets[self.Widget_Index].config(bg=Header_Bg_Color.get())
        self.Last_Header_Index=self.Widget_Index
        self.show_header_menu(event)
    def show_header_menu(self,event):
            self.header_menu.post(event.x_root, event.y_root)
    def clipboard_to_header(self,event):
        try:
            clipboard_content=pyperclip.paste()
            if clipboard_content=="":return
            clipboard_content=remove_double_quoted(clipboard_content)
            self.Header_Widgets[self.Widget_Index].config(width=len(clipboard_content))
            self.Column_Headers[self.Widget_Index].set(clipboard_content)
            self.Header_Widgets[self.Widget_Index].update()
        except tk.TclError:
            pass
    def get_row_index_clicked(self,event):
        if self.Last_Header_Index!=None:self.Header_Widgets[self.Last_Header_Index].config(bg="#bfffff")
        if self.Last_Row_Index!=None:self.Row_Widgets[self.Last_Row_Index].config(bg="#bfffff")
        clicked_widget=event.widget
        self.Widget_Index=self.Row_Widgets.index(clicked_widget)
        self.Row_Widgets[self.Widget_Index].focus()
        self.Row_Widgets[self.Widget_Index].config(bg=Even_Bg_Color.get())
        self.Last_Row_Index=self.Widget_Index
        self.show_row_menu(event)
    def show_row_menu(self,event):
            self.row_menu.post(event.x_root, event.y_root)
    def clipboard_to_row(self,event):
        try:
            clipboard_content=pyperclip.paste()
            if clipboard_content=="":return
            self.Row_Widgets[self.Widget_Index].focus_force()
            clipboard_content=remove_double_quoted(clipboard_content)
            self.Row_Widgets[self.Widget_Index].config(width=len(clipboard_content))
            self.Column_Data[self.Widget_Index].set(clipboard_content)
            self.Row_Widgets[self.Widget_Index].update()
        except tk.TclError:
            pass
    def edit_table_row(self,row_data):
        if Language.get()=='Spanish':
            save_txt='Guardar'
            cancel_txt='Cancelar'
        else:    
            save_txt='Save'
            cancel_txt='Cancel'
        try:
            colm_names=self.retrieve_column_names()
            num_columns=(len(colm_names))
            colms=len(colm_names)
            headings=[]
            wid=[]
            row=0
            for c in range(colms):
                if c==0:wid.append(5)
                else:
                    if not isinstance(row_data[c], str):value=str(row_data[c])# Convert Integer, Float To Str For Len
                    else:value=row_data[c]   
                    if len(colm_names[c])>=len(value):
                        width=len(colm_names[c])+2
                    else:width=len(value)+2    
                    wid.append(width)
            self.create_edit_view()
            for c, columns in enumerate(colm_names):# Default Names
                headings.append(c)
                headings[c]=Entry(self.Edit_View,font=my_font,width=wid[c],
                    bg=Header_Bg_Color.get(), fg=Heading_Text_Color.get(),justify='center',relief='flat') 
                headings[c].delete(0,END)
                headings[c].insert(0,columns)
                self.Edit_Widgets[len(self.Edit_Widgets)+1]=headings[c]
                headings[c].grid(row=row, column=c, columnspan=1)
                headings[c].config(state= "disabled")
            root.update()
            row+=1
            self.Column_Data=[]
            self.Row_Widgets=[]
            for c in range(len(row_data)):
                txt_var=tk.StringVar()
                self.Column_Data.append(txt_var)
                self.Column_Data[c].set(row_data[c])
                self.Row_Widgets.append(c)
                self.Row_Widgets[c]=Entry(self.Edit_View,textvariable=self.Column_Data[c],bg= '#c8ffff',fg='#000000', 
                    font=my_font,width=wid[c],highlightthickness=1,justify='center',relief='sunken')
                self.Row_Widgets[c].configure(highlightbackground='red', highlightcolor='red')
                self.Row_Widgets[c].grid(row=row, column=c, columnspan=1)
                if c>0:
                    self.Row_Widgets[c].bind("<Button-3>", self.get_row_index_clicked)
                    self.row_menu = tk.Menu(self.Row_Widgets[c], tearoff=False)
                    self.row_menu.add_command(label="Paste", command=lambda: self.clipboard_to_row(self.Row_Widgets[c]))
                if c==0:self.Row_Widgets[c].config(state= "disabled")
                self.Edit_Widgets[len(self.Edit_Widgets)+1]=self.Row_Widgets[c]
            root.update()
            row+=2
            row_space1=Label(self.Edit_View,text="",font=my_font,fg="#000000",
                       bg= "#e7e7e7",anchor="w",justify='left')
            row_space1.grid_rowconfigure(row, minsize=100)
            row_space1.grid(row=row, column=2, columnspan=num_columns,sticky=SW)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=row_space1
            row+=1
            row_space2=Label(self.Edit_View, text="",fg="#000000",bg= "#e7e7e7",justify='left')
            row_space2.grid_rowconfigure(row, minsize=100)
            row_space2.grid(row=row, column=0, columnspan=num_columns, sticky=SW)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=row_space2
            row+=1
            cancel=Button(self.Edit_View, text=cancel_txt,font=my_font,fg='#000000',bg='#dcdcdc',
                    command=lambda:self.cancel_edit_view())
            cancel.grid_rowconfigure(row, minsize=100)
            cancel.grid(row=row, column=2, padx=(0,5), columnspan=1,sticky=SE)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=cancel
            save=Button(self.Edit_View, text=save_txt,font=my_font,fg='#000000', bg='#dcdcdc',
                command=lambda:self.save_edited_entry(self.Column_Data))
            save.grid_rowconfigure(row, minsize=100)
            save.grid(row=row, column=3, padx=(0,5), columnspan=1,sticky=SE)
            self.Edit_Widgets[len(self.Edit_Widgets)+1]=save
            if Language.get()=="Spanish":
                title1='Estás Aquí → '+DB_Name.get()+' de Base de Datos → Nueva Fila de Tabla → '+ Active_Table.get()
                title='< Editar Entrada de Tabla >'
                msg1='Edite los Campos de Entrada deseados y luego\n'
                msg2='Seleccione Guardar o Cancelar.'
            else:    
                title1="You Are Here → Database "+DB_Name.get()+" → Edit Table Entry → "+ Active_Table.get()
                title='< Edit Table Entry >'
                msg1='Edit The Desired Entry Fields And Then\n'
                msg2='Select Save Or Cancel .'
            row+=1
            self.grid_edit_view(row)    
            root.title(title1)
            messagebox.showinfo(title, msg1+msg2)
            disable_menubar("all")
            self.Row_Widgets[1].focus_force()
            root.update()
        except Exception as e:
            if Language.get()=='Spanish':
                title='< Editar Entrada de la Tabla >'
                msg1='Tabla = '+Active_Table.get()+'\n'
                msg2='¡Obtenga la ID de Entrada de la Tabla = '+id+' Falló!\n'
            else:    
                title='< Edit Table Entry >'
                msg1='Table = '+Active_Table.get()+'\n'
                msg2='Get Table Entry ID = '+id+' Failed!\n'
            msg3=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2+msg3)
            enable_menubar("all")
            config_menu(None)
    def save_edited_entry(self,new_data):
        if Active_Table.get()=="":
            if Language.get()=='Spanish':
                title='< '+DB_Name.get()+' / sin Tabla Seleccionada >'
                msg1='Se debe Seleccionar una Tabla para Continuar.'
                msg2='¡Seleccione una Tabla y Vuelva a Intentarlo!'
            else:    
                title="< "+DB_Name.get()+" / No Table Selected >"
                msg1='A Table Must Be Selected To Continue.\n'
                msg2='Please Select A Table And Try Again!'
                messagebox.showerror(title, msg1+msg2)
                return
        try:
            colm_names=self.get_main_columns()
            names=[]
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            for c in range(len(colm_names)):
                names.append(colm_names[c].replace(" ","_"))
                if c>=1:
                    query=f"UPDATE {Active_Table.get()} SET {names[c]} = ? Where id = ?"
                    data=(new_data[c].get(), new_data[0].get())
                    new_val=remove_double_quoted(data[0])
                    new_data[c].set(new_val)
                    data=(new_data[c].get(), new_data[0].get())
                    conn.execute(query, data)
            conn.commit()
            if Language.get()=='Spanish':
                title='< Guardar Entrada Editada >'
                msg='¡Cambios de Entrada Editados Guardados!'
            else:    
                title='< Save Edited Entry >'
                msg="Edited Entry Changes Saved!"
            messagebox.showinfo(title, msg)
            enable_menubar("all")
            config_menu(None)
        except sqlcipher.DatabaseError as e:
            if Language.get()=='Spanish':
                title='< Guardar Entrada Eeditada >'
                msg1='Tabla = '+Active_Table.get()+'\n'
                msg2='¡Guardar ID de Entrada Editado = '+new_data[0].get()+' Falló!\n'
            else:    
                title='< Save Edited Entry >'
                msg1='Table = '+Active_Table.get()+'\n'
                msg2='Save Edited Entry ID = '+new_data[0].get()+' Failed!\n'
            msg3=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2+msg3)
            enable_menubar("all")
            config_menu(None)
        finally:
            if conn:conn.close()
            self.create_data_view()                
            self.select_table(Active_Table.get())# Populate Table With New Edited Entries
    def destroy_data_view(self):
        try:
            for w in range(1, len(self.Data_Widgets)+1):
                self.Data_Widgets[w].destroy()
            root.update()
            self.Data_Widgets={}# Collection Of Data View Widgets
        except Exception as e:
            pass
    def destroy_edit_view(self):
        try:
            for widget in root.winfo_children():
                widget.grid_forget()
            for w in range(1, len(self.Edit_Widgets)+1):
                self.Edit_Widgets[w].destroy()
            root.update()
            self.Edit_Widgets={}# Collection Of Edit View Widgets
            self.Column_Data=[]# Text Variables For Row_Widgets
            self.Column_Headers=[]# Text Variables For Header_Widgets
            self.Row_Widgets=[]# Data Row Widgets
            self.Header_Widgets=[]# Header Row Widgets
        except Exception as e:
            pass
    def get_num_tbls(self):
        tbls=self.fetch_tables()
        num_tbls=0
        for name in tbls:
            if name[0]!="sqlite_sequence":
                num_tbls+=1
        return num_tbls        
    def select_table(self,item):
        if Edit_Definitions.get()==True:return
        Active_Table.set(item)
        self.destroy_edit_view()
        if Language.get()=="English":title=str("You Are Here → Database: "+DB_Name.get()+" → Table: "+Active_Table.get())  
        else:title=str("Usted está aquí → Base de Datos: "+DB_Name.get()+" → Tabla: "+Active_Table.get()) 
        root.title(title)
        root.update()
        if DB_Name.get()!="" and item!="":  
            read_config()
        if Language.get()=="English":
            menubar.entryconfig('     Search/Sort/Modify Table     ', state="normal")
            menubar.entryconfig('     New Table Row/Column     ', state="normal")
        else:    
            menubar.entryconfig('     Buscar/Ordenar/Modificar Tabla     ', state="normal")
            menubar.entryconfig('     Nueva Fila/Columna de Tabla     ', state="normal")
        self.display_table()
        enable_menubar("all")
        config_menu(None)
        root.update()
    def get_main_columns(self):
        try:
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            colm_data=conn.execute(f'PRAGMA table_info({Active_Table.get()});').fetchall()
            if conn:conn.close()
            colm_names=[]
            for c in range(len(colm_data)):
                name=str(colm_data[c][1]).replace("_"," ")
                colm_names.append(name)
            if conn:conn.close()
            return colm_names
        except sqlcipher.DatabaseError as e:
            if Language.get()=='Spanish':
                title='< Recuperar Nombres de Columna >'
                msg1='No se pudo Recuperar los Nombres de la Columna '+Active_Table.get()+'\n'
            else:    
                title='< Retrieve Column Names >'
                msg1="Failed To Retrieve "+Active_Table.get()+" Column Names\n"
            msg2=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
    def clear_data_view(self):
        try:    
            self.Tree_View.heading(column="#0").__delitem__
            for col in self.Tree_View['columns']:
                self.Tree_View.heading(col, text='')
            self.Tree_View.delete(*self.Tree_View.get_children())
            self.Tree_View["columns"] = ()
            root.update()
        except Exception:
            pass
    def display_table(self):
        try:
            self.clear_data_view()
            style.configure("Treeview", fieldbackground=Window_Color.get(), font=('Arial', 10, 'bold'))# Unused Porsion            
            style.configure("Treeview.Heading", background=Header_Bg_Color.get(), foreground=Heading_Text_Color.get(), font=('Arial', 10, 'bold'))
            style.map("Treeview.Heading", background=[('active', 'aqua'),('selected', 'aqua')])
            self.Tree_View.tag_configure('oddrow', background=Odd_Bg_Color.get(), foreground=Odd_Text_Color.get(), font=('Arial', 10, 'normal'))
            self.Tree_View.tag_configure('evenrow', background=Even_Bg_Color.get(), foreground=Even_Text_Color.get(), font=('Arial', 10, 'normal'))
            self.Tree_View.column('#0', width=0, stretch=False)# Hide Tree Structure
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM {Active_Table.get()}')# Execute a query to fetch data
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]# Define columns
            self.Tree_View['columns'] = columns
            headings=[]
            for col in columns:# Set Column Headings Text into Treeview
                col_txt=col.replace("_"," ")
                self.Tree_View.heading(col, text=col_txt)
            c=0
            for row in rows:# Set Data Text into Treeview
                if c % 2 != 0:# Even Color
                    self.Tree_View.insert("", tk.END, values=row, tags = ("evenrow"))
                else:# Odd Color    
                    self.Tree_View.insert("", tk.END, values=row, tags = ("oddrow"))
                c+=1
            headings = {}
            self.Tree_View.pack(side='left', expand=True, fill='both')
            headings = {}
            for col in self.Tree_View['columns']:# Resize Column Widths To Max Size Of Text
                if col=="ID": multiplier=3
                else:multiplier=1.2
                heading_width=int(my_font.measure(col) * multiplier)
                col_txt=col.replace("_"," ")
                self.Tree_View.column(col, anchor='center', stretch=False, width=my_font.measure(self.Tree_View.heading(col)['text']))
                for row in self.Tree_View.get_children(''):
                    data_width = int(my_font.measure(self.Tree_View.set(row, col)) * 1.2)
                    headings[col] = int(self.Tree_View.column(col, width=None))
                    if data_width>=heading_width:width=data_width# Use Largest Width Heading vs Data
                    else:width=heading_width
                    self.Tree_View.column(col, width=max(self.Tree_View.column(col, 'width'), width))
            self.Tree_View.pack(side='left', expand=True, fill='both')
            root.update()
        except sqlcipher.DatabaseError as e:
            if Language.get()=='Spanish':
                title='< Completar Nombres de Columnas >'
                msg1='No se pudo Completar los Nombres de la Columnas '+Active_Table.get()+'\n'
            else:    
                title='< Populate Column Names >'
                msg1="Failed To Populate "+Active_Table.get()+" Column Names\n"
            msg2=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2)
        finally:    
            if cursor:cursor.close()
            if conn:conn.close()
    def retrieve_column_names(self):# Also Returns "Row" Which Isn't In Schema
        try:
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            colm_names=[]
            colm_data=conn.execute(f'PRAGMA table_info({Active_Table.get()});').fetchall()
            for c in range(len(colm_data)):
                name=str(colm_data[c][1]).replace("_"," ")
                colm_names.append(name)
            if conn:conn.close()
            return colm_names
        except sqlcipher.DatabaseError as e:
            if Language.get()=='Spanish':
                title='< Recuperar Nombres de Columna >'
                msg1='No se pudo Recuperar los Nombres de la Columna '+Active_Table.get()+'\n'
            else:    
                title='< Retrieve Column Names >'
                msg1="Failed To Retrieve "+Active_Table.get()+" Column Names\n"
            msg2=f"Error: '{e}'"
            messagebox.showerror(title, msg1+msg2)
        finally:    
            if conn:conn.close()
    def edit_table_definitions(self):
        Edit_Definitions.set(True)
        self.create_new_table(None,Active_Table.get())
    def get_table_schema(self):# Doesn't Return "Row" Which Isn't In Schema
        try:
            colm_names=[]
            colm_definitions=[]
            encrypted=self.is_encrypted(Active_DB.get())
            conn=sqlcipher.connect(Active_DB.get())
            if encrypted:conn.execute(f"PRAGMA key = '{Encryption_key.get()}';")
            cursor=conn.cursor()
            cursor.execute(f"PRAGMA table_info({Active_Table.get()})")
            columns=cursor.fetchall()
            for column in columns:
                colm_names.append(column[1])
                if column[3]==1:colm_definitions.append(column[2]+" NOT NULL")
                else:colm_definitions.append(column[2])
        except sqlcipher.DatabaseError as e:
            if Language.get()=="English":messagebox.showerror("<Get Table Schema>", e)
            else:messagebox.showerror("<Obtener Esquema de tabla>", e)
        finally:
            if cursor:cursor.close()
            if conn:conn.close()
        return colm_names,colm_definitions
    def change_colors(self,which):
        try:
            if which=='window_color' or which=="all":        
                if Language.get()=='Spanish':
                    title='Seleccione el Color de la Ventana Principal'
                else:    
                    title="Select Main Window Color"
                color_code=colorchooser.askcolor(title=title,initialcolor=Window_Color.get())
                if color_code[1]==None:return
                Window_Color.set(color_code[1])
                style.configure("Treeview", fieldbackground=Window_Color.get())# Unused Porsion
                root.configure(bg=Window_Color.get())
                self.Data_Frame.configure(bg=Window_Color.get())
                root.update()
            elif which=='header_bg' or which=="all":
                if which=='header_bg':
                    if Language.get()=='Spanish':
                        title='Seleccionar Encabezados Color de Fondo'
                    else:    
                        title="Select Headings Background Color"
                    color_code=colorchooser.askcolor(title=title,initialcolor=Header_Bg_Color.get())
                    if color_code[1]==None:return
                    Header_Bg_Color.set(color_code[1])
                    self.display_table()
            elif which=='header_text' or which=="all":
                if which=='header_text':
                    if Language.get()=='Spanish':
                        title='Seleccionar Encabezados Color del Texto'
                    else:    
                        title="Select Headings Text Color"
                    color_code=colorchooser.askcolor(title=title,initialcolor=Heading_Text_Color.get())
                    if color_code[1]==None:return
                    Heading_Text_Color.set(color_code[1])
                    self.display_table()
            elif which=='odd_text' or which=="all":
                if Language.get()=='Spanish':
                    title='Seleccione el Color de Texto de la Fila Impar'
                else:    
                    title="Select Odd Row Text Color"
                color_code=colorchooser.askcolor(title=title,initialcolor=Odd_Text_Color.get())
                if color_code[1]==None:return
                Odd_Text_Color.set(color_code[1])
                self.display_table()
            elif which=='odd_bg' or which=="all":
                if which=='odd_bg':
                    if Language.get()=='Spanish':
                        title='Seleccione el Color de Fondo de la Fila Impar'
                    else:    
                        title="Select Odd Row Background Color"
                    color_code=colorchooser.askcolor(title=title,initialcolor=Odd_Bg_Color.get())
                    if color_code[1]==None:return
                    Odd_Bg_Color.set(color_code[1])
                    self.display_table()
            elif which=='even_txt' or which=="all":
                if Language.get()=='Spanish':
                    title='Seleccionar el Color de Texto de la Fila Par'
                else:    
                    title="Select Even Row Text Color"
                color_code=colorchooser.askcolor(title=title,initialcolor=Even_Text_Color.get())
                if color_code[1]==None:return
                Even_Text_Color.set(color_code[1])
                self.display_table() 
                if Language.get()=='Spanish':
                    title='Seleccionar el Color de Fondo de la Fila Par'
                else:    
                    title="Select Even Row Background Color"
                color_code=colorchooser.askcolor(title=title,initialcolor=Even_Bg_Color.get())
                if color_code[1]==None:return
                Even_Bg_Color.set(color_code[1])
                self.display_table()
            write_config()  
        except Exception as ex:
            pass
def my_askinteger(title,prompt,init_val,min_val,max_val):
    d=My_IntegerDialog(title, prompt ,init_val,min_val,max_val)
    answer=d.result
    root.update_idletasks()
    return answer  
class My_IntegerDialog(tk.simpledialog._QueryInteger):
    def body(self, master):
        self.attributes("-toolwindow", True)# Remove Min/Max Buttons
        self.bind('<KP_Enter>', self.ok)
        self.bind('<Return>', self.ok)
        pt=tk.Label(master, text=self.prompt, justify="left", font=my_font)
        pad=int((pt.winfo_reqwidth()/2)/2)
        pt.grid(row=2, padx=(5,5),pady=(5,5), sticky=W+E)
        self.entry=tk.Entry(master, name="entry", justify='center', bg="#d6ffff", font=my_font)
        self.entry.grid(row=3, padx=(pad,pad), sticky=W+E)
        self.entry.bind('<Map>', self.on_map)
        if self.initialvalue is not None:
            self.entry.insert(0, self.initialvalue)
            self.entry.select_range(0, END)
        root.update_idletasks()
        return self.entry
    def on_map(self, event):
        self.entry.focus_force()    
def my_askstring(title, prompt, init_val=None):
    d=My_StringDialog(title, prompt , init_val)
    answer=d.result
    root.update_idletasks()
    return answer  
class My_StringDialog(tk.simpledialog._QueryString):
    def body(self, master):# initialvalue May Be List, String Or None
        self.clip_text=tk.StringVar()
        self.attributes("-toolwindow", True)# Remove Min/Max Buttons
        self.bind('<KP_Enter>', self.ok)
        self.bind('<Return>', self.ok)
        pt=tk.Label(master, text=self.prompt, justify="left", font=my_font)
        pad=int((pt.winfo_reqwidth()/2)/2)
        pt.grid(row=2, padx=(5,5),pady=(5,5), sticky=W+E)
        if self.initialvalue is not None:
            wid=0
            if type(self.initialvalue)==list:# List
                for item in self.initialvalue:
                    w=len(item)
                    if w>wid:wid=w
                self.entry=ttk.Combobox(master, name="entry", state = "readonly",justify="center",width=wid, font=my_font)
                self.entry['values']=self.initialvalue
                self.entry.current(0)
            else:# String
                wid=len(self.initialvalue)
                self.entry=tk.Entry(master, name="entry", textvariable=self.clip_text, justify='center', bg="#d6ffff", width=wid, font=my_font)
                self.clip_text.set(self.initialvalue)
                self.entry.bind("<Button-3>", self.show_context_menu)
                self.context_menu = tk.Menu(self.entry, tearoff=False)
                self.context_menu.add_command(label="Paste", command=lambda: self.paste_from_clipboard(self.entry))
        else:# None
            self.entry=tk.Entry(master, name="entry", justify='center', bg="#d6ffff", font=my_font)
            self.entry.insert(0, "")
            self.entry.select_range(0, END)
        self.entry.grid(row=3, padx=(pad,pad), sticky=W+E)
        self.entry.focus_force()    
        self.entry.bind('<Map>', self.on_map)
        root.update_idletasks()
        return self.entry
    def on_map(self, event):
        self.entry.focus_force()
    def show_context_menu(self,event):
            self.context_menu.post(event.x_root, event.y_root)
    def paste_from_clipboard(self,event):
            try:
                clipboard_content=pyperclip.paste()
                if clipboard_content=="":return
                clipboard_content=remove_double_quoted(clipboard_content)
                self.entry.config(width=len(clipboard_content))
                self.clip_text.set(clipboard_content)
                self.entry.update()
            except tk.TclError:
                pass
def remove_double_quoted(text_to_exam):
    double_quoted_1=text_to_exam.startswith('"') and text_to_exam.endswith('"')
    double_quoted_2=text_to_exam.startswith("'") and text_to_exam.endswith("'")
    if double_quoted_1:
        corrected=text_to_exam.replace('"','')
    elif double_quoted_2:
        corrected=text_to_exam.replace("'","")
    else: corrected=text_to_exam    
    return corrected        
def about():
    if Language.get()=="Spanish":
        title="Simplemente Datos Creador/Navegador"
        msg1="Creador del programa: Ross Waters\nDirección de correo electrónico: rosswatersjr@gmail.com\nPlataforma: Windows 11\n"
        msg2=f"Revisión: {version}"
        msg=msg1+msg2
    elif Language.get()=="English":
        title="Simply Data Creator/Browser"
        msg1="Created By: Ross Waters\nEmail Address: rosswatersjr@gmail.com\n"
        msg2=f"Revision {version}\n"
        msg3="Created For Windows 11"
        msg=msg1+msg2+msg3
    messagebox.showinfo(title, msg)
def restart_program():
    try:# Change Program Language
        if os.path.exists("Config.json"):write_config()
        for widget in root.winfo_children():# Destroys Menu Bars, Frame, Canvas And Scroll Bars
            if isinstance(widget, tk.canvas):widget.destroy()
            else:widget.destroy()
        DB.destroy_data_view()
        DB.destroy_edit_view()
        os.execl(sys.executable, os.path.abspath("Simply_Database.exe"), *sys.argv) 
    except Exception as ex:
        pass
        os.execl(sys.executable, os.path.abspath("Simply_Database.exe"), *sys.argv)
def go_back():
    DB.destroy_edit_view()
    DB.create_data_view()                
    DB.select_table(Active_Table.get())
def destroy(write=True):
    try:# X Icon Was Clicked
        if write:
            if os.path.exists("Config.json"):write_config()
        for widget in root.winfo_children():# Destroys Menu Bars, Frame, Canvas And Scroll Bars
            if isinstance(widget, tk.canvas):widget.destroy()
            else:widget.destroy()
        DB.destroy_data_view()
        DB.destroy_edit_view()
        os._exit(0)
    except Exception as ex:
        pass
        os._exit(0)
def disable_menubar(which):
    if Language.get()=="English":
        if which=="database" or which=="all":
            menubar.entryconfig('     Create/Select Database     ', state="disabled")
        if which=="tbl_menu" or which=="all":
            menubar.entryconfig('     Create/Select Table     ', state="disabled")
        if which=="modify_tbl_menu" or which=="all":
            menubar.entryconfig('     Search/Sort/Modify Table     ', state="disabled")
        if which=="modify_entry_menu" or which=="all":        
            menubar.entryconfig('     New Table Row/Column     ', state="disabled")
        if which=="Edit Colors" or which=="all":
            menubar.entryconfig('     Colors     ', state="disabled")
    elif Language.get()=="Spanish":        
        if which=="database" or which=="all":
            menubar.entryconfig('     Crear/Seleccionar Base de Datos     ', state="disabled")
        if which=="tbl_menu" or which=="all":
            menubar.entryconfig('     Crear/Seleccionar Tabla     ', state="disabled")
        if which=="modify_tbl_menu" or which=="all":
            menubar.entryconfig('     Buscar/Ordenar/Modificar Tabla     ', state="disabled")
        if which=="modify_entry_menu" or which=="all":        
            menubar.entryconfig('     Nueva Fila/Columna de Tabla     ', state="disabled")
        if which=="Edit Colors" or which=="all":
            menubar.entryconfig('     Colores     ', state="disabled")
def enable_menubar(which):
    if Language.get()=="English":                    
        if which=="database" or which=="all":
            menubar.entryconfig('     Create/Select Database     ', state="disabled")
        if which=="tbl_menu" or which=="all":
            menubar.entryconfig('     Create/Select Table     ', state="normal")
        if which=="modify_tbl_menu" or which=="all":
            menubar.entryconfig('     Search/Sort/Modify Table     ', state="normal")
        if which=="modify_entry_menu" or which=="all":        
            menubar.entryconfig('     New Table Row/Column     ', state="normal")
        if which=="Edit Colors" or which=="all":
            menubar.entryconfig('     Colors     ', state="normal")
    elif Language.get()=="Spanish":        
        if which=="database" or which=="all":
            menubar.entryconfig('     Crear/Seleccionar Base de Datos     ', state="disabled")
        if which=="tbl_menu" or which=="all":
            menubar.entryconfig('     Crear/Seleccionar Tabla     ', state="normal")
        if which=="modify_tbl_menu" or which=="all":
            menubar.entryconfig('     Buscar/Ordenar/Modificar Tabla     ', state="normal")
        if which=="modify_entry_menu" or which=="all":        
            menubar.entryconfig('     Nueva Fila/Columna de Tabla     ', state="normal")
        if which=="Edit Colors" or which=="all":
            menubar.entryconfig('     Colores     ', state="normal")
def set_menu_defaults():
    disable_menubar("tbl_menu")
    disable_menubar("modify_tbl_menu")
    disable_menubar("modify_entry_menu")
    disable_menubar("Edit Colors")
    if Language.get()=="English":
        modify_tbl_menu.entryconfig("Edit Table Definitions", state="disabled")
        modify_tbl_menu.entryconfig("Delete Table", state="disabled")
        modify_tbl_menu.entryconfig("Rename Table", state="disabled")
    elif Language.get()=="Spanish":    
        modify_tbl_menu.entryconfig("Editar Definiciones de Tabla", state="disabled")
        modify_tbl_menu.entryconfig("Eliminar Tabla", state="disabled")
        modify_tbl_menu.entryconfig("Renombrar Tabla", state="disabled")
def config_menu(selected=None):
    if Language.get()=="English":
        if selected=='db_selected':    
            menubar.entryconfig('     Create/Select Table     ', state="normal")
            menubar.entryconfig('     Search/Sort/Modify Table     ', state="normal")
            menubar.entryconfig('     New Table Row/Column     ', state="disabled")
            menubar.entryconfig('     Colors     ', state="disabled")
            num_tbls=DB.get_num_tbls()
            if num_tbls==0:
                menubar.entryconfig('     Create/Select Table     ', state="normal")
                tbl_menu.entryconfig("Create New Table", state="normal")
                modify_tbl_menu.entryconfig("Delete Table", state="disabled")
                modify_tbl_menu.entryconfig("Edit Table Definitions", state="disabled")
            else:
                menubar.entryconfig('     Create/Select Table     ', state="normal")
                modify_tbl_menu.entryconfig("Delete Table", state="normal")
                modify_tbl_menu.entryconfig("Edit Table Definitions", state="disabled")
            modify_tbl_menu.entryconfig("Rename Table", state="disabled")
        elif selected=='db_deleted':
            db_files=[file for file in os.listdir(DB_Path.get()) if os.path.splitext(file)[1] in DB_Extensions]# Retrieve All Databases In Folder
            if len(db_files)==0:
                menubar.entryconfig('     Create/Select Database     ', state="normal")
                db_menu.entryconfig('Delete Database', state="disabled")
                db_menu.entryconfig('Create Standard Database', state="normal")
                db_menu.entryconfig('Create Encrypted Database', state="normal")
                menubar.entryconfig('     Create/Select Table     ', state="disabled")
                menubar.entryconfig('     Search/Sort/Modify Table     ', state="disabled")
                menubar.entryconfig('     New Table Row/Column     ', state="disabled")
                menubar.entryconfig('     Colors     ', state="disabled")
            else:    
                menubar.entryconfig('     Create/Select Database     ', state="normal")
                db_menu.entryconfig('Create Standard Database', state="normal")
                db_menu.entryconfig('Create Encrypted Database', state="normal")
                db_menu.entryconfig('Delete Database', state="normal")
        elif selected==None:
            menubar.entryconfig('     Create/Select Database     ', state="normal")
            menubar.entryconfig('     Search/Sort/Modify Table     ', state="normal")
            num_tbls=DB.get_num_tbls()
            if num_tbls==0:# No Tables Exist
                menubar.entryconfig('     Create/Select Table     ', state="disabled")
                menubar.entryconfig('     Search/Sort/Modify Table     ', state="normal")
                menubar.entryconfig('     New Table Row/Column     ', state="disabled")
                menubar.entryconfig('     Colors     ', state="disabled")
                modify_tbl_menu.entryconfig("Search Table", state="disabled")
                modify_tbl_menu.entryconfig("Edit Table Definitions", state="disabled")
                modify_tbl_menu.entryconfig("Delete Table", state="disabled")
                modify_tbl_menu.entryconfig("Rename Table", state="disabled")
                modify_entry_menu.entryconfig("New Table Row", state="disabled")
                modify_entry_menu.entryconfig("New Table Column", state="disabled")
            else:# Tables Exist
                menubar.entryconfig('     Create/Select Table     ', state="normal")
                menubar.entryconfig('     Search/Sort/Modify Table     ', state="normal")
                menubar.entryconfig('     New Table Row/Column     ', state="normal")
                modify_tbl_menu.entryconfig("Search Table", state="normal")
                if Active_Table.get()=="":
                    modify_tbl_menu.entryconfig("Edit Table Definitions", state="disabled")
                    modify_tbl_menu.entryconfig("Rename Table", state="disabled")
                else:    
                    modify_tbl_menu.entryconfig("Edit Table Definitions", state="normal")
                    modify_tbl_menu.entryconfig("Rename Table", state="normal")
                modify_tbl_menu.entryconfig("Delete Table", state="normal")
                modify_entry_menu.entryconfig("New Table Row", state="normal")
                modify_entry_menu.entryconfig("New Table Column", state="normal")
    elif Language.get()=="Spanish":            
        if selected=='db_selected':    
            menubar.entryconfig('     Crear/Seleccionar Tabla     ', state="normal")
            menubar.entryconfig('     Buscar/Ordenar/Modificar Tabla     ', state="normal")
            menubar.entryconfig('     Nueva Fila/Columna de Tabla     ', state="disabled")
            menubar.entryconfig('     Colores     ', state="disabled")
            num_tbls=DB.get_num_tbls()
            if num_tbls==0:
                menubar.entryconfig('     Crear/Seleccionar Tabla     ', state="normal")
                tbl_menu.entryconfig("Crear Nueva Tabla", state="normal")
                modify_tbl_menu.entryconfig("Editar Definiciones de Tabla", state="disabled")
                modify_tbl_menu.entryconfig("Eliminar Tabla", state="disabled")
            else:
                menubar.entryconfig('     Crear/Seleccionar Tabla     ', state="normal")
                modify_tbl_menu.entryconfig("Editar Definiciones de Tabla", state="disabled")
                modify_tbl_menu.entryconfig("Eliminar Tabla", state="normal")
            modify_tbl_menu.entryconfig("Renombrar Tabla", state="disabled")
        elif selected=='db_deleted':
            db_files=[file for file in os.listdir(DB_Path.get()) if os.path.splitext(file)[1] in DB_Extensions]# Retrieve All Databases In Folder
            if len(db_files)==0:
                menubar.entryconfig('     Crear/Seleccionar Base de Datos     ', state="normal")
                db_menu.entryconfig('Eliminar Base de Datos', state="disabled")
                db_menu.entryconfig('Crear Base de Datos Estándar', state="normal")
                db_menu.entryconfig('Crear Base de Datos Encriptada', state="normal")
                menubar.entryconfig('     Crear/Seleccionar Tabla     ', state="disabled")
                menubar.entryconfig('     Buscar/Ordenar/Modificar Tabla     ', state="disabled")
                menubar.entryconfig('     Nueva Fila/Columna de Tabla     ', state="disabled")
                menubar.entryconfig('     Colores     ', state="disabled")
            else:    
                menubar.entryconfig('     Crear/Seleccionar Base de Datos     ', state="normal")
                db_menu.entryconfig('Crear Base de Datos Estándar', state="normal")
                db_menu.entryconfig('Crear Base de Datos Encriptada', state="normal")
                db_menu.entryconfig('Eliminar Base de Datos', state="normal")
        elif selected==None:
            menubar.entryconfig('     Crear/Seleccionar Base de Datos     ', state="normal")
            menubar.entryconfig('     Buscar/Ordenar/Modificar Tabla     ', state="normal")
            num_tbls=DB.get_num_tbls()
            if num_tbls==0:# No Tables Exist
                menubar.entryconfig('     Crear/Seleccionar Tabla     ', state="disabled")
                menubar.entryconfig('     Buscar/Ordenar/Modificar Tabla     ', state="normal")
                menubar.entryconfig('     Nueva Fila/Columna de Tabla     ', state="disabled")
                menubar.entryconfig('     Colores     ', state="disabled")
                modify_tbl_menu.entryconfig("Tabla de Búsqueda", state="disabled")
                modify_tbl_menu.entryconfig("Editar Definiciones de Tabla", state="disabled")
                modify_tbl_menu.entryconfig("Eliminar Tabla", state="disabled")
                modify_tbl_menu.entryconfig("Renombrar Tabla", state="disabled")
                modify_entry_menu.entryconfig("Nueva Fila de Tabla", state="disabled")
                modify_entry_menu.entryconfig("Nueva Columna de Tabla", state="disabled")
            else:# Tables Exist
                menubar.entryconfig('     Crear/Seleccionar Tabla     ', state="normal")
                menubar.entryconfig('     Buscar/Ordenar/Modificar Tabla     ', state="normal")
                menubar.entryconfig('     Nueva Fila/Columna de Tabla     ', state="normal")
                modify_tbl_menu.entryconfig("Tabla de Búsqueda", state="normal")
                if Active_Table.get()=="":
                    modify_tbl_menu.entryconfig("Editar Definiciones de Tabla", state="disabled")
                    modify_tbl_menu.entryconfig("Renombrar Tabla", state="disabled")
                else:    
                    modify_tbl_menu.entryconfig("Editar Definiciones de Tabla", state="normal")
                    modify_tbl_menu.entryconfig("Renombrar Tabla", state="normal")
                modify_tbl_menu.entryconfig("Eliminar Tabla", state="normal")
                modify_entry_menu.entryconfig("Nueva Fila de Tabla", state="normal")
                modify_entry_menu.entryconfig("Nueva Columna de Tabla", state="normal")
def populate_db_menu():
    db_menu.delete(0,"end")
    if Language.get()=="English":
        db_menu.add_command(label='Create Standard Database',command=lambda a="standard":DB.create_new_database(a))
        db_menu.add_command(label='Create Encrypted Database',command=lambda a="encrypted":DB.create_new_database(a))
        db_menu.add_command(label='Import Database',command=DB.import_database)
        db_menu.add_command(label='Delete Database',command=DB.delete_database)
        db_menu.add_separator()
        arrow_label=str('↓'+' Databases '+'↓')
        db_menu.add_command(label=arrow_label)
        db_menu.entryconfig(arrow_label, state="disabled")
        db_menu.add_separator()
    elif Language.get()=="Spanish":    
        db_menu.add_command(label='Crear Base de Datos Estándar',command=lambda a="standard":DB.create_new_database(a))
        db_menu.add_command(label='Crear Base de Datos Encriptada',command=lambda a="encrypted":DB.create_new_database(a))
        db_menu.add_command(label='Importar Base de Datos',command=DB.import_database)
        db_menu.add_command(label='Eliminar Base de Datos',command=DB.delete_database)
        db_menu.add_separator()
        arrow_label=str('↓'+' Base de Datos '+'↓')
        db_menu.add_command(label=arrow_label)
        db_menu.entryconfig(arrow_label, state="disabled")
        db_menu.add_separator()
    db_files=[file for file in os.listdir(DB_Path.get()) if os.path.splitext(file)[1] in DB_Extensions]# Retrieve All Databases In Folder
    db_files=sorted(db_files)
    for i in range(len(db_files)):# Populate db_menu
        lbl_name=db_files[i]
        db_menu.add_command(label=lbl_name,command=lambda a=DB_Path.get(),b=db_files[i]:DB.select_database(a,b))
        db_menu.add_separator()
def populate_menus():
    if Language.get()=="English":
        readme_path=os.path.join(Path(__file__).parent.absolute(),"Readme_English.txt")
        menubar.add_cascade(label='     File     ',menu=file_menu)
        file_menu.add_command(label='Change Language',command=lambda:change_language())
        file_menu.add_separator()
        file_menu.add_command(label='Reset Password',command=lambda:change_password())
        file_menu.add_separator()
        file_menu.add_command(label='Read Me',command=lambda:subprocess.Popen(["notepad.exe", readme_path]))
        file_menu.add_separator()
        file_menu.add_command(label='About',command=lambda:about())
        file_menu.add_separator()
        file_menu.add_command(label='Exit',command=lambda:destroy())
        menubar.add_cascade(label='     Create/Select Database     ',menu=db_menu)
        populate_db_menu()
        menubar.add_cascade(label='     Create/Select Table     ',menu=tbl_menu)
        tbl_menu.add_separator()
        menubar.add_cascade(label='     Search/Sort/Modify Table     ',menu=modify_tbl_menu)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Search Table',command=DB.search_table)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Sort Table (A-Z)',command=lambda:DB.sort_table('ASC'))
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Sort Table (Z-A)',command=lambda:DB.sort_table('DESC'))
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Edit Table Definitions',command=DB.edit_table_definitions)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Rename Table',command=DB.rename_table)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Delete Table',command=DB.delete_table)
        modify_tbl_menu.add_separator()
        menubar.add_cascade(label='     New Table Row/Column     ',menu=modify_entry_menu)
        modify_entry_menu.add_command(label='New Table Row',command=DB.new_table_row)
        modify_entry_menu.add_separator()
        modify_entry_menu.add_command(label='New Table Column',command=DB.new_table_column)
        modify_entry_menu.add_separator()
        menubar.add_cascade(label='     Colors     ',menu=color_menu)
        menubar.entryconfig('     Search/Sort/Modify Table     ', state="disabled")
    elif Language.get()=="Spanish":    
        readme_path=os.path.join(Path(__file__).parent.absolute(),"Readme_Spanish.txt")
        menubar.add_cascade(label='     Archivo     ',menu=file_menu)
        file_menu.add_command(label='Cambiar Idioma',command=lambda:change_language())
        file_menu.add_separator()
        file_menu.add_command(label='Restablecer Contraseña',command=lambda:change_password())
        file_menu.add_separator()
        file_menu.add_command(label='Léeme',command=lambda:subprocess.Popen(["notepad.exe", readme_path]))
        file_menu.add_separator()
        file_menu.add_command(label='Acerca de',command=lambda:about())
        file_menu.add_separator()
        file_menu.add_command(label='Salida',command=lambda:destroy())
        menubar.add_cascade(label='     Crear/Seleccionar Base de Datos     ',menu=db_menu)
        populate_db_menu()
        menubar.add_cascade(label='     Crear/Seleccionar Tabla     ',menu=tbl_menu)
        tbl_menu.add_separator()
        menubar.add_cascade(label='     Buscar/Ordenar/Modificar Tabla     ',menu=modify_tbl_menu)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Tabla de Búsqueda',command=DB.search_table)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Ordenar Tabla (A-Z)',command=lambda:DB.sort_table('ASC'))
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Ordenar Tabla (Z-A)',command=lambda:DB.sort_table('DESC'))
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Editar Definiciones de Tabla',command=DB.edit_table_definitions)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Renombrar Tabla',command=DB.rename_table)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Eliminar Tabla',command=DB.delete_table)
        modify_tbl_menu.add_separator()
        menubar.add_cascade(label='     Nueva Fila/Columna de Tabla     ',menu=modify_entry_menu)
        modify_entry_menu.add_command(label='Nueva Fila de Tabla',command=DB.new_table_row)
        modify_entry_menu.add_separator()
        modify_entry_menu.add_command(label='Nueva Columna de Tabla',command=DB.new_table_column)
        modify_entry_menu.add_separator()
        menubar.add_cascade(label='     Colores     ',menu=color_menu)
        menubar.entryconfig('     Buscar/Ordenar/Modificar Tabla     ', state="disabled")
def populate_color_menu():
    if Language.get()=="English":
        color_menu.add_command(label='Main Window Color',command=lambda:DB.change_colors('window_color'))
        color_menu.add_separator()
        color_menu.add_command(label='Headings Text Color',command=lambda:DB.change_colors('header_text'))
        color_menu.add_command(label='Headings Background Color',command=lambda:DB.change_colors('header_bg'))
        color_menu.add_separator()
        color_menu.add_command(label='Odd Row Data Text Color',command=lambda:DB.change_colors('odd_text'))
        color_menu.add_command(label='Odd Row Data Background Color',command=lambda:DB.change_colors('odd_bg'))
        color_menu.add_separator()
        color_menu.add_command(label='Even Row Data Text Color',command=lambda:DB.change_colors('even_txt'))
        color_menu.add_command(label='Even Row Data Background Color',command=lambda:DB.change_colors('even_bg'))
        color_menu.add_separator()
    elif Language.get()=="Spanish":    
        color_menu.add_command(label='Color de la Ventana Principal',command=lambda:DB.change_colors('window_color'))
        color_menu.add_separator()
        color_menu.add_command(label='Encabezados Color del Texto',command=lambda:DB.change_colors('header_text'))
        color_menu.add_command(label='Encabezados Color de Fondo',command=lambda:DB.change_colors('header_bg'))
        color_menu.add_separator()
        color_menu.add_command(label='Color del Texto de los Datos de Fila Impares',command=lambda:DB.change_colors('odd_text'))
        color_menu.add_command(label='Color de Fondo de Datos de Fila Impar',command=lambda:DB.change_colors('odd_bg'))
        color_menu.add_separator()
        color_menu.add_command(label='Color de Texto de Datos de Fila Uniforme',command=lambda:DB.change_colors('even_txt'))
        color_menu.add_command(label='Color de Fondo de Datos de Fila Uniforme',command=lambda:DB.change_colors('even_bg'))
        color_menu.add_separator()
def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()
def set_defaults():
    entered_password=my_askstring("Simply Data Login", "Please Enter A Login Password!", "")
    if entered_password==None or entered_password=="":destroy()
    else:
        My_Pass.set(hash_password(entered_password))
        key=entered_password
        key=key[::-1]
        Encryption_key.set(key)
    Language.set("English")
    Window_Color.set("#d5ffff")
    Header_Bg_Color.set('#f9ff99')
    Heading_Text_Color.set('#072663')
    Odd_Text_Color.set('#000000')
    Even_Text_Color.set('#000000')
    Odd_Bg_Color.set('#dedede')
    Even_Bg_Color.set('#eeeeee')
    data={}
    with open("Config.json", "w") as json_file:# Create Empty json File
            json.dump(data, json_file, indent=4) # indent=4 for pretty-printing
            json_file.close()
    data={"0": Language.get(),"1": str(root_width),"2": str(root_height),
          "3": str(root_x),"4": str(root_y),"5": Window_Color.get(),
          "6": Heading_Text_Color.get(),"7": Header_Bg_Color.get(),
          "8": Odd_Text_Color.get(),"9": Odd_Bg_Color.get(),"10": Even_Text_Color.get(),
          "11": Even_Bg_Color.get(),"12": My_Pass.get(),"13": Encryption_key.get()}
    with open("Config.json", 'w') as json_file:
        json.dump(data, json_file, indent=4)
        json_file.close()
    data.clear()
    root.geometry('%dx%d+%d+%d' % (root_width, root_height,  root_x, root_y))
    root.update()
if __name__ == '__main__':
    root=tk.Tk()
    style=ttk.Style()
    style.theme_use('alt')
    style.map('TCombobox', background=[('readonly','#0b5394')])# Down Arrow 
    style.map('TCombobox', fieldbackground=[('readonly','#bfffff')])
    style.map('TCombobox', selectbackground=[('readonly','#0b5394')])
    style.map('TCombobox', selectforeground=[('readonly', '#ffffff')])
    style.configure("TCombobox", arrowsize=16, arrowcolor="aqua")
    style.configure("Vertical.TScrollbar", background="#094983")
    style.configure("Horizontal.TScrollbar", background="#094983")
    style.configure("Vertical.TScrollbar", arrowsize=20, arrowcolor="aqua")
    style.configure("Horizontal.TScrollbar", arrowsize=20, arrowcolor="aqua")
    style.configure('My.TFrame', background='lightgray')
    my_font=font.Font(family='Times New Romans', size=10, weight='bold', slant='italic')
    root.protocol("WM_DELETE_WINDOW", destroy)
    DB_Path=StringVar()
    DB_Path.set(Path(__file__).parent.absolute())
    primary_monitor=MonitorFromPoint((0, 0))
    monitor_info=GetMonitorInfo(primary_monitor)
    monitor_area=monitor_info.get("Monitor")
    work_area=monitor_info.get("Work")
    taskbar_height=monitor_area[3]-work_area[3]
    screen_height=work_area[3]-taskbar_height
    root_width=int(work_area[2]*0.6)
    root_height=int(work_area[3]*0.4)
    root_x=(work_area[2]/2)-(root_width/2)
    root_y=(work_area[3]/2)-(root_height/2)
    ico_path=os.path.join(Path(__file__).parent.absolute(),"Database.ico")
    root.iconbitmap(default=ico_path) # root and children
    readme_path=os.path.join(Path(__file__).parent.absolute(),"ReadMe.txt")
    DB_Extensions=[".db",".db2",".db3",".sl2",".sl3",".sdb",".s2db",".sqlite",".sqlite2",".sqlite3"]
    Language=StringVar()
    Window_Color=StringVar()
    Header_Bg_Color=StringVar()
    Heading_Text_Color=StringVar()
    Odd_Text_Color=StringVar()
    Even_Text_Color=StringVar()
    Odd_Bg_Color=StringVar()
    Even_Bg_Color=StringVar()
    DB_Name=StringVar()# Name Of Database Without Exts Or Spaces
    Active_DB=StringVar()# Complete Address Of Database File With Exts Without Spaces
    Active_Table=StringVar()
    Edit_Definitions=BooleanVar()
    Edit_Definitions.set(False)
    menubar=Menu(root)# Create Menubar
    file_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=my_font)# File Menu and commands
    db_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=my_font)# File Menu and commands
    tbl_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=my_font)# File Menu and commands
    modify_tbl_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=my_font)# File Menu and commands
    modify_entry_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=my_font)# File Menu and commands
    color_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=my_font)# File Menu and commands
    root.config(menu=menubar)
    DB=SQL3_Database(root)
    DB.create_data_view()
    My_Pass=StringVar()
    Encryption_key=StringVar()
    root.withdraw()
    if not os.path.exists("Config.json"):set_defaults()
    else:
        read_config()
        if Language.get()=="English":msg="Please Enter A Login Password!"
        elif Language.get()=="Spanish":msg="¡Por favor, Introduzca una Contraseña de Inicio de Sesión!"
        while True:
            entered_password =my_askstring("Simply Data Login", msg, "")
            if entered_password==None:destroy(False)
            else:entered_hashed_password = hash_password(entered_password)
            if entered_hashed_password == My_Pass.get():break
            if Language.get()=="English":msg="Error! Please Try And Enter The Password Again."
            elif Language.get()=="Spanish":msg="¡Error! Por favor, inténtelo de nuevo e ingrese la contraseña nuevamente."
    root.deiconify()
    root.after(500, select_language(restart=False))
    if Language.get()=="English":root.title("Simply Data Creator/Browser")
    else:root.title("Simplemente Datos Creador/Navegador")
    root.mainloop()
