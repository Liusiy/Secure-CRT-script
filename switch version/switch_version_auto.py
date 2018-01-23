# $language = "Python"
# $interface = "1.0"

#Description: Restart OLT into monitoring mode,
#             then copy .bin from tftp server, and reboot by .bin
#Author:      Liu Siyuan
#Date:        2018/1/17

#EN specify the environment
#1 : 1030C
#2 : 1030D
#3 : 1030C-ext

EN = 1

hostname = "olt"
host_ip = "10.0.0.66 255.255.255.0 "
version = {1 : "_10.3.0C_", \
           2 : "_10.3.0D_", \
           3 : "_10.3.0C_"}

build = {1 : "49640", \
         2 : "49680", \
         3 : "49428"}

src_switch_bin = {1 : "BD_GP3616" + version[1] + build[1] + ".bin ", \
                  2 : "BD_GP3616" + version[2] + build[2] + ".bin ", \
                  3 : "BD_GP3616" + version[3] + build[3] + ".bin "}

dst_switch_bin = "switch.bin "
maple_1030c = "maple.1030c "
maple_1030d = "maple.1030d.ext "
maple_startup = "maple.blob "
pc_ip = "10.0.0.100 "
usrname = "admin"
pswd = "admin" 

mode_monitor = "monitor#"
mode_user = hostname + ">"
mode_su = hostname + "#"
mode_cfg = hostname + "_config#"
mode_cfg_others = hostname + "_config_"
mode_diag = [hostname+"(D)#", hostname+"_config(D)#"]
mode_all = [mode_monitor, mode_user, mode_su, mode_cfg, mode_cfg_others] + mode_diag

#mode_intf = 'olt_config_gpon'+ slot + '/' + link + '#'

#def quitAndReb():
#    for j in range(5):
#        crt.Screen.Send(chr(13))
#        if crt.Screen.WaitForStrings(["olt>", "olt"]) == 1:
#            crt.Screen.Send("su")
#            crt.Screen.Send("reb n" + chr(13))
#            break
#        crt.Screen.Send("quit")

#    position = crt.Screen.WaitForStrings(["olt", ">", "..."])
#    if position == 1:
#        quitAndReb()
#    else:
#        for i in range(5):
#            crt.Screen.Send("/" + chr(13))
#            if crt.Screen.WaitForStrings(["> ~"]) == 1:
#                crt.Screen.Send("Quit" + chr(13)*2)
#                quitAndReb()
#                break
#
def sendCmd(cmd):
    crt.Screen.Send(cmd + chr(13))
    
def waitStr(mode_list, time):
    mode = crt.Screen.WaitForStrings(mode_list, time)
    return mode

def usr_pswd_check():
    if waitStr(["Username:", hostname], 1) == 1:
        sendCmd(usrname)
        temp = waitStr(["Access denied!", "Authentication failed!", hostname], 1)
        if temp == 1 or temp == 2:
            return False
    temp = waitStr(["Password:", "password:", hostname], 1)
    if temp == 1 or temp == 2:
        sendCmd(pswd)
        temp = waitStr(["Access denied!", "Authentication failed!", hostname], 1)
        if temp == 1 or temp == 2:
            return False
    
def rebToMonitor():
#发送enter键，这样WaitForStrings才能进行有效的采集
#可以认为WaitForStrings采集脚本运行之后的屏幕显示
    sendCmd(chr(13))    
#获取的mode为int型数值，为元素在列表中的索引
    mode = waitStr(mode_all, 1)
    if mode == 1:
        return
    if mode == 2:
        sendCmd("su")
        if usr_pswd_check() == False:
            return False
        sendCmd("reb n")
    elif mode == 3:
        sendCmd("reb n")
    elif mode == 4:
        sendCmd("quit")
        sendCmd("reb n")
    elif mode == 5:
        sendCmd(("quit" ) * 2 + "reb n" )
        if waitStr("Unknown command", 1) == 1:
            sendCmd("quit")
            sendCmd("su")
            sendCmd("reb n")
    elif mode == 6 or mode == 7:
        while waitStr([mode_user, mode_su, mode_cfg, mode_cfg_others] + mode_diag, 1) != 1:
            sendCmd("quit")
        sendCmd("su")
        if waitStr(["password:", hostname], 1) == 1:
            sendCmd(pswd)
            if waitStr(["Access denied", hostname], 1) == 1:
                return False
        sendCmd("reb n")
        
    if waitStr(["                 Welcome to BDCOM " + \
                                  "GP3600-08 OLT"], 0) == 1:
        sendCmd(chr(13))
                

#    if waitStr(["RTC Test"]) == 1:
#        for i in range(3):
#            sendCmdKeys("^p")
#            crt.Sleep(100)
z

def rebByVflash():
    sendCmd(chr(13))
    sendCmd("dir")
    temp = waitStr(["     maple.blob",  "     switch.bin"], 1)
    if temp !=1 and temp != 2:
        return False
    if temp == 1:
        if EN == 1:
            sendCmd("dir")
            if waitStr(["     maple.1030c"], 1) == 1:
                sendCmd("rename " + maple_startup + maple_1030d )
                sendCmd("rename " + maple_1030c + maple_startup )
        elif EN == 2 or EN == 3:
            sendCmd("dir")
            if waitStr(["     maple.1030d.ext"], 1) == 1:
                sendCmd("rename " + maple_startup + maple_1030c )
                sendCmd("rename " + maple_1030d + maple_startup )
                
        sendCmd("boot flash mem vflash")
        sendCmd("vflash size 20")
        sendCmd("ip add " + host_ip)
        sendCmd("copy tftp:" + src_switch_bin[EN] + "flash:" + dst_switch_bin + pc_ip )
    elif temp == 2: #Forgot to modify the tftp server path 
        sendCmd("vflash information")
        if waitStr(["Unknown command", "small block size"], 1) == 2:
            sendCmd("copy tftp:" + src_switch_bin[EN] + "flash:" + dst_switch_bin + pc_ip )
        else:
            return Flase
    if waitStr(["TFTP:tftpXfer fail"], 10) == 1:
        return False
    if waitStr(["TFTP:successfully"], 0) == 1:
        sendCmd("boot flash switch.bin")

def goToModeCfg():
    if waitStr(["Press RETURN to", "Error: Cannot find a boot image file."], 0) == 1:
        sendCmd(chr(13))
        if usr_pswd_check() == False:
            return False
        sendCmd("su")
        if usr_pswd_check() == False:
            return Flase
        sendCmd("config")
    elif waitStr(["Press RETURN to", "Error: Cannot find a boot image file."], 0) == 2:
        return False

    crt.Sleep(100)
    
def main():
    global EN
    while True:
        if EN == 1:
            EN = 3
        else:
            EN = 1
        if rebToMonitor() == False:
            return
        if rebByVflash() == False:
            return
        if goToModeCfg() == False:
            return
        crt.Sleep(10000)

main()


    
