from cv2 import DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMINGLUT
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.core.window import Window
from kivymd.uix.datatables import MDDataTable
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.app import MDApp
from kivy.metrics import dp
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
        "A200": "#A51919",
        "A500": "#A51919",
        "A700": "#A51919",
    },

    "Gray": {
        "200": "#999999",
        "500": "#999999",
        "700": "#999999",
    },

    "Blue": {
        "200": "#4471C4",
        "500": "#4471C4",
        "700": "#4471C4",
    },

    "Green": {
        "200": "#19A56B",
        "500": "#19A56B",
        "700": "#19A56B",
    },

    "Yellow": {
        "200": "#FFC000",
        "500": "#FFC000",
        "700": "#FFC000",
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
        "CardsDialogs": "#000000",
        "FlatButtonDown": "#333333",
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
count_starting = 3
count_get_data = 10

p = pyaudio.PyAudio() # start the PyAudio class
stream=p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,
        frames_per_buffer=CHUNK) #uses default input device

class ScreenMain(MDScreen):        
    def __init__(self, **kwargs):
        global mydb, db_antrian
        super(ScreenMain, self).__init__(**kwargs)
        try:
            mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_trb"
            )

            db_antrian = np.array([["001", "002", "003"],
                                    ["PB123XY","PB234YZ","PB345XZ"],
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
                ("No.", dp(20), self.sort_on_num),
                ("Antrian", dp(30)),
                ("No Reg Kendaraan", dp(70)),
                ("Jenis", dp(50)),
                ("Action", dp(25)),
            ],
        )
        self.data_tables.bind(on_row_press=self.on_row_press)
        layout.add_widget(self.data_tables)

    def sort_on_num(self, data):
        try:
            return zip(*sorted(enumerate(data),key=lambda l: l[0][0]))
        except:
            toast("Error sorting data")

    def on_row_press(self, table, row):
        try:
            start_index, end_index  = row.table.recycle_data[row.index]["range"]
            value1                  = row.table.recycle_data[start_index + 1]["text"]
            value2                  = row.table.recycle_data[start_index + 2]["text"]
            value3                  = row.table.recycle_data[start_index + 3]["text"]
            value4                  = row.table.recycle_data[start_index + 4]["text"]

            self.ids.lb_no_antrian.text = str(value1)
            self.ids.lb_no_uji.text = str(value2)
            self.ids.lb_id_jenis_kendaraan.text = str(value3)
            self.ids.lb_status.text = str(value4)
        except Exception as e:
            toast_msg = f'error update table: {e}'
            toast(toast_msg)   

    def regular_update_display(self, dt):
        global flag_conn_stat, flag_device
        global dt_sound, count_starting, count_get_data

        try:
            screen_counter = self.screen_manager.get_screen('screen_counter')
            self.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            self.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_counter.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_counter.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))

            if(self.ids.lb_status.text == "Mulai Tes"):
                self.ids.bt_run.disabled = False
            else:
                self.ids.bt_run.disabled = True

            if(not flag_play):
                screen_counter.ids.bt_stop.md_bg_color = colors['Green']['200']
                screen_counter.ids.bt_stop.disabled = False
                screen_counter.ids.bt_run.md_bg_color = colors['Red']['A200']
                screen_counter.ids.bt_run.disabled = False
            else:
                screen_counter.ids.bt_run.disabled = True
                screen_counter.ids.bt_stop.disabled = True

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
                screen_counter.ids.lb_test_subtitle.text = "Nilai Kebisingan Terukur"
                screen_counter.ids.lb_sound.text = str(np.round(dt_sound, 2))
                                               
            elif(count_starting > 0):
                if(flag_play):
                    screen_counter.ids.lb_test_subtitle.text = "Memulai Pengujian Kebisingan Dalam"
                    screen_counter.ids.lb_sound.text = str(count_starting)

            if(count_get_data <= 0):
                screen_counter.ids.lb_test_result.size_hint_y = 0.15
                if(dt_sound >= 83 and dt_sound <= 118):
                    screen_counter.ids.lb_test_result.md_bg_color = colors['Green']['200']
                    screen_counter.ids.lb_test_result.text = "LULUS"
                else:
                    screen_counter.ids.lb_test_result.md_bg_color = colors['Red']['A200']
                    screen_counter.ids.lb_test_result.text = "GAGAL"

            elif(count_get_data > 0):
                    screen_counter.ids.lb_test_result.size_hint_y = None
                    screen_counter.ids.lb_test_result.height = dp(0)
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
            mycursor.execute("SELECT noantrian, nouji, idjeniskendaraan, sts FROM tb_cekident")
            myresult = mycursor.fetchall()
            db_antrian = np.array(myresult).T
            self.data_tables.row_data=[(f"{i+1}", f"{db_antrian[0, i]}", f"{db_antrian[1, i]}", f"{db_antrian[2, i]}", 
                                        'Mulai Tes' if (int(db_antrian[3, i]) == 0) else ('Lulus' if (int(db_antrian[3, i]) == 1) else 'Gagal')) 
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

    def exec_restart(self):
        global flag_play, stream, p
        global count_starting, count_get_data

        screen_main = self.screen_manager.get_screen('screen_main')

        count_starting = 3
        count_get_data = 10

        self.ids.bt_run.disabled = True

        if(not flag_play):
            stream.start_stream()
            Clock.schedule_interval(screen_main.regular_get_data, 1)
            flag_play = True

    def exec_stop(self):
        global flag_play, stream, p
        global count_starting, count_get_data

        count_starting = 3
        count_get_data = 10

        flag_play = False
        self.ids.bt_stop.disabled = True

        self.open_screen_main()

    def open_screen_main(self):
        self.screen_manager.current = 'screen_main'


class RootScreen(ScreenManager):
    pass

class SoundLevelMeterApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Gray"
        self.theme_cls.theme_style = "Dark"
        self.icon = 'asset/logo.png'
        Window.fullscreen = 'auto'
        Window.borderless = False
        # Window.size = 900, 1440
        # Window.size = 450, 720
        # Window.allow_screensaver = True

        Builder.load_file('main.kv')
        return RootScreen()

if __name__ == '__main__':
    SoundLevelMeterApp().run()