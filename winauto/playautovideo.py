import time
from pywinauto.application import Application


with open('list.txt','r') as fp:
    for list in fp:

        list = list.strip()
        if len(list) > 3 :
            print('ready for play:',list)
            app = Application().start(list,timeout=None)
            time.sleep(6)
            app.TPlayForm.right_click()
            app.TPlayForm.type_keys("k")
            app.TPlayForm.right_click()
            app.TPlayForm.type_keys("l")
            app.TPlayForm.right_click()
            app.TPlayForm.type_keys("s")
            app.wait_for_process_exit(timeout=9999)
            time.sleep(2)
        else:
            break
        

