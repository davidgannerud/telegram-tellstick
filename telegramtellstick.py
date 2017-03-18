import sys
import time
import untangle
from tellcore.telldus import TelldusCore
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton

def on_chat_message(msg):
    global main_keyboard
    global user_status

    print(msg)
    content_type, chat_type, chat_id = telepot.glance(msg)
    command = msg['text'].strip().lower().split()[0]
    user_id = str(chat_id)

    if command == xml_config.control.btn_on['name'].lower():
        user_status[user_id] = 'on'
    elif command == xml_config.control.btn_off['name'].lower():
        user_status[user_id] = 'off'
    else:
        print('Unknown command ', command)

    keyboard = InlineKeyboardMarkup(inline_keyboard=main_keyboard)
    bot.sendMessage(chat_id, 'Light Control', reply_markup=keyboard)

    show_keyboard = {'keyboard': [  [xml_config.control.btn_on['name']],
                                    [xml_config.control.btn_off['name']]]}
    bot.sendMessage(chat_id, user_status[user_id], reply_markup=show_keyboard)

def on_callback_query(msg):
    query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
    global user_status
    print('Callback Query:', query_id, chat_id, query_data)
    user_id = str(chat_id)

    single_command(user_id, query_id, query_data)

def single_command(user_id, query_id, query_data):
    global user_status
    if user_status[user_id] == 'on':
        light_list[query_data].turn_on()
        bot.answerCallbackQuery(query_id, text=xml_config.control.btn_on['name'] + ' ' + query_data)
    elif user_status[user_id] == 'off':
        light_list[query_data].turn_off()
        bot.answerCallbackQuery(query_id, text=xml_config.control.btn_off['name'] + ' ' + query_data)

# def group_command(user_id):
#     global user_status
#
#     repeats = 0
#
#     if command == xml_config.control.btn_on['name'].lower():
#         group_index = user_state[user_ids.index(chat_id)] - DF_GROUPS
#
#
#     elif command == xml_config.control.btn_off['name'].lower():
#         group_index = user_state[user_ids.index(chat_id)] - DF_GROUPS
#         while repeats < int(groups[group_index][1]):
#             repeats += 1
#             for i in range(2, len(groups[group_index])):
#                 light_index = names.index(groups[group_index][i])
#                 light_list[light_index].turn_off()
#
#     # TODO Loop over groups
#     if user_status[user_id] == 'on':
#         while repeats < int(groups[group_index][1]):
#             repeats += 1
#             for i in range(2, len(groups[group_index])):
#                 # light_index = names.index(groups[group_index][i])
#                 # light_list[light_index].turn_on()
#                 light_list[query_data].turn_on()
#                 bot.answerCallbackQuery(query_id, text=xml_config.control.btn_on['name'] + ' ' + query_data)
#     elif user_status[user_id] == 'off':
#         light_list[query_data].turn_off()
#         bot.answerCallbackQuery(query_id, text=xml_config.control.btn_off['name'] + ' ' + query_data)



TOKEN = sys.argv[1]  # get token from command-line

print('Init telldus core')
lightcore = TelldusCore()

print('Init telepot')
bot = telepot.Bot(TOKEN)
bot.message_loop({'chat': on_chat_message,
                  'callback_query': on_callback_query})

user_status = {}
light_list = {}
names = []
groups = []

for index in range(2, len(sys.argv)):
    user_status[str(sys.argv[index])] = 'on'

# Parse from XML
xml_config = untangle.parse('config.xml')

for device in lightcore.devices():
    light_list[device.name] = device

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
main_keyboard = []

for label in light_list:
    main_keyboard.append([InlineKeyboardButton(text=label, callback_data=label)])

print('Listening ...')

while 1:
    time.sleep(10)
