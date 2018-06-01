import paramiko
import sys
import os
import time
#import hashlib
from tkinter import *
from tkinter import messagebox

from cfg2xls_sw import cfgxlsproc


class SW_CONF():
    def __init__(self,main_win):
        self.main_win = main_win
        # add some widgets to the root window...

        self.main_win.update_idletasks()
        self.main_win.deiconify()  # now window size was calculated
        self.main_win.withdraw()  # hide window again
        self.main_win.geometry('770x310+300+200')
#        self.main_win.geometry('%sx%s+s%+s%' % (self.main_win.winfo_width() + 10, self.main_win.winfo_height() + 10),400,400)
        # center window on desktop
        self.main_win.deiconify()



        self.main_win.title("防火墙配置导出处理程序")
        self.tips_lable_text = "tips"
        self.var_l_tips = IntVar()



    def check_ip_format(self,ipaddr):
        if re.match('((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))',ipaddr) != None:
            return True
        else:
            return False

    def proc_conf_click(self):
        self.var_l_tips.set("正在分析配置文件,输出Excel文件.")
        self.main_win.update_idletasks()
        try:
            cfgxlsproc()
            
        except:
            self.var_l_tips.set("程序出错，请联系管理员.")
            self.main_win.update_idletasks()
            
        self.var_l_tips.set("防火器策略Excel文件已生成.文件名: cfg_new.xlsx")
        self.main_win.update_idletasks()
        if messagebox.askyesno('询问','确认现在打开Excel ？')== True:
#            os.system("start " + r"cfg_new.xlsx")
            os.startfile(r"cfg_new.xlsx")
            self.var_l_tips.set("正在启动Excel... ... ")
            self.main_win.update_idletasks()

    def get_conf_click(self):
        hostip = self.e1.get()
        if not self.check_ip_format(hostip):
            messagebox.showerror('ERROR', 'IP地址有误.')
            return 1
        username = self.e2.get()
        if len(username)<3 :
            messagebox.showerror('ERROR', '用户名有误.')
            return 1
        port = 22
        password = self.e3.get()
        if len(password)<3 :
            messagebox.showerror('ERROR', '密码有误.')
            return 1
        self.get_sw_conf(hostip,port,username,password)
        

    def init_win(self):
        entry_var = StringVar()

#        self.space1_lable = Label(self.main_win).grid(column=0, row=0)

        self.hostip_lable = Label(self.main_win, text="防火墙IP:",font = ("Arial, 11")).grid(column=0, row=1, sticky=E)
        self.username_lable = Label(self.main_win, text="   管理员用户:",font = ("Arial, 11")).grid(sticky=E)
        self.pwd_lable = Label(self.main_win, text="密码:",font = ("Arial, 11")).grid(sticky=E)
        self.tips_lable = Label(self.main_win, textvariable=self.var_l_tips).grid(column=1, row=5, sticky=E)
        self.var_l_tips.set(" ")
        
        self.space_lable = Label(self.main_win).grid(column=1, row=0, sticky=E)

        self.e1 = Entry(self.main_win,textvariable = entry_var ,width = 50,font = ("Arial, 11"))
        
        entry_var.set("192.168.")
        self.e2 = Entry(self.main_win,width = 50,font = ("Arial, 11"))
        self.e3 = Entry(self.main_win,width = 50,font = ("Arial, 11"))

        self.e1.grid(row=1, column=1)
        self.e2.grid(row=2, column=1)
        self.e3.grid(row=3, column=1)

        self.photo = PhotoImage(file='ep.png')
        self.label = Label(image=self.photo)
        self.label.image = self.photo
        self.label.grid(row=1, column=2, columnspan=3, rowspan=3, sticky=W+E+N+S, padx=18, pady=18)

        self.get_conf_button = Button(self.main_win, text="读配置", bg="lightblue", width=12,command=self.get_conf_click)
        self.get_conf_button.grid(row=4, column=1,padx=7, pady=5, sticky="w")

        self.proc_conf_button = Button(self.main_win, text="导出配置",bg="lightblue", width=12,command=self.proc_conf_click)
        self.proc_conf_button.grid(row=4, column=1,padx=17, pady=15, )
        mainloop()


    def get_sw_conf(self,hostip,port,username,password):
        self.var_l_tips.set("Connecting host: " + username+"@"+hostip)
        self.main_win.update_idletasks()
        i = 1
        while True:
            print ("Trying to connect to %s (%i/3)" % (hostip, i))

            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostip, username=username, password=password, port=port,timeout=3)
                print ("Connected to %s" % hostip)

                self.var_l_tips.set("Connected to %s" % hostip)
                self.main_win.update_idletasks()
                
                remote_conn = ssh.invoke_shell()
                output = remote_conn.recv(65535)
                output_str = bytes.decode(output)
                print (output_str)
                time.sleep(0.4)
                prompt = username + "@"
                if not(prompt in output_str):
                    messagebox.showerror('ERROR', '用户或密码有误.')
                    return 2
                else:
                    break
                
            except paramiko.AuthenticationException:
                print ("Authentication failed when connecting to %s" % hostip)
                sys.exit(1)
            except:
                print ("Could not SSH to %s, waiting for it to start" % hostip)
                i += 1
                time.sleep(1)
            # If we could not connect within time limit
            if i > 2:
                print ("Could not connect to %s. Giving up" % hostip)
                self.var_l_tips.set(username + "@" + hostip+"  Connect Failed...")
                self.main_win.update_idletasks()

                return 2


        more_str = bytes.fromhex('2D2D4D4F52452D2D1B5B38441B5B4B')
        #替换--MORE--等
        
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

        i = 1
        while (True):
            if prompt in output_str:
                print("hava prompt...............")
                break
            self.var_l_tips.set("Reading SonicWall configure file." + str(i*1600)+ "lines")
            self.main_win.update_idletasks()

            i = i + 1
            remote_conn.send(' ')
            time.sleep(0.1)
            output = remote_conn.recv(65535)

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
