import utils
import time, cv2
import numpy as np

from multiprocessing import Process, Queue

program_off = False
reject_run = True
yolo_run = False
setting_change = False

off_click = False
reject_click = False
yolo_click = False
setting_click = False

AU_start, AD_start, AU_quit, AD_quit  = Queue(), Queue(), Queue(), Queue()
BU_start, BD_start, BU_quit, BD_quit = Queue(), Queue(), Queue(), Queue()
AU_reject, AD_reject, AU_img, AD_img = Queue(), Queue(), Queue(), Queue()
BU_reject, BD_reject, BU_img, BD_img = Queue(), Queue(), Queue(), Queue()
AU_setting, AD_setting = Queue(), Queue()
BU_setting, BD_setting = Queue(), Queue()

def mouse_event(event, x, y, flags, param):
    global program_off, reject_run, yolo_run, setting_change, off_click, reject_click, yolo_click, setting_click
    global AU_reject, AD_reject, BU_reject, BD_reject
    _, _ = flags, param
    
    """ 마우스 오버레이시 변화 """
    if 9 < x < 84:
        if 48 < y < 121:
            off_click = True
        elif 145 < y < 218:
            reject_click = True
        elif 240 < y < 320:
            yolo_click = True
        elif 340 < y < 420:
            setting_click = True
        else:
            off_click = False
            reject_click = False
            yolo_click = False
            setting_click = False
        
    if event == cv2.EVENT_LBUTTONDOWN:
        pass

    if event == cv2.EVENT_LBUTTONUP:
        if 9 < x < 84 and 48 < y < 121:
            program_off = True

        if 9 < x < 84 and 145 < y < 218:
            if reject_run:
                reject_run = False
                AU_reject.put('pass')
                AD_reject.put('pass')
                BU_reject.put('pass')
                BD_reject.put('pass')
            else:
                reject_run = True
                AU_reject.put('reject')
                AD_reject.put('reject')
                BU_reject.put('reject')
                BD_reject.put('reject')
            
        if 9 < x < 84 and 240 < y < 320:
            if yolo_run:
               yolo_run = False
               AU_start.put('stop')
               AD_start.put('stop')
               BU_start.put('stop')
               BD_start.put('stop')
            else:
               yolo_run = True
               AU_start.put('start')
               AD_start.put('start')
               BU_start.put('start')
               BD_start.put('start')
               
        if 9 < x < 84 and 340 < y < 420:
            setting_change = True

    if event == cv2.EVENT_RBUTTONDOWN:
        print(f'x:({x}), y:({y})')

if __name__ == "__main__":
    #utils.del_folder()
    
    p_AU = Process(target=utils.Main, args=('A_U', AU_start, AU_quit, AU_reject, AU_img, AU_setting,))
    p_AD = Process(target=utils.Main, args=('A_D', AD_start, AD_quit, AD_reject, AD_img, AD_setting,))
    p_BU = Process(target=utils.Main, args=('B_U', BU_start, BU_quit, BU_reject, BU_img, BU_setting,))
    p_BD = Process(target=utils.Main, args=('B_D', BD_start, BD_quit, BD_reject, BD_img, BD_setting,))

    p_AU.start()
    time.sleep(1)
    p_AD.start()
    time.sleep(1)
    p_BU.start()
    time.sleep(1)
    p_BD.start()
    time.sleep(1)

    cv2.namedWindow('Noksan', flags=cv2.WINDOW_NORMAL)
    cv2.resizeWindow(winname='Noksan', width=100, height=490)
    cv2.setMouseCallback('Noksan', mouse_event)
    
    while True:
        IMG = np.zeros((470, 90, 3), np.uint8)
        
        """ 프로그램 종료 버튼 그리기 """
        if off_click:
            IMG = cv2.putText(IMG, f"OFF", (15, 78),
                              cv2.FONT_HERSHEY_DUPLEX, 1, [150, 150, 255], 2)
            IMG = cv2.putText(IMG, f"Click here", (10, 108),
                              cv2.FONT_HERSHEY_DUPLEX, .4, [150, 150, 255], 1)
        else:
            IMG = cv2.putText(IMG, f"OFF", (15, 80),
                              cv2.FONT_HERSHEY_DUPLEX, 1, [250, 200, 255], 2)
            IMG = cv2.putText(IMG, f"Click here", (10, 110),
                              cv2.FONT_HERSHEY_DUPLEX, .4, [250, 200, 255], 1)
        cv2.line(IMG, (5,130), (85,130), (50,50,50), 1)
        
        """ 리젝트 가동 유무 그리기 """
        if reject_run:
            if reject_click:
                IMG = cv2.putText(IMG, f"ON", (20, 178),
                                  cv2.FONT_HERSHEY_DUPLEX, 1, [150, 150, 255], 2)
                IMG = cv2.putText(IMG, f"Reject on", (13, 208),
                                  cv2.FONT_HERSHEY_DUPLEX, .4, [150, 150, 255], 1)
            else:
                IMG = cv2.putText(IMG, f"ON", (20, 180),
                                  cv2.FONT_HERSHEY_DUPLEX, 1, [250, 200, 255], 2)
                IMG = cv2.putText(IMG, f"Reject on", (13, 210),
                                  cv2.FONT_HERSHEY_DUPLEX, .4, [250, 200, 255], 1)
        else:
            if reject_click:
                IMG = cv2.putText(IMG, f"OFF", (15, 178),
                                  cv2.FONT_HERSHEY_DUPLEX, 1, [150, 150, 255], 2)
                IMG = cv2.putText(IMG, f"Reject off", (13, 208),
                                  cv2.FONT_HERSHEY_DUPLEX, .4, [150, 150, 255], 1)
            else:
                IMG = cv2.putText(IMG, f"OFF", (15, 180),
                                  cv2.FONT_HERSHEY_DUPLEX, 1, [250, 200, 255], 2)
                IMG = cv2.putText(IMG, f"Reject off", (13, 210),
                                  cv2.FONT_HERSHEY_DUPLEX, .4, [250, 200, 255], 1)
        cv2.line(IMG, (5, 230), (85, 230), (50, 50, 50), 1)
        
        """ 가동 유무 그리기 """
        if yolo_run:
            if yolo_click:
                IMG = cv2.putText(IMG, f"RUN", (15, 278),
                                  cv2.FONT_HERSHEY_DUPLEX, 1, [150, 150, 255], 2)
                IMG = cv2.putText(IMG, f"Detect on", (15, 308),
                                  cv2.FONT_HERSHEY_DUPLEX, .4, [150, 150, 255], 1)
            else:
                IMG = cv2.putText(IMG, f"RUN", (15, 280),
                                  cv2.FONT_HERSHEY_DUPLEX, 1, [250, 200, 255], 2)
                IMG = cv2.putText(IMG, f"Detect on", (15, 310),
                                  cv2.FONT_HERSHEY_DUPLEX, .4, [250, 200, 255], 1)
        else:
            if yolo_click:
                IMG = cv2.putText(IMG, f"STOP", (7, 278),
                                  cv2.FONT_HERSHEY_DUPLEX, 1, [150, 150, 255], 2)
                IMG = cv2.putText(IMG, f"Detect off", (13, 308),
                                  cv2.FONT_HERSHEY_DUPLEX, .4, [150, 150, 255], 1)
            else:
                IMG = cv2.putText(IMG, f"STOP", (7, 280),
                                  cv2.FONT_HERSHEY_DUPLEX, 1, [250, 200, 255], 2)
                IMG = cv2.putText(IMG, f"Detect off", (13, 310),
                                  cv2.FONT_HERSHEY_DUPLEX, .4, [250, 200, 255], 1)
        cv2.line(IMG, (5, 330), (85, 330), (50, 50, 50), 1)
        
        """ 설정값 변경 그리기 """
        if setting_click:
            IMG = cv2.putText(IMG, f"SETS", (5, 378),
                              cv2.FONT_HERSHEY_DUPLEX, 1, [150, 150, 255], 2)
            IMG = cv2.putText(IMG, f"Update NOW", (3, 408),
                              cv2.FONT_HERSHEY_DUPLEX, .4, [150, 150, 255], 1)
        else:
            IMG = cv2.putText(IMG, f"SETS", (5, 380),
                              cv2.FONT_HERSHEY_DUPLEX, 1, [250, 200, 255], 2)
            IMG = cv2.putText(IMG, f"Update sets", (5, 410),
                              cv2.FONT_HERSHEY_DUPLEX, .4, [250, 200, 255], 1)
        cv2.line(IMG, (5,430), (85,430), (50,50,50), 1)

        if setting_change:
            setting_change = False
            AU_setting.put('on')
            AD_setting.put('on')
            BU_setting.put('on')
            BD_setting.put('on')

        cv2.imshow('Noksan', IMG)
        cv2.moveWindow('Noksan', 10, 0)
        cv2.waitKey(1)
        
        for i in range(AU_img.qsize()):
            imgAU = AU_img.get()
            if i == 0:
                cv2.imshow('A-Upper', imgAU)
                cv2.moveWindow('A-Upper', 175, 50)

        for i in range(AD_img.qsize()):
            imgAD = AD_img.get()
            if i == 0:
                cv2.imshow('A-Down', imgAD)
                cv2.moveWindow('A-Down', 175, 500)
        
        for i in range(BU_img.qsize()):
            imgBU = BU_img.get()
            if i == 0:
                cv2.imshow('B-Upper', imgBU)
                cv2.moveWindow('B-Upper', 575, 50)

        for i in range(BD_img.qsize()):
            imgBD = BD_img.get()
            if i == 0:
                cv2.imshow('B-Down', imgBD)
                cv2.moveWindow('B-Down', 575, 500)
        
        if program_off:
            AU_quit.put('off')
            AD_quit.put('off')
            BU_quit.put('off')
            BD_quit.put('off')
            cv2.destroyAllWindows()
            break

    p_AU.terminate()
    p_AD.terminate()
    p_AU.join()
    p_AD.join()
    p_BU.terminate()
    p_BD.terminate()
    p_BU.join()
    p_BD.join()
