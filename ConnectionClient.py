#clientscreen.py
from tkinter import *
from tkinter import font
from tkinter import messagebox
from functools import partial
import socket, _thread

HOST = 'localhost'
PORT = 9009
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def recieveThread():
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            chatbox.insert(END, data.decode())
            pass
        except OSError:
            pass
        except Exception as e:
            messagebox.showerror("죄송해요!", "다음의 문제가 발생했습니다 : \n" + str(e))
            break
        pass
    sock.close()
    pass

def sendMessage(box, event):
    try:
        sock.send(box.get().encode())
        box.delete(0, 'end')
        pass
    except Exception as e:
        messagebox.showerror("죄송해요!", "다음의 문제가 발생했습니다 : \n" + str(e))
        pass
    pass

root = Tk()
root.title("Connection")
root.geometry("400x500")

def donothing():
    pass

def startConnection(dialog, hostentry, portentry):
    global sock
    if not len(hostentry.get()) == 0 and not len(portentry.get()) == 0:
        HOST = hostentry.get()
        port = int(portentry.get())
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
            _thread.start_new_thread(recieveThread, ())
            destroyDialog(dialog)
            pass
        except Exception as e:
            print(e)
            messagebox.showerror("죄송해요!", "서버와의 연결에 문제가 발생했습니다.\n나중에 다시 시도해보세요!")
            pass
    else:
        messagebox.showerror("잠깐만요!", "호스트와 포트를 정확하게 입력해주세요!")
        pass    
    pass

def destroyDialog(dialog):
    dialog.destroy()

def enterRoom():
    dialog = Toplevel()
    dialog.title("채팅방 접속")
    dialog.geometry("240x120")

    #dialog - Frame Layout
    hostframe = Frame(dialog)
    portframe = Frame(dialog)
    btnframe = Frame(dialog)
    hostframe.pack(side=TOP, padx=10, pady=10)
    portframe.pack(side=TOP, padx=10)
    btnframe.pack(side=BOTTOM, padx=10, pady=10)

    #dialog - Host Input
    hostlabel = Label(hostframe, text="HOST : ", font=font)
    hostentry = Entry(hostframe, font=font, bd=3)
    hostlabel.pack(side=LEFT)
    hostentry.pack(side=RIGHT, expand=True, fill=X)
    
    #dialog - Port Input
    portlabel = Label(portframe, text="PORT : ", font=font)
    portentry = Entry(portframe, font=font, bd=3)
    portlabel.pack(side=LEFT)
    portentry.pack(side=RIGHT, expand=True, fill=X)

    #dialog - Ok, Cancel Btn
    okbutton = Button(btnframe, text="  확인  ", font=font, command = partial(startConnection, dialog, hostentry, portentry))
    spacelabel = Label(btnframe, text=" ", font=font)
    cancelbutton = Button(btnframe, text="  취소  ", font=font, command = partial(destroyDialog, dialog))
    okbutton.pack(side=LEFT)
    cancelbutton.pack(side=RIGHT)
    spacelabel.pack(side=RIGHT)

    dialog.mainloop()
    pass

def exitRoom():
    sock.send("/quit".encode())
    sock.close()
    pass

#font manager
font = font.Font(family="맑은 고딕", size=10)

#menu creator
menubar = Menu(root)
conmenu = Menu(menubar, tearoff=0)
conmenu.add_command(label="채팅방 접속하기", font=font, command = enterRoom)
conmenu.add_command(label="채팅방 나가기", font=font, command = exitRoom)
menubar.add_cascade(label="채팅방", font=font, menu = conmenu)
root.config(menu = menubar)

#frame creator
listframe = Frame(root, padx=10, pady=10)
inputframe = Frame(root, padx=10, pady=5, bg="#cccccc")
listframe.pack(side=TOP, expand = True, fill=BOTH)
inputframe.pack(side=BOTTOM, fill=X)

#listbox creator
scrollbar = Scrollbar(listframe)
scrollbar.pack(side=RIGHT, fill=Y)
chatbox = Listbox(listframe, font=font, yscrollcommand = scrollbar.set)
chatbox.pack(side=LEFT, expand = True, fill=BOTH)
scrollbar.config(command = chatbox.yview)

#input creator
inputlabel = Label(inputframe, text = "메세지 :  ", font=font, bg="#cccccc")
inputlabel.pack(side=LEFT)
inputbox = Entry(inputframe, bd=3, font=font)
sendbutton = Button(inputframe, text="전송", font=font, command = partial(sendMessage, inputbox, None), padx=15, bg="#cccccc")
sendbutton.pack(side=RIGHT)
spacelabel = Label(inputframe, text =" ", font=font, bg="#cccccc")
spacelabel.pack(side=RIGHT)
inputbox.pack(side=RIGHT, expand = True, fill=X)

root.bind('<Return>', partial(sendMessage, inputbox))

root.mainloop()
