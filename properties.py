'''
====================================================
공통 속성값 설정
====================================================
'''
# choose 'cam' or 'vision_cam'
cam_type = 'vision_cam'

# if U press q key, close program
esc = 114

# cv2.waitKey
frame_delay = 1

"""각종 설정 값"""
relay_port = 0 #USB-Relay포트
Reject_limit = 100 #리젝트 한계 기준
Save_img_limit = 100 #이미지 저장 한계 기준

"""데이터 저장 일수"""
day_limit = 183

"""사진 저장할 메인 폴더 지정"""
save_folder = '/home/nongshim/Desktop/Reject_imgs'

'''NG 이미지 창 x 죄표'''
small_x = int(int(659 * .8) * 2 + 30 + 90 + 20 + 20)

'''
====================================================
카메라별/위치별 속성값 설정
====================================================
'''

A_U = {
    'line': 'A',
    'window': '#12A.Line_Upper - Q : Quit',
    'small_x': 500,
    'cam_port': 0,
    'cam_setting': './camera_setting_AU.pfs',
    'relay_gate': 1,
    'relay_runtime': .15,
    'tray':[0] * 8,
    "batch_size": 1,
    "config_file": './burn/yolov4.cfg',
    "data_file": './burn/obj.data',
    "thresh": 0.2,
    "hier_thresh": .99,
    "nms": .1,
    "weights": './weights/yolov4_best.weights'
    }

A_D = {
    'line': 'A',
    'window': '#12A.Line_Down - Q : Quit',
    'small_x': 500,
    'cam_port': 1,
    'cam_setting': './camera_setting_AD.pfs',
    'relay_gate': 2,
    'relay_runtime': .15,
    'tray':[0] * 8,
    "batch_size": 1,
    "config_file": './burn/yolov4.cfg',
    "data_file": './burn/obj.data',
    "thresh": 0.2,
    "hier_thresh": .99,
    "nms": .1,
    "weights": './weights/yolov4_best.weights'
}

B_U = {
    'line': 'B',
    'window': '#12B.Line_Upper - Q : Quit',
    'small_x': 500,
    'cam_port': 2,
    'cam_setting': './camera_setting_BU.pfs',
    'relay_gate': 3,
    'relay_runtime': .15,
    'tray':[0] * 8,
    "batch_size": 1,
    "config_file": './burn/yolov4.cfg',
    "data_file": './burn/obj.data',
    "thresh": 0.2,
    "hier_thresh": .99,
    "nms": .1,
    "weights": './weights/yolov4_best.weights'
    }

B_D = {
    'line': 'B',
    'window': '#12B.Line_Down - Q : Quit',
    'small_x': 500,
    'cam_port': 3,
    'cam_setting': './camera_setting_BD.pfs',
    'relay_gate': 4,
    'relay_runtime': .15,
    'tray':[0] * 8,
    "batch_size": 1,
    "config_file": './burn/yolov4.cfg',
    "data_file": './burn/obj.data',
    "thresh": 0.2,
    "hier_thresh": .99,
    "nms": .1,
    "weights": './weights/yolov4_best.weights'
}


if __name__ == "__main__":
    print("불러오고 싶은 라인의 번호를 입력해주세요.")
