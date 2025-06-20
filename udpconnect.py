from kivymd.app import MDApp
from kivy.clock import Clock
from os import path
import socket
import json
from time import time, sleep

class UDPConnect():
    def __init__(self):
        self.app = MDApp.get_running_app()
        self.ip_file = f"{self.app.user_dir}/ip_setting_record.txt"
        self.exam_file()
        self.PORT = 9999
        self.indata = ''
        self.ip = ''   # 來自udp_test 的append_data, 當有設備回應時, 會有此ip, 並後續記錄下來
        self.get_ip_method = 0  #0 = broadcast, 1 = scan ip
        self.response = []      # 將發送 request_mac的回應, 放置的地方
        self.found_ip = 0
        self.connect_successful = 0 # 如果有連上設備 值為1
        self.mac_records = {}
        self.outdata = "request_mac" + " "
        self.udp_ip = ""
        self.remote_port = 9999
        # self.set_socket()

    def exam_file(self):
        if not path.isfile(self.ip_file):
            with open(self.ip_file, "w") as f:
                f.write('')
            f.close()
        with open (self.ip_file,'r') as f:
            f1 = f.read()
        f.close()
        if f1 != '':
            print(eval(f1))

    def set_socket(self):
        self.sok = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sok.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sok.sendto(self.outdata.encode(), self.server_addr)
        self.sok.settimeout(1)

    def get_ip(self):
        print('如果有其他進行中的clock, 先停止')
        # self.app.waterheater.stop_clock()
        print('可增加在連線中, 會有動畫感')
        # self.app.clock_connecting_to_waterheater()
        self.try_get_ip_counter = 0
        # self.app.no_sleep()
        Clock.schedule_once(self.get_ip_with_scan, 1)


    def get_ip_with_scan(self, *args):
        # self.app.sm.get_screen("login_screen").ids["connect_status"].text = "掃瞄IP，請稍後"
        HOST = self.get_ip_subnet()
        HOST_1 = ""
        self.try_get_ip_counter += 1

        if self.get_ip_method == 0:
            try_get_ip_sum = 5
            HOST_1 = HOST + "255"
            self.udp_test(HOST_1)
            print(f'indata in get ip with scan: {self.indata} try ip counter:{self.try_get_ip_counter}')
            if self.indata!="" and 'control' in eval(self.indata):
                if eval(self.indata)['control'] == self.app.control_brand:
                    Clock.unschedule(self.get_ip_with_scan)
                    self.socket_connect()
                else:
                    print(f'failed {self.try_get_ip_counter}')
            else:
                print(f'failed {self.try_get_ip_counter}')
            sleep(0.5)


        elif self.get_ip_method == 1:
            try_get_ip_sum = 252
            if len(self.response) == 0:
                # HOST_ip = f'{HOST}{self.try_get_ip_counter+1}'
                # self.app.sm.get_screen('login_screen').ids["page_title"].ids[
                #     "all_pages_title"].text = f'{self.app.lang_login_title} \n {HOST_ip}'
                self.udp_test(HOST_1)
            else:
                self.app.clear_no_sleep()
                self.app.socket_connect()
                Clock.unschedule(self.get_ip_with_scan)
        if self.try_get_ip_counter >=try_get_ip_sum:
            Clock.unschedule(self.get_ip_with_scan)

            # self.app.clear_no_sleep()
            # self.app.unclock_connecting_to_waterheater()
            # self.app.waterheater.stop_clock()
            # self.app.waterheater.start_clock()

        if self.indata != "" and self.connect_successful == 1 and eval(self.indata)['control']== self.app.control_brand:
            self.found_ip = 1
            self.timeexpire = 0
            # self.app.sm.get_screen("login_screen").ids["connect_status"].md_bg_color = [0 / 255, 204 / 255, 204 / 255,1]
            # self.app.sm.get_screen("login_screen").ids["connect_status"].text = '已連線'
            # self.app.broker_exist = 1
        else:
            self.found_ip = 0
            # self.app.sm.get_screen("login_screen").ids["connect_status"].text = "未連線"

    def get_ip_subnet(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        try:
            s.connect(('10.254.254.254', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP[0:IP.rfind(".") + 1]


    def udp_test(self, HOST_1):
        try:
            self.server_addr = (HOST_1, self.PORT)
            self.set_socket()
            def append_data():
                self.indata, addr = self.sok.recvfrom(1024)
                if self.indata != "":
                    self.response.append([json.loads((self.indata.decode()).replace("'", '"')), addr[0]])
            if self.get_ip_method == 0:
                while True:
                    append_data()
                    sleep(.1)


        except:
            changed = 0
            i = 1
            for re in self.response:
                self.connect_successful = 1
                if re[0]['control']!= self.app.control_brand:
                    continue
                if len(self.mac_records) == 0:
                    self.mac_records[re[0]['control']] = {re[0]['mac']: [i, re[1]]}
                    i = 0
                    changed = 1
                # macs = list(self.app.mac_records[self.app.control_type].keys())
                macs = list(self.mac_records[self.app.control_brand].keys())
                if re[0]['mac'] in macs:
                    if re[1] != self.mac_records[re[0]['control']][re[0]['mac']][1]:
                        self.mac_records[re[0]['control']][re[0]["mac"]] = [
                            self.mac_records[re[0]['control']][re[0]['mac']][0], re[1]]
                        changed = 1
                else:
                    self.mac_records[re[0]['control']][re[0]["mac"]] = [0, re[1]]
                    changed = 1
            if changed == 1:
                with open(self.ip_file, 'w') as f:
                    f.write(f'{self.mac_records}')
                f.close()

    def socket_connect(self):
        if not path.isfile(self.ip_file):
            with open(self.ip_file, 'w') as f:
                f.write("")
            f.close()

        with open(self.ip_file, 'r') as f:
            f1 = f.read()
        f.close()
        if f1 == "{}" or f1 == "":
            self.mac_records = {}
        else:
            self.mac_records = json.loads(f1.replace("'", '"'))
            if self.app.control_brand in self.mac_records:
                if len(self.mac_records[self.app.control_brand]) > 3:
                    self.mac_records = {}
            else:
                self.mac_records = {}

        # 這部份是如果有存mac資料, 先試著連線, 不成功的話, 再重新做get_ip動作
        if self.app.control_brand in self.mac_records:
            self.udp_test(self.mac_records)
            on_ips = [value[1] for key, value in self.mac_records[self.app.control_brand].items() if value[0] == 1]
            for i in range(5):
                self.udp_test(on_ips[0])
                if self.connect_successful == 1:
                    break
                else:
                    print(f'try : {i}')
            if self.connect_successful == 1:
                self.found_ip = 1
            else:
                self.found_ip= 0
#                self.get_ip()
        else:
            pass
#            self.get_ip()

        if self.found_ip == 1 and self.mac_records!={}:
            wh_json = self.mac_records[self.app.control_brand]
            for wh_mac in wh_json:
                if wh_json[wh_mac][0] == 1:
                    try:
                        self.udp_ip = wh_json[wh_mac][1]
                        self.mac = wh_mac
                        self.set_socket()
                        self.app.status_label.text += f"\n ip:{self.udp_ip}"
                        indata, addr = self.sok.recvfrom(1024)
                        # self.app.screen_change(f'{self.app.control_brand}_screen')
                        self.connect_successful = 1

                    except:
                        if self.ip != "":
                            self.server_addr = (self.ip, self.PORT)
                        else:
                            self.found_ip = 0
                            # self.app.screen_change("login_screen")
        else:
            self.found_ip = 0
