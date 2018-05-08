import paramiko
import sys
import time
#import hashlib
from tkinter import *


class SW_CONF():
    def __init__(self,main_win):
        self.main_win = main_win
        self.tips_lable_text = "tips"
        self.var = IntVar()

    def check_ip_format(self,ipaddr):
        if re.match('((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))',ipaddr) != None:
            return True
        else:
            return False

    def get_conf_click(self):
        hostip = self.e1.get()
        msgbox(text, title, ok_button='OK', image=None, root=None)
        if self.check_ip_format(hostip):
            msgbox(text, title, ok_button='OK', image=None, root=None)
        username = self.e2.get()
        port = 22
        password = self.e3.get()
        self.get_sw_conf(hostip,port,username,password)

    def init_win(self):

        self.hostip_lable = Label(self.main_win, text="防火墙ip:").grid(sticky=E)
        self.username_lable = Label(self.main_win, text="用户:").grid(sticky=E)
        self.pwd_lable = Label(self.main_win, text="密码:").grid(sticky=E)
        self.tips_lable = Label(self.main_win, textvariable=self.var).grid(column=1, row=4, sticky=E)

        self.e1 = Entry(self.main_win,width = 50)
        self.e2 = Entry(self.main_win,width = 50)
        self.e3 = Entry(self.main_win,width = 50)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)

        self.photo = PhotoImage(file='e:\\test\\tt.png')
        self.label = Label(image=self.photo)
        self.label.image = self.photo
        self.label.grid(row=0, column=2, columnspan=2, rowspan=2, sticky=W+E+N+S, padx=5, pady=5)

        self.get_conf_button = Button(self.main_win, text="读取配置", bg="lightblue", width=10,
                                              command=self.get_conf_click)
        self.get_conf_button.grid(row=2, column=2)

        button2 = Button(self.main_win, text='Zoom out')
        button2.grid(row=2, column=3)
        mainloop()


    def get_sw_conf(self,hostip,port,username,password):
        self.var.set("Try to connect host:" + hostip)
        return
        i = 10
        while True:
            print ("Trying to connect to %s (%i/30)" % (hostip, i))

            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostip, username=username, password=password, port=port)
                print ("Connected to %s" % hostip)

                self.tips_lable.config(text = "Connected to %s" % hostip)

                remote_conn = ssh.invoke_shell()
                output = remote_conn.recv(65535)
                print (output)
                break
            except paramiko.AuthenticationException:
                print ("Authentication failed when connecting to %s" % hostip)
                sys.exit(1)
            except:
                print ("Could not SSH to %s, waiting for it to start" % hostip)
                i += 1
                time.sleep(2)
            # If we could not connect within time limit
            if i == 30:
                print ("Could not connect to %s. Giving up" % hostip)
                sys.exit(1)

        # Send the command (non-blocking)

        more_str = bytes.fromhex('2D2D4D4F52452D2D1B5B38441B5B4B')
    #    more_str = b'abc'        #2D2D4D4F52452D2D1B5B38441B5B4B

        fo = open("sw.log","w")

        remote_conn.send('show version \n')
        output = remote_conn.recv(65535)
        prompt = username + "@"
        output_str = bytes.decode(output)
        print (output_str)

        fo.write(output_str)

        remote_conn.send('cli screen length session 1600\n')
        time.sleep(0.1)
        output = remote_conn.recv(65535)
        prompt = username + "@"
        output_str = bytes.decode(output)
        print (output_str)
        fo.write(output_str)
        output_str = ''
        remote_conn.send('show curr\n')


        while (True):
            if prompt in output_str:
                print("hava prompt...............")
                break
            remote_conn.send(' ')
            time.sleep(0.1)
            output = remote_conn.recv(65535)
    #        print(type(output))
            output = output.replace(more_str,b'')

            output_str = bytes.decode(output)

            print (output_str)
            fo.write(output_str)

        ssh.close()

        fo.close()

def gui_start():
    main_window = Tk()
    sw_conf = SW_CONF(main_window)
    # 设置根窗口默认属性
    sw_conf.init_win()

    main_window.mainloop()

if __name__ == "__main__":
    gui_start()