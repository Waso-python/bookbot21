from operator import contains
from tbot import tbot_config
from bot import models
import os
from dotenv import load_dotenv
import telebot
from telebot import types


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
	
	load_dotenv(dotenv_path)



# bot = telebot.TeleBot('')
bot = telebot.TeleBot(os.getenv('TOKEN'))
# var = models.User.objects.all().values_list('login')
# print(var)
# bot.send_message(message.from_user.id, models.User.objects.get(login = message.text).firstname)
# print(models.User.objects.get(login = message.text).firstname)
data:dict = {}

def get_buttons(model, key, *args):
	markup = types.InlineKeyboardMarkup()
	btns = []
	keys = model.objects.all().values_list(*args)
	for i in keys:
		btns.append(types.InlineKeyboardButton(i[1], callback_data = str(i[0])+'_' +key))
	markup.add(*btns)
	return markup


@bot.message_handler(content_types='text')
def anonym(message):
	check_reg(message.json)

@bot.callback_query_handler(func=lambda call: True) #вешаем обработчик событий на нажатие всех inline-кнопок
def callback_inline(call): 
	spl = str(call.data).split('_')
	chat_id = call.from_user.id
	if call.data and call.from_user.id in data:
		
		if "campus" in spl:
			
			print(call.data)
			
			
			data[chat_id][0].campus = models.Campus.objects.get(pk = int(spl[0]))
			bot.send_message(call.from_user.id, data[chat_id][0].campus)
			bot.edit_message_reply_markup(call.message.chat.id, call.message.id, types.ReplyKeyboardRemove())
			
			bot.send_message(chat_id, "Кто ты?", reply_markup=get_buttons(models.Role, 'roles', 'id', 'name'))



		if "roles" in spl:

			print(call.data)
			
			
			data[chat_id][0].role = models.Role.objects.get(pk = int(spl[0]))
			bot.edit_message_reply_markup(call.message.chat.id, call.message.id, types.ReplyKeyboardRemove())

			bot.send_message(call.from_user.id, f'Твой логин - {str(data[chat_id][0].login)}, твое имя - {str(data[chat_id][0].firstname)},кампус -  {str(data[chat_id][0].campus)},ты - {str(data[chat_id][0].role)}?')
			markup = types.InlineKeyboardMarkup()
			btn_yes = types.InlineKeyboardButton('Да', callback_data = 'reg-yes')
			btn_no = types.InlineKeyboardButton('Нет', callback_data = 'reg-no')
			markup.add(btn_yes, btn_no)
			bot.send_message(chat_id, "Все верно?", reply_markup=markup)
			
		if "reg-yes" in spl:
			#go to main menu
			data[chat_id][0].bot_id = chat_id
			data[chat_id][0].save()
			bot.edit_message_reply_markup(call.message.chat.id, call.message.id, types.ReplyKeyboardRemove())
			bot.send_message(call.message.chat.id, 'Регистрация завершена')

		print('1 ' + str(data[chat_id][0].login))
		print('2 ' + str(data[chat_id][0].firstname))
		print('3 ' + str(data[chat_id][0].campus))
		print('4 ' + str(data[chat_id][0].role))
		
		if "reg-no" in spl:
			#go to main menu
			del data[chat_id]
			bot.edit_message_reply_markup(call.message.chat.id, call.message.id, types.ReplyKeyboardRemove())
			# bot.send_message(call.message.chat.id, 'Регистрация завершена')

	if "del-yes" in spl:
		#go to main menu
		models.User.objects.get(bot_id = chat_id).delete()
		del data[chat_id]
		bot.edit_message_reply_markup(call.message.chat.id, call.message.id, types.ReplyKeyboardRemove())
		bot.send_message(call.message.chat.id, 'User deleted')

	if "del-no" in spl:
		#go to main menu
		bot.edit_message_reply_markup(call.message.chat.id, call.message.id, types.ReplyKeyboardRemove())
			
		
		# print(call['data']) #проверяем есть ли данные если да, далаем с ними что-то.


@bot.message_handler(commands=['start'])
def check(message):
	check_reg(message.json)

@bot.message_handler(commands=['delete'])
def check(message):
	
	chat_id = message.json['from']['id']
	try:
		models.User.objects.get(bot_id = chat_id)
		markup = types.InlineKeyboardMarkup()
		btn_yes = types.InlineKeyboardButton('Да', callback_data = 'del-yes')
		btn_no = types.InlineKeyboardButton('Нет', callback_data = 'del-no')
		markup.add(btn_yes, btn_no)
		bot.send_message(message.chat.id, "Удалить данные о Вас?", reply_markup=markup)
	except:
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
		# markup = types.InlineKeyboardMarkup()
		# btns = []
		# keys = models.Campus.objects.all().values_list('id', 'name')
		
		# for i in keys:
		# 	btns.append(types.InlineKeyboardButton(i[1], callback_data = str(i[0])+'_campus'))
		# markup.add(*btns)
		if data[chat_id][1] == False:
			bot.send_message(chat_id, "Выбери кампус", reply_markup=get_buttons(models.Campus, 'campus', 'id', 'name'))
			data[chat_id][1] == True
		else:
			data[chat_id][1] = False
	# if data[chat_id][0].role == None and data[chat_id][0].campus != None:
		# markup = types.InlineKeyboardMarkup()
		# btns = []
		# keys = models.Role.objects.all().values_list('id', 'name')
		# for i in keys:
		# 	btns.append(types.InlineKeyboardButton(i[1], callback_data = str(i[0])+'_roles'))
		# markup.add(*btns)
		# if data[chat_id][1] == False:
		# 	bot.send_message(chat_id, "Кто ты по жизни?", reply_markup=get_buttons(models.Role, 'id', 'name'))
	

	print('1 '+str(data[chat_id][0].login))
	print('2 '+str(data[chat_id][0].firstname))
	print('3 ' + str(data[chat_id][0].campus))

	
	
	

bot.polling(none_stop=True, interval=0)
# print(models.User.objects.get(login = 'sdarr'))
