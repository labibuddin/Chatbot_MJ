import telebot
from telebot import types
import pandas as pd
import mysql.connector
import os

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='',
    database='masjid_jogokariyan'
)
# print(mydb)
sql = mydb.cursor()

API_TOKEN = 'API DARI BOTFATHER TELEGRAM'

bot = telebot.TeleBot(API_TOKEN)

user_dict = {}


class User:
    def __init__(self, name):
        self.name = name
        self.asal = None
        self.keperluan = None
        self.jumlah_rombongan = None
        self.jenis_kendaraan = None
        self.jumlah_kendaraan = None


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.reply_to(message, """\
Assalamu'alaikum Akhiy/Ukhtiy.
Selamat Datang Tamu Studi Banding Masjid Jogokariyan
Siapa nama Anda? (mewakili rombongan atau pun pribadi)
""")
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        msg = bot.reply_to(message, 'Dimanakah daerah asal Anda?')
        bot.register_next_step_handler(msg, process_asal_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_asal_step(message):
    try:
        chat_id = message.chat.id
        asal = message.text
        user = user_dict[chat_id]
        user.asal = asal
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Studi Banding', 'Solat Berjamaah')        
        msg = bot.reply_to(message, 'Apa keperluan anda datang ke Masjid Jogokariyan?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_keperluan_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_keperluan_step(message):
    try:
        chat_id = message.chat.id
        keperluan = message.text
        user = user_dict[chat_id]
        if (keperluan == u'Studi Banding') or (keperluan == u'Solat Berjamaah'):
            user.keperluan = keperluan
        else:
            raise Exception("Unknown keperluan")
        msg = bot.reply_to(message, 'Berapa jumlah rombongan?')
        bot.register_next_step_handler(msg, process_jmlhrombongan_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_jmlhrombongan_step(message):
	try:
		chat_id = message.chat.id
		jumlah_rombongan = message.text
		if not jumlah_rombongan.isdigit():
			msg = bot.reply_to(message, 'Jumlah rombongan harus berupa angka')
			bot.register_next_step_handler(msg, process_jmlhrombongan_step)
			return
		user = user_dict[chat_id]
		user.jumlah_rombongan = jumlah_rombongan
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
		markup.add('Sepeda Motor', 'Mobil', 'Bus Kecil', 'Bus Besar')
		msg = bot.reply_to(message, 'Apa jenis kendaraan Anda dan rombongan?', reply_markup=markup)
		bot.register_next_step_handler(msg, process_jenis_kendaraan_step)
	except Exception as e:
		bot.reply_to(message, 'oooops')


def process_jenis_kendaraan_step(message):
    try:
        chat_id = message.chat.id
        jenis_kendaraan = message.text
        user = user_dict[chat_id]
        if (jenis_kendaraan == u'Sepeda Motor') or (jenis_kendaraan == u'Mobil') or (jenis_kendaraan == u'Bus Kecil') or (jenis_kendaraan == u'Bus Besar'):
            user.jenis_kendaraan = jenis_kendaraan
        else:
            raise Exception("Unknown jenis kendaraan")
        msg = bot.reply_to(message, 'Berapa jumlah kendaraan?')
        bot.register_next_step_handler(msg, process_jmlhkendaraan_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')
        

def process_jmlhkendaraan_step(message):
    try:
        chat_id = message.chat.id
        jumlah_kendaraan = message.text
        if not jumlah_kendaraan.isdigit():
            msg = bot.reply_to(message, 'Jumlah kendaraan harus berupa angka')
            bot.register_next_step_handler(msg, process_jmlhkendaraan_step)
            return
        user = user_dict[chat_id]
        user.jumlah_kendaraan = jumlah_kendaraan 		
        bot.send_message(chat_id, 'Ini data Anda ' + user.name + '\n Asal: ' + str(user.asal) + '\n keperluan: ' + user.keperluan + '\n Jumlah rombongan: ' + str(user.jumlah_rombongan) + '\n Jenis kendaraan: ' + str(user.jenis_kendaraan) + '\n Jumlah kendaraan: ' + str(user.jumlah_kendaraan))
                
        val = (user.name, user.asal, user.keperluan, user.jumlah_rombongan, user.jenis_kendaraan, user.jumlah_kendaraan)
        sql.execute("""INSERT INTO data_tamuv2 (Nama, Asal, Keperluan, Jumlah_Rombongan, Jenis_Kendaraan, Jumlah_Kendaraan) VALUES ('%s','%s','%s','%s','%s','%s')"""%(val))
        mydb.commit()
        bot.reply_to(message, 'data berhasil diinput')
        user.name, user.asal, user.keperluan, user.jumlah_rombongan, user.jenis_kendaraan, user.jumlah_kendaraan = '','','','','',''

    except Exception as e:
        bot.reply_to(message, 'oooops')

@bot.message_handler(commands=['daftarTamu'])
def tampilkan(message):
    sql.execute("""SELECT * FROM data_tamuv2""")
    hasil_sql = sql.fetchall()
    #print(hasil_sql)
    #mydb.commit()
    
    pesan_balasan = ''
    for x in hasil_sql:
        pesan_balasan = pesan_balasan + str(x) + '\n'
    bot.reply_to(message, pesan_balasan)
    
                
bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()

bot.infinity_polling()
