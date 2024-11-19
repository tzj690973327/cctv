import os
import cv2
import pathlib
import requests
from datetime import datetime

class ChangeDetection:
    result_prev = []
    HOST = 'http://127.0.0.1:8000'
    username = 'shaq'
    password = 'tzj690973327'
    token = ''
    title = ''
    text = ''
    
    def __init__(self, names): 
        self.result_prev = [0 for i in range(len(names))]
        
        res = requests.post(self.HOST + '/api-token-auth/', {
            'username': self.username,
            'password': self.password,
        })
        res.raise_for_status()
        self.token = res.json()['token']  # 토큰저장
        print(self.token)

    def add(self, names, detected_current, save_dir, image):
        self.title = ''
        self.text = ''
        change_flag = 0  # 변화감지플레그


        for i in range(len(self.result_prev)):
         if self.result_prev[i] == 0 and detected_current[i] == 1:  # 假设1表示变化
            change_flag = 1
            self.title = names[i]
            self.text += names[i] + ", "

        self.result_prev = detected_current[:]  # 保存当前检测状态

    # 如果发生变化，上传图片
        if change_flag == 1:
          self.send(save_dir, image)
       
    '''
        i = 0
        
        while i < len(self.result_prev):
            if self.result_prev[i] == 0 and detected_current[i] == 1:
                change_flag = 1
                self.title = names[i]
                self.text += names[i] + ", "
            
            i += 1

        self.result_prev = detected_current[:]  # 객체검출상태저장
            
        if change_flag == 1:
            self.send(save_dir, image)
     '''

    def send(self, save_dir, image):  # 移动了send方法的缩进，确保在类中定义
        now = datetime.now()
        now.isoformat()
        today = datetime.now()
        
        #save_path = os.getcwd() / save_dir / 'detected' / str(today.year) / str(today.month) / str(today.day)
        save_path = os.path.join(os.getcwd(), save_dir, 'detected', str(today.year), str(today.month), str(today.day))

        pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)
        
        #full_path = save_path / '{0}-{1}-{2}-{3}.jpg'.format(today.hour, today.minute, today.second, today.microsecond)
        full_path = os.path.join(
    save_path,
    '{0}-{1}-{2}-{3}.jpg'.format(today.hour, today.minute, today.second, today.microsecond)
)


        dst = cv2.resize(image, dsize=(320, 240), interpolation=cv2.INTER_AREA)
        cv2.imwrite(full_path, dst)
        
        # 인증이필요한요청에아래의headers를붙임
        headers = {'Authorization': 'JWT ' + self.token, 'Accept': 'application/json'}
        
        # Post Create
        data = {
            'title': self.title,
            'text': self.text, 
            'created_date': now,  # 修正了时间格式
            'published_date': now,
            'author': 1
        }

        print("Data being sent:", data)
        print("File path being sent:", full_path)
        # 确保文件存在
        if not os.path.exists(full_path):
            print(f"File does not exist: {full_path}")
            return
        
        file={"image": open(full_path, 'rb')}
        res=requests.post(self.HOST + '/api_root/Post/', data=data, files=file, headers=headers)  
        print(f"Response status: {res.status_code}, Response text: {res.text}")  # 添加打印
        print(res)


def capture_and_detect(names):
    cap = cv2.VideoCapture(0)  # 打开摄像头，0表示默认摄像头
    detector = ChangeDetection(names)  # 创建ChangeDetection实例
    detected_current = [0] * len(names)  # 初始假设没有检测到变化

    while True:
        ret, frame = cap.read()  # 获取摄像头画面
        if not ret:
            print("无法获取图像")
            break

        # 这里可以插入你的图像处理和检测算法
        # 假设没有检测到变化，检测到变化时设置 detected_current[i] = 1

        # 调用 add 方法进行变化检测和上传
        detector.add(names, detected_current, 'your_save_dir', frame)
        
        # 显示图像（可选）
        cv2.imshow('Camera', frame)

        # 按 'q' 键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
