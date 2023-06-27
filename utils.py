import os
import random
import time, datetime, cv2, hid
import darknet
import numpy as np
import properties
import importlib

from pypylon import pylon
from time import sleep, localtime, strftime
from multiprocessing import Process, Queue
from multi_relay import Relay

"""비전 카메라 사용을 위한"""
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

camera = None

""" 릴레이 호출 """
def get_relay():
    dic = []
    for i in hid.enumerate():
        #print(i)
        if i['product_string'] == 'USBRelay2':
            dic.append(i['path'])
    return dic

def Main(line, start_Q, quit_Q, reject_Q, img_Q, setting_Q):
    global IMG, cameras

    if line == 'A_U':
        attribute = properties.A_U
    elif line == 'A_D':
        attribute = properties.A_D
    elif line == 'B_U':
        attribute = properties.B_U
    elif line == 'B_D':
        attribute = properties.B_D

    dic = get_relay()
    
    tray = attribute['tray']
    run_or_stop = 'stop' #초기값 설정
    reject_or_pass = 'reject'

    """ 카메라 활성 """
    cam_check, cameras = load_camera(attribute)

    if cam_check:
        IMG = np.zeros((1282,1026,3),np.uint8)  # 빈 이미지
        IMG = cv2.putText(IMG, "Waiting RUN signal...", (10, 100), cv2.FONT_HERSHEY_DUPLEX, 1, [255,200,255], 2)
        
        """ YOLO 모델 활성 """
        network, class_names = load_network(attribute)

        """ 본 검사 프로그램 가동 """
        while True:
            if start_Q.qsize() > 0:
                run_or_stop = start_Q.get()
                #print("검사 가동 상태를 변경합니다.")
                
            if reject_Q.qsize() > 0:
                reject_or_pass = reject_Q.get()
                #print("리젝트 유무 설정을 변경합니다.")
        
            if setting_Q.qsize() > 0:
                _ = setting_Q.get()
                importlib.reload(properties)
                #print("새로운 설정값을 로드합니다.")
        
            if run_or_stop == 'start':
                img_check, pic = get_img()
            
                if img_check:
                    result = image_detection(pic, network, class_names, attribute)
                
                    IMG_marked, detections, IMG = result
                    
                    img_Q.put(cv2.resize(IMG, (350, 350), interpolation=cv2.INTER_LINEAR))
                
                    if 1 in tray[-2:] :
                        run_R(dic, attribute)
                    tray = move_tray(tray)
                    if 1 in tray:
                        print(tray)
                
                    if detections:
                        answer, confidence, name = decide_ng(detections, attribute)
                    
                        if answer:
                            if reject_or_pass == 'reject':
                                tray[0] = 1

                            IMG_name = save_img(pic, attribute, confidence, name)
                            #save_annotations(IMG_name, image_resized, detections, class_names)
                            show_NG(IMG, attribute, confidence)
            else:
                _1, _2 = get_img()
                IMG = np.zeros((350,350,3),np.uint8)
                IMG = cv2.putText(IMG, "Program not run plz press F5...", (10, 100), cv2.FONT_HERSHEY_DUPLEX, 1, [255,200,255], 2)
                img_Q.put(IMG)
            
        cameras.StopGrabbing()
        cameras.Close()
        cv2.destroyAllWindows()
                    
def load_camera(attribute):
    global camera, cam
    """ 카메라 설정 """
    maxCamerasToUse = 1
    try:
        tlFactory = pylon.TlFactory.GetInstance()
        devices = tlFactory.EnumerateDevices()

        camera = pylon.InstantCameraArray(min(len(devices), maxCamerasToUse))
        for i, cam in enumerate(camera):
            cam.Attach(tlFactory.CreateDevice(devices[attribute['cam_port']]))
        camera.Open()
        pylon.FeaturePersistence.Load(attribute['cam_setting'], cam.GetNodeMap(), True)
        print('*'*16)
        print("Camera Ready... Setting : {}".format(attribute['cam_setting']))
        print('*'*16)
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        
        return True, camera
    
    except:
        print("-"*16)
        print("Camera Error....")
        print("-"*16)
        return False, 'error'

def get_img():
    try:
        grabResult = cameras.RetrieveResult(2000, pylon.TimeoutHandling_ThrowException)
        if cameras.IsGrabbing():
            image_raw = converter.Convert(grabResult)
            image_raw = image_raw.GetArray()
            image = cv2.cvtColor(image_raw, cv2.COLOR_BGR2RGB)
            grabResult.Release()
            return True, image
    except:
        return False, 'error'

def load_network(attribute):
    """ 네트워크 모델 생성 하여 모델, 클래스이름, 클래스별 색상을 받기 """
    random.seed(3)  # deterministic bbox colors
    network, class_names, class_colors = darknet.load_network(config_file=attribute["config_file"],
                                                              data_file=attribute["data_file"],
                                                              weights=attribute["weights"],
                                                              batch_size=1)
    return network, class_names

def image_detection(pic, network, class_names, attribute):
    """ 이미지 내 사물 디텍팅 하기 """
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    darknet_image = darknet.make_image(width, height, 3)

    image_rgb = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height),                                   interpolation=cv2.INTER_LINEAR)

    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh=attribute["thresh"], nms=attribute["nms"])
    darknet.free_image(darknet_image)
    image = draw_boxes(detections, image_resized, image_rgb)

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), detections, image_resized

def draw_boxes(detections, image, image_orig):
    color = [255, 0, 0]
    height, width, _ = image.shape
    height_orig, width_orig, _ = image_orig.shape

    for label, confidence, bbox in detections:
        left, top, right, bottom = bbox2points(bbox)

        left = int(left / width * width_orig)
        top = int(top / height * height_orig)
        right = int(right / width * width_orig)
        bottom = int(bottom / height * height_orig)

        cv2.rectangle(image_orig, (left, top), (right, bottom), color, 1)
        cv2.putText(image_orig, "{} [{:.2f}]".format(label, float(confidence)),
                    (left + 5, top + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    color, 1)
    return image_orig

def bbox2points(bbox):
    x, y, w, h = bbox
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

def move_tray(tray):
    tray = tray[-1:]
    tray.insert(0,0)
    return tray

def decide_ng(detections, attribute):
    answer = False
    confidence = 0
    name = None
    for label, confi, posi, in detections:
        if 'Reject' in label:
            if float(confi) / 100 > properties.Reject_limit:
                answer = True
                if float(confi) > confidence:
                    confidence = float(confi)
                    name = label
    return answer, confidence, name

def show_NG(IMG, attribute, confi):
    IMG = cv2.resize(IMG, (int(659*.35), ing(494*.35)))
    window = f"{attribute['line']}-line NG"
    cv2.imshow(window, IMG)
    
    if attribute['line'] == 'A':
        cv2.moveWindow(window, properties.small_x, 0)
    elif attribute['line'] == 'B':
        cv2.moveWindow(window, properties.small_x, int(494*.35)+73)

def make_dir(save_folder=properties.save_folder):
    """ 불량 이미지 저장할 폴더 생성하고 경로로 설정하기 """
    dir_path = save_folder
    if os.path.exists(
        dir_path + "/" + str(strftime("%Y-%m-%d", localtime())) + "/" + str(strftime("%H", localtime()))):
        dirname_reject = dir_path + "/" + str(strftime("%Y-%m-%d", localtime())) + "/" + str(
                strftime("%H", localtime()))
    else:
        if os.path.exists(dir_path + "/" + str(strftime("%Y-%m-%d", localtime()))):
            try:
                os.mkdir(dir_path + "/" + str(strftime("%Y-%m-%d", localtime())) + "/" + str(strftime("%H", localtime())))
            except:
                pass
            dirname_reject = dir_path + "/" + str(strftime("%Y-%m-%d", localtime())) + "/" + str(strftime("%H", localtime()))
        else:
            try:
                os.mkdir(dir_path + "/" + str(strftime("%Y-%m-%d", localtime())))
                os.mkdir(dir_path + "/" + str(strftime("%Y-%m-%d", localtime())) + "/" + str(strftime("%H", localtime())))
            except:
                pass
            dirname_reject = dir_path + "/" + str(strftime("%Y-%m-%d", localtime())) + "/" + str(strftime("%H", localtime()))
        print("\nThe New Folder For saving Rejected image is Maked...\n")

    return dirname_reject

def sv_img(img, attribute, confidence, name) :
    """ 이미지 저장 """
    dirname_reject = make_dir(properties.save_folder)
    name1 = str(label) + "-" + str(strftime("%Y-%m-%d-%H-%M-%S", localtime()))
    name2 = str(attribute['line']) + ".jpg"
    name_orig = str('[' + str(confidence) + ']') + name1 + name2
    final_name = os.path.join(dirname_reject, name_orig)
    cv2.imwrite(final_name, img)
    
    return final_name

def run_R(dic, attribute):
    try:
        R = Relay(path=dic[attribute['relay_port']])
        R.state(attribute['relay_gate'], on=True)
        R.h.close()
    except:
        pass

    sleep(attribute['relay_runtime'])

    try:
        R = Relay(path=dic[attribute['relay_port']])
        R.state(attribute['relay_gate'], on=False)
        R.h.close()
    except:
        pass

def del_folder():
    days = os.listdir(properties.save_folder)
    day2num = []
    for day in days:
        array_ = day.split('-')
        num = int(array_[0] + array_[1] + array_[2])
        day2num.append(num)

    day2num.sort()

    if properties.day_limit < len(day2num):
        del_folder_list = day2num[:len(day2num) - properties.day_limit]
        for del_ in del_folder_list:
            print(f'{del_} 폴더를 삭제합니다.')

            print(f'{str(del_)[:4]}-{str(del_)[4:6]}-{str(del_)[6:]}')
            shutil.rmtree(os.path.join(properties.save_folder, f'{str(del_)[:4]}-{str(del_)[4:6]}-{str(del_)[6:]}'))
    else:
        print('-' * 50)
        print(f'{properties.day_limit}일치 폴더를 그대로 저장합니다.')
        print('-' * 50)
