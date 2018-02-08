
'''
没有经过测试多驱动的eject
If you have more that one drive, you can use to open command to initialize a specific device before calling the function above. For example (not tested).

ctypes.windll.WINMM.mciSendStringW(u"open D: type cdaudio alias d_drive", None, 0, None)
ctypes.windll.WINMM.mciSendStringW(u"set d_drive door open", None, 0, None)
'''

import ctypes
def cdrom_eject():
	ctypes.windll.WINMM.mciSendStringW(u"set cdaudio door open", None, 0, None)

