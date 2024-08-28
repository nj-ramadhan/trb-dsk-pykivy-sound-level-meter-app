from cv2 import DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMINGLUT
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivymd.font_definitions import theme_font_styles
from kivymd.uix.datatables import MDDataTable
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.app import MDApp
from kivymd import fonts_path
from kivy.metrics import dp, sp
from kivymd.toast import toast
import numpy as np
import time
import os
import pyaudio
from math import log10
import audioop  
import mysql.connector

colors = {
    "Red": {
        "A200": "#FF2A2A",
        "A500": "#FF8080",
        "A700": "#FFD5D5",
    },

    "Gray": {
        "200": "#CCCCCC",
        "500": "#ECECEC",
        "700": "#F9F9F9",
    },

    "Blue": {
        "200": "#4471C4",
        "500": "#5885D8",
        "700": "#6C99EC",
    },

    "Green": {
        "200": "#2CA02C", #41cd93
        "500": "#2DB97F",
        "700": "#AAA5AA",
    },

    "Yellow": {
        "200": "#ffD42A",
        "500": "#ffE680",
        "700": "#fff6D5",
    },

    "Light": {
        "StatusBar": "E0E0E0",
        "AppBar": "#202020",
        "Background": "#EEEEEE",
        "CardsDialogs": "#FFFFFF",
        "FlatButtonDown": "#CCCCCC",
    },

    "Dark": {
        "StatusBar": "101010",
        "AppBar": "#E0E0E0",
        "Background": "#111111",
        "CardsDialogs": "#222222",
        "FlatButtonDown": "#DDDDDD",
    },
}

VENDOR_ID = 0x04F2
PRODUCT_ID = 0xB6A8
SER_BAUD = 9600
SER_PORT = "COM9"
SER_DTR = 1
SER_DSR = True
SER_TIMEOUT = 1

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 0.8
WIDTH = 2

sound_rms = 1
flag_device = False
flag_conn_stat = False
flag_play = False

dt_sound = 45.5
dt_no_antrian = ""
dt_no_reg = ""
dt_no_uji = ""
dt_nama = ""
dt_jenis_kendaraan = ""
dt_status = ""

count_starting = 3
count_get_data = 10

p = pyaudio.PyAudio() # start the PyAudio class
stream=p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,
        frames_per_buffer=CHUNK) #uses default input device

class ScreenMain(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenMain, self).__init__(**kwargs)
        global mydb, db_antrian

        try:
            mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_trb"
            )

            db_antrian = np.array([["001", "002", "003"],
                                    ["PB123XY","PB234YZ","PB345XZ"],
                                    [ "Z1234SA", "Z2345SP", "Z3456SM"],
                                    [ "Budi", "Ani", "Udin"],
                                    [ "Pick-Up", "Pribadi", "travel"],
                                    [ "0", "0", "1"]])
        except Exception as e:
            toast_msg = f'error initiate Database: {e}'
            toast(toast_msg)   
                    
        Clock.schedule_once(self.delayed_init, 2)
        
    def delayed_init(self, dt):
        Clock.schedule_interval(self.regular_update_display, 1)
        layout = self.ids.layout_table
        
        self.data_tables = MDDataTable(
            use_pagination=True,
            pagination_menu_pos="auto",
            rows_num=10,
            column_data=[
                ("No.", dp(10), self.sort_on_num),
                ("Antrian", dp(20)),
                ("No. Reg", dp(25)),
                ("No. Uji", dp(35)),
                ("Nama", dp(35)),
                ("Jenis", dp(50)),
                ("Status", dp(20)),
            ],
        )
        self.data_tables.bind(on_row_press=self.on_row_press)
        layout.add_widget(self.data_tables)
        self.exec_reload_table()

    def sort_on_num(self, data):
        try:
            return zip(*sorted(enumerate(data),key=lambda l: l[0][0]))
        except:
            toast("Error sorting data")

    def on_row_press(self, table, row):
        global dt_no_antrian, dt_no_reg, dt_no_uji, dt_nama, dt_jenis_kendaraan, dt_status

        try:
            start_index, end_index  = row.table.recycle_data[row.index]["range"]
            dt_no_antrian           = row.table.recycle_data[start_index + 1]["text"]
            dt_no_reg               = row.table.recycle_data[start_index + 2]["text"]
            dt_no_uji               = row.table.recycle_data[start_index + 3]["text"]
            dt_nama                 = row.table.recycle_data[start_index + 4]["text"]
            dt_jenis_kendaraan      = row.table.recycle_data[start_index + 5]["text"]
            dt_status               = row.table.recycle_data[start_index + 6]["text"]

        except Exception as e:
            toast_msg = f'error update table: {e}'
            toast(toast_msg)   

    def regular_update_display(self, dt):
        global flag_conn_stat, flag_device
        global dt_sound, count_starting, count_get_data
        global dt_no_antrian, dt_no_reg, dt_no_uji, dt_nama, dt_jenis_kendaraan, dt_status

        try:
            screen_counter = self.screen_manager.get_screen('screen_counter')
            self.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            self.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_counter.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_counter.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))

            self.ids.lb_no_antrian.text = str(dt_no_antrian)
            self.ids.lb_no_reg.text = str(dt_no_reg)
            self.ids.lb_no_uji.text = str(dt_no_uji)
            self.ids.lb_nama.text = str(dt_nama)
            self.ids.lb_jenis_kendaraan.text = str(dt_jenis_kendaraan)
            # self.ids.lb_status.text = str(dt_status)

            screen_counter.ids.lb_no_antrian.text = str(dt_no_antrian)
            screen_counter.ids.lb_no_reg.text = str(dt_no_reg)
            screen_counter.ids.lb_no_uji.text = str(dt_no_uji)
            screen_counter.ids.lb_nama.text = str(dt_nama)
            screen_counter.ids.lb_jenis_kendaraan.text = str(dt_jenis_kendaraan)
            # screen_counter.ids.lb_status.text = str(dt_status)

            if(dt_status == "Belum Tes"):
                self.ids.bt_start.disabled = False
            else:
                self.ids.bt_start.disabled = True

            if(not flag_play):
                screen_counter.ids.bt_save.md_bg_color = colors['Green']['200']
                screen_counter.ids.bt_save.disabled = False
                screen_counter.ids.bt_reload.md_bg_color = colors['Red']['A200']
                screen_counter.ids.bt_reload.disabled = False
            else:
                screen_counter.ids.bt_reload.disabled = True
                screen_counter.ids.bt_save.disabled = True

            if(not flag_conn_stat):
                self.ids.lb_comm.color = colors['Red']['A200']
                self.ids.lb_comm.text = 'Status : Disconnected'
                screen_counter.ids.lb_comm.color = colors['Red']['A200']
                screen_counter.ids.lb_comm.text = 'Status : Disconnected'

            else:
                # self.ids.lb_comm.color = colors['Blue']['200']
                self.ids.lb_comm.text = 'Status : Connected'
                # screen_counter.ids.lb_comm.color = colors['Blue']['200']
                screen_counter.ids.lb_comm.text = 'Status : Connected'
                if(not flag_device):
                    toast('Device successfully connected')

            if(count_starting <= 0):
                screen_counter.ids.lb_test_subtitle.text = "HASIL PENGUKURAN"
                screen_counter.ids.lb_sound.text = str(np.round(dt_sound, 2))
                screen_counter.ids.lb_info.text = "Ambang Batas Kebisingan adalah 83 dB hingga 118 dB"
                                               
            elif(count_starting > 0):
                if(flag_play):
                    screen_counter.ids.lb_test_subtitle.text = "MEMULAI PENGUKURAN"
                    screen_counter.ids.lb_sound.text = str(count_starting)
                    screen_counter.ids.lb_info.text = "Silahkan Nyalakan Klakson Kendaraan"


            if(dt_sound >= 83 and dt_sound <= 118):
                screen_counter.ids.lb_info.text = "Kendaraan Anda Memiliki Tingkat Kebisingan Suara Klakson Dalam Range Ambang Batas"
            elif(dt_sound < 83):
                screen_counter.ids.lb_info.text = "Kendaraan Anda Memiliki Tingkat Kebisingan Suara Klakson Dibawah Ambang Batas"
            elif(dt_sound > 118):
                screen_counter.ids.lb_info.text = "Kendaraan Anda Memiliki Tingkat Kebisingan Suara Klakson Diatas Ambang Batas"

            if(count_get_data <= 0):
                screen_counter.ids.lb_test_result.size_hint_y = 0.25
                if(dt_sound >= 83 and dt_sound <= 118):
                    screen_counter.ids.lb_test_result.md_bg_color = colors['Green']['200']
                    screen_counter.ids.lb_test_result.text = "LULUS"
                    dt_status = "Lulus"
                    screen_counter.ids.lb_test_result.text_color = colors['Green']['700']
                else:
                    screen_counter.ids.lb_test_result.md_bg_color = colors['Red']['A200']
                    screen_counter.ids.lb_test_result.text = "TIDAK LULUS"
                    dt_status = "Tidak Lulus"
                    screen_counter.ids.lb_test_result.text_color = colors['Red']['A700']

            elif(count_get_data > 0):
                    screen_counter.ids.lb_test_result.md_bg_color = colors['Gray']['700']
                    # screen_counter.ids.lb_test_result.size_hint_y = None
                    # screen_counter.ids.lb_test_result.height = dp(0)
                    screen_counter.ids.lb_test_result.text = ""

        except Exception as e:
            toast_msg = f'error update display: {e}'
            toast(toast_msg)                

    def regular_get_data(self, dt):
        global flag_play
        global dt_sound
        global sound_rms
        global count_starting, count_get_data
        try:
            if(count_starting > 0):
                count_starting -= 1              

            if(count_get_data > 0):
                count_get_data -= 1
                
            elif(count_get_data <= 0):
                flag_play = False
                Clock.unschedule(self.regular_get_data)

            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                sound_rms = audioop.rms(stream.read(CHUNK), WIDTH) / 32767
                # db = 20 * log10(sound_rms) #0.033, 0.109, 0.347
                # mod = 20 * log10(rms * 32767)
                amplitude = sound_rms * 1600000
                # mod_Amp = amp * 1518727
                dB = 20 * log10(amplitude)
                dBA = dB if sound_rms > 0.03 else dB - (((0.3 - sound_rms) * 15 ) ** 2 )
                # mod_dB = 20 * log10(sound_rms) + 93.37
                # print(f"RMS: {sound_rms} DB: {db} mod_Amp: {mod_Amp} mod_dB: {mod_dB}") 
                dt_sound = dBA
                
        except Exception as e:
            toast_msg = f'error get data: {e}'
            print(toast_msg) 

    def exec_reload_table(self):
        global mydb, db_antrian
        try:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT noantrian, nopol, nouji, user, idjeniskendaraan, sts FROM tb_cekident")
            myresult = mycursor.fetchall()
            db_antrian = np.array(myresult).T
            print(db_antrian)
            self.data_tables.row_data=[(f"{i+1}", f"{db_antrian[0, i]}", f"{db_antrian[1, i]}", f"{db_antrian[2, i]}", f"{db_antrian[3, i]}" ,f"{db_antrian[4, i]}", 
                                        'Belum Tes' if (int(db_antrian[5, i]) == 0) else ('Lulus' if (int(db_antrian[5, i]) == 1) else 'Tidak Lulus')) 
                                        for i in range(len(db_antrian[0]))]

        except Exception as e:
            toast_msg = f'error reload table: {e}'
            print(toast_msg)

    def exec_start(self):
        global flag_play, stream, p

        if(not flag_play):
            stream.start_stream()
            Clock.schedule_interval(self.regular_get_data, 1)
            self.open_screen_counter()
            flag_play = True

            # stream.close()
            # p.terminate()  

    def open_screen_counter(self):
        self.screen_manager.current = 'screen_counter'

    def exec_shutdown(self):
        os.system("shutdown /s /t 1") #for windows os
        toast("shutting down system")
        # os.system("shutdown -h now")

class ScreenCounter(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenCounter, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 2)
        
    def delayed_init(self, dt):
        pass

    def exec_start(self):
        global flag_play
        global count_starting, count_get_data

        screen_main = self.screen_manager.get_screen('screen_main')

        count_starting = 3
        count_get_data = 10

        if(not flag_play):
            stream.start_stream()
            Clock.schedule_interval(screen_main.regular_get_data, 1)
            flag_play = True

    def exec_reload(self):
        global flag_play
        global count_starting, count_get_data

        screen_main = self.screen_manager.get_screen('screen_main')

        count_starting = 3
        count_get_data = 10
        self.ids.bt_reload.disabled = True

        if(not flag_play):
            stream.start_stream()
            Clock.schedule_interval(screen_main.regular_get_data, 1)
            flag_play = True

    def exec_save(self):
        global flag_play
        global count_starting, count_get_data
        global mydb, db_antrian
        global dt_no_antrian, dt_no_reg, dt_no_uji, dt_nama, dt_jenis_kendaraan, dt_status

        self.ids.bt_save.disabled = True

        mycursor = mydb.cursor()

        sql = "UPDATE tb_cekident SET sts = %s WHERE noantrian = %s"
        val = (1 if dt_status == "Lulus" else 2, dt_no_antrian)

        mycursor.execute(sql, val)

        mydb.commit()

        print(mycursor.rowcount, "record(s) affected")

        self.open_screen_main()

    def open_screen_main(self):
        global flag_play        
        global count_starting, count_get_data

        screen_main = self.screen_manager.get_screen('screen_main')

        count_starting = 3
        count_get_data = 10
        flag_play = False   
        screen_main.exec_reload_table()
        self.screen_manager.current = 'screen_main'


class RootScreen(ScreenManager):
    pass

class SoundLevelMeterApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.icon = 'asset/logo.png'

        LabelBase.register(
            name="Orbitron-Regular",
            fn_regular="asset/font/Orbitron-Regular.ttf")

        theme_font_styles.append('Display')
        self.theme_cls.font_styles["Display"] = [
            "Orbitron-Regular",
            72,
            False,
            0.15,
        ]       
        
        Window.fullscreen = 'auto'
        Window.borderless = False
        # Window.size = 900, 1440
        # Window.size = 450, 720
        # Window.allow_screensaver = True

        Builder.load_file('main.kv')
        return RootScreen()

if __name__ == '__main__':
    SoundLevelMeterApp().run()