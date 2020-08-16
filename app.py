import telebot
import markups
import config
import google_dict
import data_base

bot = telebot.TeleBot(config.bot_token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	db = data_base.DataBase()
	user = db.findUser(str(message.from_user.id))
	if user is None:
		db.insertUser(str(message.from_user.id), "en")
	else:
		db.updateLanguage(str(message.from_user.id), "en")
	msg = bot.send_message(message.chat.id, "I can explain to you any word.\nPlease select your preferred language:", reply_markup=markups.language_markup)

@bot.message_handler(commands=['help'])
def get_info(message):
	msg = "Hello, my name is *MeanIt*! I am here for you to help with new words! Just add the word down here and I will show you the meanings!"
	msg += "\n\nYou can control me by sending these commands:\n\n"
	msg += "*Change language\n*"
	msg += "/english - set current language English\n"
	msg += "/french - set current language French\n"
	msg += "/german - set current language German\n\n"
	msg += "/help - get help on using the bot\n"
	bot.send_message(message.chat.id, msg, parse_mode='Markdown')


OFFSET = 127462 - ord('A')

def flag(code):
	code = code.upper()
	return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)

@bot.callback_query_handler(func = lambda m: True)
def setLanguage(call):
	if call.data == "en":
		setEnglishLanguage(call.message)
	elif call.data == "fr":
		setFrenchLanguage(call.message)
	elif call.data == "de":
		setGermanLanguage(call.message)

@bot.message_handler(commands=['english'])
def setEnglishLanguage(message):
	db = data_base.DataBase()
	user = db.findUser(str(message.from_user.id))
	answer = "Now I know English" + flag('gb') + "."
	if user is None:
		db.insertUser(str(message.from_user.id), "en")
	elif user[1] != "en":
		db.updateLanguage(str(message.from_user.id), "en")
	else:
		answer = "I already know English" + flag('gb') + "."
	msg = bot.send_message(message.chat.id, answer)

@bot.message_handler(commands=['french'])
def setFrenchLanguage(message):
	db = data_base.DataBase()
	user = db.findUser(str(message.from_user.id))
	answer = "Maintenant je connais le français" + flag('fr') + "."
	if user is None:
		db.insertUser(str(message.from_user.id), "fr")
	elif user[1] != "fr":
		db.updateLanguage(str(message.from_user.id), "fr")
	else:
		answer = "Je connais déjà le français" + flag('fr') + "."
	msg = bot.send_message(message.chat.id, answer)

@bot.message_handler(commands=['german'])
def setGermanLanguage(message):
	db = data_base.DataBase()
	user = db.findUser(str(message.from_user.id))
	answer = "Jetzt kenne ich die Deutsche Sprache" + flag('de') + "."
	if user is None:
		db.insertUser(str(message.from_user.id), "de")
	elif user[1] != "de":
		db.updateLanguage(str(message.from_user.id), "de")
	else:
		answer = "Ich kenne schon Deutsch" + flag('de') + "."
	msg = bot.send_message(message.chat.id, answer)

@bot.message_handler(content_types=['text'])
def getWord(message):
	db = data_base.DataBase()
	user = db.findUser(str(message.from_user.id))
	data = google_dict.find_word(user[1], message.text)
	if (data.status_code == 200):
		createAnswer(data.json(), message)

def createAnswer(data_list, message):
	audio = None
	for data in data_list:
		word = data['word'].capitalize()
		answer = f"*{word}*\n\n"
		answer += "*Pronunciation*:"
		for phonetics in data["phonetics"]:
			for (key, value) in phonetics.items():
				if key == 'audio':
					audio = value
				else:
					key = key.capitalize()
					answer += f"\n{key}: {value}"
		answer += "\n\n"
		answer += "*Meaning*:\n"
		for i, (key, value) in enumerate(data['meaning'].items()):
			key = key.capitalize()
			answer += f"_{key}_:\n"
			for j, word in enumerate(value):
				answer += f"{i + 1}.{j + 1}"
				for k, v in word.items():
					k = k.capitalize()
					answer += f" *{k}*: {v}"
				answer += "\n"
			answer += "\n"
		answer += "\n"
		bot.send_message(message.chat.id, answer, parse_mode='Markdown')
		if audio is not None:
			bot.send_audio(message.chat.id, audio)


if __name__ == '__main__':
	bot.polling(none_stop=True, interval=0)
