#!/home/pi/Documents/telepython/.env/bin/python3

import time
import telepot
import RPi.GPIO as GPIO
from subprocess import call
import cv2
from picamera import PiCamera
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

relay = 12
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7,GPIO.IN)
GPIO.setup(relay,GPIO.OUT)
GPIO.setup(37,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(relay, 0)
intruder = False
enabled = False
pirtake = False
standby = 0
path = '/home/pi/Documents/telepython/media'


def handle(msg):
    global enabled
    global pirtake
    global intruder

    command = msg['text'] 
    from_id = msg['from']['id'] #id telegram
    print ('Got command: %s' % command)
    
    if from_id == 809596619: # mencocokan id telegram

        keyboard = ReplyKeyboardMarkup(keyboard=[['start', 'status', 'help'], ['foto', 'buka','rekam'], ['startsensor', 'stopsensor']])
        bot.sendMessage(chat_id, 'Siap tuan', reply_markup=keyboard)

        if command.lower() == "start": #banner selamat datang
            bot.sendMessage(chat_id, 'Selamat datang di kamera keamanan Ketuk Pintu. /help untuk melihat beberapa perintah')
        
        elif command.lower() == "help": #bantuan
            bot.sendMessage(chat_id, '''Berikut perintah yang bisa digunakan pada bot ini : \n- start : Info bot ini \n- status : Cek status sensor\n- help : bantuan perintah pada bot \n- foto : mengambil gambar \n- buka : membuka pintu(aktifkan relay) \n- rekam : merekam video selama 5 detik \n- startsensor : menyalakan sensor \n- stopsensor : mematikan sensor''')
            bot.sendMessage(chat_id, 'kamera akan mengambil gambar ketika ada gerakan pada sensor melebihi 3 detik')
        
        elif command.lower() == "foto": #mengambil foto saat ini
            camera = cv2.VideoCapture(0)
            return_value, image = camera.read()
            foto = path + "/foto/foto_" + (time.strftime("%d%b%y_%H%M%S"))
            cv2.imwrite(foto + '.jpg', image)
            print('capturing')
            del(camera)
            inf = open(foto + '.jpg', 'rb')
            caption = 'Foto pada '+time.strftime("%H:%M:%S %d-%m-%Y")
            bot.sendPhoto(chat_id,inf,caption)
        
        elif command.lower() == "rekam": #merekam situasi selama 10 detik     
            waktu = 5
            with PiCamera() as camera:
                camera.resolution = (640, 480)
                filename = path + "/video/video_" + (time.strftime("%d%b%y_%H%M%S"))
                camera.start_recording(filename + '.h264')
                camera.wait_recording(waktu)
                camera.stop_recording()
                command = "MP4Box -add " + filename + '.h264' + " " + filename + '.mp4'
                print(command)
                call([command], shell=True)
                bot.sendVideo(chat_id, video = open(filename + '.mp4', 'rb'))
        
        elif command.lower() == "buka": #membuka pintu
            bot.sendMessage(chat_id,text="pintu dibuka")
            GPIO.output(relay, 1)
            time.sleep(4)
            GPIO.output(relay, 0)

        elif command.lower() == "startsensor": #menyalakan sensor
            if pirtake == True:
                bot.sendMessage(chat_id,text="Sensor dalam keadaan menyala")
            else:
                pirtake = True
                bot.sendMessage(chat_id,text="Sensor menyala")

        elif command.lower() == "stopsensor": #mematikan sensor
            if pirtake == True:
                pirtake = False
                bot.sendMessage(chat_id,text="Sensor dimatikan")
            else:
                pirtake = False
                bot.sendMessage(chat_id,text="Sensor dalam keadaan mati")
        #BREAK HERE
        elif command.lower() == "status": #melihat status sensor
            if pirtake == 1:
                bot.sendMessage(chat_id, 'Sensor aktif')
            
            else:
                bot.sendMessage(chat_id, 'Sensor mati')
            
        else:
            bot.sendMessage(chat_id,text="perintah invalid") #respons saat tidak ada perintah yang cocok
            

    else: 
        bot.sendMessage(from_id,text="Mohon maaf,tidak bisa berinteraksi untuk saat ini") #respons ketika user lain mencoba menggunakan bot
        print("intruder : "+str(from_id))
        bot.sendMessage(chat_id,text="Seseorang mencoba untuk berinteraksi dengan bot ini. \nid : "+str(from_id)+"\nperintah : "+ command) #mengirim laporan kepada user valid

chat_id = #masukan id telegram
bot = telepot.Bot('') #token bot ketuk_pintu
bot.message_loop(handle)
print('I am listening...')
bot.sendMessage(chat_id,text="Bot aktif") #pesan yang dikirim saat skrip python ini aktif

while 1:
    pirvalue = GPIO.input(7)
    tombol = GPIO.input(37)
#     if tombol == 0:
# #bot.sendMessage(chat_id,text="Pintu dibuka")
#         GPIO.output(relay, 1)
#         time.sleep(4)
#         GPIO.output(relay, 0)        
        
    if pirvalue == 1 and pirtake == True: #sensor diaktifkan dan pir menerima sinyal
        intruder = True
        if standby == 1: #status sensor mendeteksi sesuatu
            bot.sendMessage(chat_id, 'Sensor mendeteksi sesuatu!')
        
        if standby >= 3: #saat sensor keadaan HIGH selama 3 detik akan memfoto objek di depan
            camera = cv2.VideoCapture(0)
            return_value, image = camera.read()
            motion = path + "/sensor/motion_" + (time.strftime("%d%b%y_%H%M%S"))
            cv2.imwrite(motion + '.jpg', image)
            print('capturing')
            del(camera)
            inf = open(motion + '.jpg', 'rb')
            captionpir = 'Terjadi gerakan pada '+time.strftime("%H:%M:%S %d-%m-%Y")
            bot.sendPhoto(chat_id,inf,captionpir)
            standby = 0

        else: #sensor dalam kondisi high namun belum memenuhi syarat
            print(standby)
            standby += 1
        

    
    if pirvalue == 0: #jika sensor tidak mendeteksi apapun status intruder menjadi low
        intruder = False
        standby = 0
    time.sleep(1)


