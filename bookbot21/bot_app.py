from operator import contains
from datetime import datetime, timedelta
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

data:dict = {}
book_data:dict = {}

@bot.message_handler(commands=['delete'])
def delete(message):
	chat_id = message.json['from']['id']
	try:
		models.User.objects.get(bot_id = chat_id)
		markup = types.InlineKeyboardMarkup()
		btn_yes = types.InlineKeyboardButton('Да', callback_data = 'del-yes')
		btn_no = types.InlineKeyboardButton('Нет', callback_data = 'del-no')
		markup.add(btn_yes, btn_no)
		bot.send_message(message.chat.id, "Удалить данные о Вас?", reply_markup=markup)
	except Exception as e:
		print('delete', str(e))
		check_reg(message)

@bot.message_handler(commands=['self'])
def get_user_info(message):
	try:
		user = models.User.objects.get(bot_id=message.json['from']['id'])
		bot.send_message(message.json['from']['id'], f"Имя - {user.firstname}\nЛогин - {user.login}\nКампус - {user.campus.name}\n Роль - {user.role.name}"  )
	except Exception as e:
		print('SELF' ,e)
		bot.send_message(message.json['from']['id'], 'В системе нет данных о вас! Пожалуйста зарегистрируйтесь')


def del_message(chat_id, *args):
	for message_id in args:
		if message_id:
			bot.delete_message(chat_id, message_id.json['message_id'])
			data[chat_id][2] = 0


def get_buttons(model, key, *args, **kwargs):
	markup = types.InlineKeyboardMarkup()
	btns = []
	
	if 'req' in kwargs:
		keys = model.objects.filter(is_admin = False).values_list(*args)
	elif 'type_id' in kwargs:
		keys = model.objects.filter(object_type_id = kwargs['type_id']).values_list(*args)
	elif 'days' in kwargs:
		date_now = datetime.now().date()
		keys = []
		for i in range(30):
			keys.append([str(date_now) ,str(date_now)])
			date_now += timedelta(days=1)
	else:
		keys = model.objects.all().values_list(*args)
	for i in keys:
		btns.append(types.InlineKeyboardButton(i[1], callback_data = str(i[0])+'_' +key))
	markup.add(*btns)
	return markup


@bot.callback_query_handler(func=lambda call: True) #вешаем обработчик событий на нажатие всех inline-кнопок
def callback_inline(call):
	print(call.data)
	spl = str(call.data).split('_')
	chat_id = call.from_user.id

	if call.data and call.from_user.id in data:
		del_message(chat_id, data[chat_id][2])
		if "campus" in spl:
			print(call.data)
			data[chat_id][0].campus = models.Campus.objects.get(pk = int(spl[0]))
			data[chat_id][2] = bot.send_message(chat_id, "Кто ты?", reply_markup=get_buttons(models.Role, 'roles', 'id', 'name', req='roles'))

		if "roles" in spl:
			print(call.data)
			data[chat_id][0].role = models.Role.objects.get(pk = int(spl[0]))
			markup = types.InlineKeyboardMarkup()
			btn_yes = types.InlineKeyboardButton('Да', callback_data = 'reg-yes')
			btn_no = types.InlineKeyboardButton('Нет', callback_data = 'reg-no')
			markup.add(btn_yes, btn_no)
			data[chat_id][2] = bot.send_message(call.from_user.id, f'Твой логин - {str(data[chat_id][0].login)}\nТвое имя - {str(data[chat_id][0].firstname)}\nКампус -  {str(data[chat_id][0].campus)}\nТы - {str(data[chat_id][0].role)}\nВсе Верно?', reply_markup=markup)
			
		print('1 ' + str(data[chat_id][0].login))
		print('2 ' + str(data[chat_id][0].firstname))
		print('3 ' + str(data[chat_id][0].campus))
		print('4 ' + str(data[chat_id][0].role))

		if "reg-yes" in spl:
			#go to main menu
			data[chat_id][0].bot_id = chat_id
			data[chat_id][0].save()
			# bot.edit_message_reply_markup(call.message.chat.id, call.message.id, types.ReplyKeyboardRemove())
			del data[chat_id]
			bot.send_message(call.message.chat.id, 'Регистрация завершена')
		
		if "reg-no" in spl:
			del data[chat_id]



	if "del-yes" in spl:
		#go to main menu
		models.User.objects.get(bot_id = chat_id).delete()
		bot.edit_message_reply_markup(call.message.chat.id, call.message.id, types.ReplyKeyboardRemove())
		bot.send_message(call.message.chat.id, 'User deleted')

	if "del-no" in spl:
		bot.edit_message_reply_markup(call.message.chat.id, call.message.id, types.ReplyKeyboardRemove())
	
	if "types" in spl:
		print(int(spl[0]))
		book_data[chat_id][2] = bot.send_message(chat_id, 'Выберите объект', reply_markup=get_buttons(models.SchoolObject, 'objects', 'id', 'object_name', type_id = int(spl[0])))

	if "objects" in spl:
		print(int(spl[0]))
		book_data[chat_id][0].school_object_id = int(spl[0])
		book_data[chat_id][2] = bot.send_message(chat_id, 'Выберите дату', reply_markup=get_buttons(None, 'days', days = None))	
	
	if "days" in spl:
		print(int(spl[0]))
		book_data[chat_id][0].school_object_id = int(spl[0])
		book_data[chat_id][2] = bot.send_message(chat_id, 'Выберите дату', reply_markup=get_buttons(None, 'days', days = None))	

	


@bot.message_handler(commands=['start'])
def check(message):
	check_reg(message)

@bot.message_handler(content_types='text')
def check_reg(message):
	global data
	print(message.json)
	
	chat_id = message.json['from']['id']
	try:
		models.User.objects.get(bot_id = chat_id)
		bot.send_message(chat_id,'Вы зарегистрированы')
		main_menu(message) # go to main menu
		return
	except Exception as e:
		print('EXEPTION', e)
		if chat_id not in data:
			data[chat_id] = [models.User(), False, 0]
			
	if data[chat_id][0].campus == None:
		del_message(chat_id, data[chat_id][2], message)
	else:
		del_message(chat_id, message)
	
	if data[chat_id][0].login == None:
		if data[chat_id][1] == False:
			data[chat_id][2] = bot.send_message(chat_id,'В системе нет данных о вас! Пожалуйста зарегистрируйтесь')
			data[chat_id][2] = bot.send_message(chat_id,'Введи логин интры или платформы')
			data[chat_id][1] = True
		else:
			data[chat_id][0].login = message.json['text']
			# print(data[chat_id][0].login)
			data[chat_id][1] = False
	if data[chat_id][0].firstname == None and data[chat_id][0].login != None:
		if data[chat_id][1] == False:
			data[chat_id][2] = bot.send_message(chat_id,'Введи имя')
			data[chat_id][1] = True
		else:
			data[chat_id][0].firstname = message.json['text']
			# print(data[chat_id][0].firstname)
			data[chat_id][1] = False
	if data[chat_id][0].campus == None and data[chat_id][0].firstname != None:
		if data[chat_id][1] == False:
			data[chat_id][2] = bot.send_message(chat_id, "Выбери кампус", reply_markup=get_buttons(models.Campus, 'campus', 'id', 'name'))
			data[chat_id][1] == True
		else:
			data[chat_id][1] = False

	print('1 '+str(data[chat_id][0].login))
	print('2 '+str(data[chat_id][0].firstname))
	print('3 '+str(data[chat_id][0].campus))

#////////////////////////////////////////////////////////////////////////////////////////////////////

def main_menu(message):
	
	# ObjectType
	global book_data
	print(message.json)
	
	chat_id = message.json['from']['id']
	if chat_id not in book_data:
		book_data[chat_id] = [models.Booking(), False, None]
	
	# if book_data[chat_id][0].campus == None:
	# 	del_message(chat_id, book_data[chat_id][2], message)
	# else:
	# 	del_message(chat_id, message)
	
	if book_data[chat_id][0].school_object_id == None:
		book_data[chat_id][2] = bot.send_message(chat_id, 'Выберите типы объектов', reply_markup=get_buttons(models.ObjectType, 'types', 'id', 'name'))
		
	
	
	
	return	



	# if book_data[chat_id][0].firstname == None and book_data[chat_id][0].login != None:
	# 	if book_data[chat_id][1] == False:
	# 		book_data[chat_id][2] = bot.send_message(chat_id,'Введи имя')
	# 		book_data[chat_id][1] = True
	# 	else:
	# 		book_data[chat_id][0].firstname = message.json['text']
	# 		# print(book_data[chat_id][0].firstname)
	# 		book_data[chat_id][1] = False
	# if book_data[chat_id][0].campus == None and book_data[chat_id][0].firstname != None:
	# 	if book_data[chat_id][1] == False:
	# 		book_data[chat_id][2] = bot.send_message(chat_id, "Выбери кампус", reply_markup=get_buttons(models.Campus, 'campus', 'id', 'name'))
	# 		book_data[chat_id][1] == True
	# 	else:
	# 		book_data[chat_id][1] = False

	# print('1 '+str(book_data[chat_id][0].login))
	# print('2 '+str(book_data[chat_id][0].firstname))
	# print('3 '+str(book_data[chat_id][0].campus))








bot.polling(none_stop=True, interval=0)
# print(models.User.objects.get(login = 'sdarr'))
