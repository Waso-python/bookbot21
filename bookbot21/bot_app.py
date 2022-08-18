from email import message
from tbot import tbot_config
from bot import models
import os
from dotenv import load_dotenv
import telebot
from telebot import types


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)



bot = telebot.TeleBot(os.getenv('TOKEN'))
# var = models.User.objects.all().values_list('login')
# print(var)
# bot.send_message(message.from_user.id, models.User.objects.get(login = message.text).firstname)
# print(models.User.objects.get(login = message.text).firstname)
data:dict = {}



@bot.callback_query_handler(func=lambda call: True) #вешаем обработчик событий на нажатие всех inline-кнопок
def callback_inline(call): 
	if call.data:
		print(call.data)
		chat_id = call.from_user.id
		data[chat_id][0].campus = models.Campus.objects.get(pk = int(call.data))
		print('1 '+str(data[chat_id][0].login))
		print('2 '+str(data[chat_id][0].firstname))
		print('3 ' + str(data[chat_id][0].campus))
		print(data[chat_id][0].campus.name)
		
		# print(call['data']) #проверяем есть ли данные если да, далаем с ними что-то.


@bot.message_handler(commands=['start'])
def check(message):
	check_reg(message.json)


@bot.message_handler(content_types='text')
def anonym(message):
	check_reg(message.json)



def check_reg(message_json):
	global data
	print(len(data))
	print(message_json)
	
	chat_id = message_json['from']['id']
	
	try:
		models.User.objects.get(bot_id = chat_id)
		bot.send_message(chat_id,'register')
		return 1 # go to main menu
	except:
		if chat_id not in data:
			data[chat_id] = [models.User(), False]
			
	# user = data[chat_id][0]
	# ready = data[chat_id][1]
	
	if data[chat_id][0].login == None:
		if data[chat_id][1] == False:
			bot.send_message(chat_id,'Введи логин интры или платформы')
			data[chat_id][1] = True
		else:
			data[chat_id][0].login = message_json['text']
			# print(data[chat_id][0].login)
			data[chat_id][1] = False
	if data[chat_id][0].firstname == None and data[chat_id][0].login != None:
		if data[chat_id][1] == False:
			bot.send_message(chat_id,'Введи имя')
			data[chat_id][1] = True
		else:
			data[chat_id][0].firstname = message_json['text']
			# print(data[chat_id][0].firstname)
			data[chat_id][1] = False
	if data[chat_id][0].campus == None and data[chat_id][0].firstname != None:
		markup = types.InlineKeyboardMarkup()
		btns = []
		keys = models.Campus.objects.all().values_list('id', 'name')
		for i in keys:
			btns.append(types.InlineKeyboardButton(i[1], callback_data = i[0]))
		markup.add(*btns)
		if data[chat_id][1] == False:
			bot.send_message(chat_id, "Выбери кампус", reply_markup=markup)
			data[chat_id][1] == True
		else:
			data[chat_id][1] = False
	if data[chat_id][0].role == None and data[chat_id][0].campus != None:
		markup = types.InlineKeyboardMarkup()
		btns = []
		keys = models.role.objects.all().values_list('id', 'name')
		for i in keys:
			btns.append(types.InlineKeyboardButton(i[1], callback_data = i[0]))
		markup.add(*btns)
		if data[chat_id][1] == False:
			bot.send_message(chat_id, "Кто ты по жизни?", reply_markup=markup)
	

	print('1 '+str(data[chat_id][0].login))
	print('2 '+str(data[chat_id][0].firstname))
	print('3 ' + str(data[chat_id][0].campus))

	
	
	

bot.polling(none_stop=True, interval=0)
# print(models.User.objects.get(login = 'sdarr'))
