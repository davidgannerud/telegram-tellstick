# coding: utf-8

import sys
import time
import pprint
import telepot
from tellcore.telldus import TelldusCore
import os
import untangle

DF_DEFAULT = 0
DF_SINGLE = 1000
DF_GROUPS = 2000

def showMainKeyboard(chat_id, user_state):
	global main_keyboard
	global userIds
	
	show_keyboard = {'keyboard': main_keyboard}

	bot.sendMessage(chat_id, 'Light control', reply_markup=show_keyboard)
	user_state[userIds.index(chat_id)] = DF_DEFAULT


def showGroupsKeyboard(chat_id, user_state):
	global group_keyboard

	show_keyboard = {'keyboard': group_keyboard}

	bot.sendMessage(chat_id, xml_config.control.btn_groups['name'], reply_markup=show_keyboard)
	user_state[userIds.index(chat_id)] = DF_GROUPS

def groupCommand(chat_id, command, user_state):
	global userIds
	
	if command == xml_config.control.btn_on['name'].lower():
		group_index = user_state[userIds.index(chat_id)] - DF_GROUPS
		for i in range(2, len(groups[group_index])):
			light_index = names.index(groups[group_index][i])
 			lightList[light_index].turn_on()
 		showMainKeyboard(chat_id, user_state)
	elif command == xml_config.control.btn_off['name'].lower():
		group_index = user_state[userIds.index(chat_id)] - DF_GROUPS
		for i in range(2, len(groups[group_index])):
			light_index = names.index(groups[group_index][i])
 			lightList[light_index].turn_off()
 		showMainKeyboard(chat_id, user_state)
	elif command == xml_config.control.btn_return['name'].lower():
		showMainKeyboard(chat_id, user_state)
	else:
		for index in range(0, len(groups)):
			if command == groups[index][0].lower():
				user_state[userIds.index(chat_id)] += index
				break
				
		show_keyboard = {'keyboard': [  [xml_config.control.btn_on['name']],
										[xml_config.control.btn_off['name']],
										[xml_config.control.btn_return['name']]]}
		bot.sendMessage(chat_id, command, reply_markup=show_keyboard)

def singleCommand(chat_id, command, user_state):
	if command == xml_config.control.btn_on['name'].lower():
		lightList[user_state[userIds.index(chat_id)] - DF_SINGLE].turn_on()
		showMainKeyboard(chat_id, user_state)
	elif command == xml_config.control.btn_off['name'].lower():
		lightList[user_state[userIds.index(chat_id)] - DF_SINGLE].turn_off()
		showMainKeyboard(chat_id, user_state)
	elif command == xml_config.control.btn_return['name'].lower():
		showMainKeyboard(chat_id, user_state)

def lights(chat_id, command):
	print command

	if (user_state[userIds.index(chat_id)]) == DF_DEFAULT:
		if command == xml_config.control.btn_close['name'].lower():
			 hide_keyboard = {'hide_keyboard': True}
			 bot.sendMessage(chat_id, u'Close light control', reply_markup=hide_keyboard)
		elif command == xml_config.control.btn_groups['name'].lower():
			showGroupsKeyboard(chat_id, user_state)
		else:
			for index in range(0, len(names)):
				if command == names[index].lower():
					show_keyboard = {'keyboard': [  [xml_config.control.btn_on['name']],
													[xml_config.control.btn_off['name']],
													[xml_config.control.btn_return['name']]]}
					bot.sendMessage(chat_id, names[index], reply_markup=show_keyboard)
					user_state[userIds.index(chat_id)] = DF_SINGLE + index
					break
	elif (user_state[userIds.index(chat_id)] & DF_SINGLE) == DF_SINGLE:
		singleCommand(chat_id, command, user_state)
	elif (user_state[userIds.index(chat_id)] & DF_GROUPS) == DF_GROUPS:
		groupCommand(chat_id, command, user_state)


def handle(msg):
	global user_state
# 	pprint.pprint(msg)
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
		showMainKeyboard(chat_id, user_state)
	elif command[0] == '/close':
		hide_keyboard = {'hide_keyboard': True}
		bot.sendMessage(chat_id, 'Closing light control', reply_markup=hide_keyboard)
	else:
		lights(chat_id, command[0])


# Getting the token from command-line is better than embedding it in code,
# because tokens are supposed to be kept secret.
TOKEN = sys.argv[1]
userIds = []
user_state = []

for index in range(2, len(sys.argv)):
	userIds.append(long(sys.argv[index]))
	user_state.append(DF_DEFAULT)

localtime = time.asctime( time.localtime(time.time()) )
print "Local current time :", localtime

print 'Init telldus core'
lightcore = TelldusCore()
lightList = []
names = []
groups = []

# Parse from XML
xml_config = untangle.parse('config.xml')

for switch in xml_config.control.devices.switch:
	names.append(switch['name'])
	lightList.append(lightcore.add_device(  switch['name'], 
											switch['protocol'], 
											switch['model'], 
											house=switch['house'], 
											unit=switch['unit'], 
											code=switch['code']))

# Extract groups from config file
row = 0
for group in xml_config.control.group:
	groups.append([])
	groups[row].append(group['name'])
	groups[row].append(group['repeats'])

	for switch in group.switch:
		groups[row].append(switch['name'])

	row += 1


# Create main keyboard
col = 0
row = 0
main_keyboard = []
main_keyboard.append([])

for label in names:
	main_keyboard[row].append(label)
	col += 1
	if col == 3:
		col = 0
		row += 1
		main_keyboard.append([])

if col > 2:
	row += 1
	main_keyboard.append([])

main_keyboard[row].append(xml_config.control.btn_groups['name'])
main_keyboard[row].append(xml_config.control.btn_close['name'])


# Create group keyboard
group_keyboard = []
group_keyboard.append([])

for groupName in groups:
	group_keyboard[0].append(groupName[0])

group_keyboard[0].append(xml_config.control.btn_return['name'])


print 'Init bot'
bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
print 'Bot started'

# Keep the program running.
while 1:
	time.sleep(1)
