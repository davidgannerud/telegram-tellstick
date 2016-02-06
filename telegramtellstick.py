# coding: utf-8

import sys
import time
import pprint
import telepot
from tellcore.telldus import TelldusCore
import os
import untangle

DF_DEFAULT = 99
DF_GROUPS = 88
DF_ALL = 12

def showMain(chat_id):
    global userState
    global mainKeyboard
    
    show_keyboard = {'keyboard': mainKeyboard}

    bot.sendMessage(chat_id, 'Light control', reply_markup=show_keyboard)
    userState[userIds.index(chat_id)] = DF_DEFAULT

def showGroups(chat_id):
    global userState
    global groupKeyboard
    
    show_keyboard = {'keyboard': groupKeyboard}

    bot.sendMessage(chat_id, xmlObj.control.btn_groups['name'], reply_markup=show_keyboard)
    userState[userIds.index(chat_id)] = DF_GROUPS
    

def lights(chat_id, command):
    global userState
    if userState[userIds.index(chat_id)] == DF_DEFAULT:
        if command == xmlObj.control.btn_close['name'].lower():
             hide_keyboard = {'hide_keyboard': True}
             bot.sendMessage(chat_id, u'Close light control', reply_markup=hide_keyboard)
        elif command == xmlObj.control.btn_groups['name'].lower():
            showGroups(chat_id)
        else:
            for index in range(0, len(names)):
                if command == names[index].lower():
                    show_keyboard = {'keyboard': [  [xmlObj.control.btn_on['name']],
                                                    [xmlObj.control.btn_off['name']],
                                                    [xmlObj.control.btn_return['name']]]}
                    bot.sendMessage(chat_id, names[index], reply_markup=show_keyboard)
                    userState[userIds.index(chat_id)] = index
                    break
#     elif userState[userIds.index(chat_id)] == DF_GROUPS:
#         if command == xmlObj.control.btn_on['name'].lower():
#             for item in groups:
#                 item.turn_on()
#         elif command == xmlObj.control.btn_off['name'].lower():
#             for item in lightList:
#                 item.turn_off()
#         else:
#             for cmd in groups:
#                 if command == cmd[0].lower():
#                     show_keyboard = {'keyboard': [  [xmlObj.control.btn_on['name']],
#                                                     [xmlObj.control.btn_off['name']],
#                                                     [xmlObj.control.btn_return['name']]]}
#                     bot.sendMessage(chat_id, names[index], reply_markup=show_keyboard)
#                     userState[userIds.index(chat_id)] = index
#                     break
#     elif userState[userIds.index(chat_id)] == DF_ALL:
#         if command == u'tänd':
#             for item in lightList:
#                 item.turn_on()
#         elif command == u'släck':
#             for item in lightList:
#                 item.turn_off()
#         else:
#             showMain(chat_id) 
    else:
        if command == xmlObj.control.btn_on['name'].lower():
            lightList[userState[userIds.index(chat_id)]].turn_on()
        elif command == xmlObj.control.btn_off['name'].lower():
            lightList[userState[userIds.index(chat_id)]].turn_off()
        else:
            showMain(chat_id)

def handle(msg):

    pprint.pprint(msg)
    content_type, chat_type, chat_id = telepot.glance2(msg)
    validUser = False
	
    # only respond to one user
    for user in userIds:
        if chat_id == user:
            validUser = True
            
    if validUser == False:
        return

    # ignore non-text message
    if content_type != 'text':
        return

    command = msg['text'].strip().lower().split()

    if command[0] == '/start':
        showMain(chat_id)
    elif command[0] == '/close':
        hide_keyboard = {'hide_keyboard': True}
        bot.sendMessage(chat_id, 'Closing light control', reply_markup=hide_keyboard)
#     elif command[0] == '/add':
#         addEvent(chat_id, command)
    else:
        lights(chat_id, command[0])


# Getting the token from command-line is better than embedding it in code,
# because tokens are supposed to be kept secret.
TOKEN = sys.argv[1]
userIds = []
userState = []

for index in range(2, len(sys.argv)):
    userIds.append(long(sys.argv[index]))
    userState.append(DF_DEFAULT)

localtime = time.asctime( time.localtime(time.time()) )
print "Local current time :", localtime

print 'Init telldus core'
lightcore = TelldusCore()
lightList = []
names = []
groups = []
groups.append([])

# Parse from XML
xmlObj = untangle.parse('config.xml')

for switch in xmlObj.control.devices.switch:
    lightList.append(lightcore.add_device(  switch['name'], 
                                            switch['protocol'], 
                                            switch['model'], 
                                            house=switch['house'], 
                                            unit=switch['unit'], 
                                            code=switch['code']))
    names.append(switch['name'])

row = 0
# for group in xmlObj.control.group:
#     #print group['name']
#     groups[row].append(group['name'])
#     groups[row].append(group['repeats'])
#     
#     for switch in group.switch:
#         #print switch['name']
#         groups[row].append(switch['name'])
#         
#     print groups[row]
#     row += 1
#     groups.append([])

# Create keyboards
x = 0
y = 0
mainKeyboard = []
mainKeyboard.append([])

for label in names:
    mainKeyboard[y].append(label)
    x += 1
    if x == 3:
        x = 0
        y += 1
        mainKeyboard.append([])

mainKeyboard.append([])
mainKeyboard[y].append(xmlObj.control.btn_groups['name'])
mainKeyboard[y].append(xmlObj.control.btn_close['name'])


groupKeyboard = []

# for groupName in groups:
#     groupKeyboard.append(groupName[0])

groupKeyboard.append(xmlObj.control.btn_return['name'])


print 'Init bot'
bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
print 'Bot started'

# Keep the program running.
while 1:
    time.sleep(1)
