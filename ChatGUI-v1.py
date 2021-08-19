#!/usr/bin/env python
import PySimpleGUI as sg
import socketio
import requests
import urllib.parse
import json

sio = socketio.Client()
url = input('What is the ip? Remember to add the "http" as well!')
s = requests.Session()

sg.theme('LightGreen1') # give our window a spiffy set of colors

#1
#2
#5

#layout for gui
layout = [[sg.Text(text = "Chathub GUI                                                 "), 
        sg.Input(size=(25, 10), default_text="Username", key='username', do_not_clear=False),
        sg.Input(size=(25, 10), default_text="Password", key='password', do_not_clear=False),
        sg.Button('Login')],
        [sg.Multiline(size=(80, 20), font=('Arial, 10'), key='_OUT_', write_only=True, autoscroll=True, reroute_cprint=True), #Output
        sg.Multiline(size=(30, 17), key='userList')], #User List
        [sg.Multiline('Enter', size=(70, 1), key='-QUERY-', do_not_clear=False, enter_submits = True), #Input
        sg.Button('Enter', size=(10, 1), button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=True)]]

window = sg.Window('ChatHub v1.0', layout, font=('Helvetica', ' 13'), resizable=False,finalize=True, default_button_element_size=(8,2), use_default_focus=False)
width, height = window.get_screen_size()

window.Element('_OUT_').bind("<FocusIn>", '+FOCUS_IN+')
window.Element('_OUT_').bind("<FocusOut>", '+FOCUS_OUT+')
window.Element('userList').bind("<FocusIn>", '+FOCUS_IN+')
window.Element('userList').bind("<FocusOut>", '+FOCUS_OUT+')

emotes = {
    "sob": "😭",
    "silly": "🤪",
    "smiley": "😀",
    "sweat": "😅",
    "lol": "🤣",
    "quiet": "🤫",
    "tougue": "😛",
    "thinking": "🤔",
    "no_mouth": "😶",
    "pensive": "😔",
    "vomiting": "🤮",
    "sleeping": "😴",
    "dizzy": "😵",
    "eggplant": "🍆",
    "sweat_drops": "💦",
    "monkey": "🐵",
    "sus": "😳",
    "eyes": "👀",
    "sunglasses": "😎",
    "spacecat": "🐱‍🚀",
    "flushed": "😳"
}

def send_msg(msg):
    query = msg
    for i in emotes:
        query = query.replace(":"+i+":", emotes[i])
    output = urllib.parse.quote(query)
    try: 
        s.get(f"{url}/getmessage?messagebox={output}")
    except requests.exceptions.ConnectionError:
        sg.popup_error('ChatHub is currently not online. Please try again later!')
        window.close()

@sio.event
def connect():
    print('Connected to ChatHub-1')

@sio.event
def disconnect():
    print('disconnected from server')

@sio.on('chat message')
def msgSent():
    req = s.get(f"{url}/messages.json")
    raw = req.content.decode('utf-8')
    msgs = json.loads(raw)
    output = ""
    for i in msgs:
        output = output + i + "\n"
    #output = output + " \033                             \033"

    #window.FindElement('_OUT_').Update(output)
    sg.cprint(output)
try:
    msgSent()
except requests.exceptions.ConnectionError:
        sg.popup_error('ChatHub is currently not online. Please try again later!')
        window.close()

@sio.on('user join')
def userList(data):
    users = ""
    for i in data:
        users = users + i + "\n"
    window.FindElement('userList').Update(users)

@sio.on('user leave')
def userList(data):
    users = ""
    for i in data:
        users = users + i + "\n"
    window.FindElement('userList').Update(users)

try:
    sio.connect(url)  
except socketio.exceptions.ConnectionError:
    sg.popup_error('ChatHub is currently not online. Please try again later!')
    window.close()

while True:     # The Event Loop
    event, value = window.read()
    if event == None:
        break
    if event == 'Enter':
        query = str(value['-QUERY-'].rstrip())
        # EXECUTE YOUR COMMAND HERE
        send_msg(query)
    if event == 'Login':
        user = str(value['username'].rstrip())
        password = str(value['password'].rstrip())
        req = requests.get(f'{url}/loginuser?username={user};password={password}')
        file = str(req.content.decode('utf-8'))
        if ("jfDIo89DVjio(S2390f" in file) == True:
            #sg.popup("Invalid Credentials. Try Again")
            window.FindElement('password').Update('Password')
        else:
            s.cookies.set('username', user, domain='localhost.local')
            s.cookies.set('password', password, domain='localhost.local')
            #sg.popup('Login Complete!')
            msgSent()

    if event == '_OUT_+FOCUS_IN+':
        widget = window['_OUT_'].Widget
        widget.bind("<1>", widget.focus_set())
        window['_OUT_'].update(disabled=True)
    elif event == '_OUT_+FOCUS_OUT+':
        window['_OUT_'].Widget.unbind("<1>")
        window['_OUT_'].update(disabled=False)

    if event == 'userList+FOCUS_IN+':
        widget = window['userList'].Widget
        widget.bind("<1>", widget.focus_set())
        window['userList'].update(disabled=True)
    elif event == 'userList+FOCUS_OUT+':
        window['userList'].Widget.unbind("<1>")
        window['userList'].update(disabled=False)



window.close()