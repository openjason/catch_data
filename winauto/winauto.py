import time
from pywinauto.application import Application
#app = Application().start("f:\\test\\录像1.exe")
app = Application().start("notepad.exe")

app.Notepad.menu_select("查看->状态栏")


app.Notepad.menu_select("帮助->关于记事本")

#for i in app.dict_keys:
#    print(i)
about_dlg = app.window_(title_re = u"关于", class_name = "#32770")

about_dlg['确定'].Click()

#dlg_spec.
   
#app.32770.OK.click()

app.UntitledNotepad.Edit.type_keys("pywinauto Works!", with_spaces = True)
