import cv2
import numpy as np

#设定阈值，HSV空间
blueLower = np.array([20, 43, 46])
blueUpper = np.array([50, 255, 255])

#打开摄像头
camera = cv2.VideoCapture(0)
import  RPi.GPIO as GPIO
import time

PWMA = 18
AIN1 = 22
AIN2 = 27

PWMB = 23
BIN1 = 25
BIN2 = 24

def t_up(speed,t_time):
	L_Motor.ChangeDutyCycle(speed)
	GPIO.output(AIN2,False)#AIN2
	GPIO.output(AIN1,True) #AIN1

	R_Motor.ChangeDutyCycle(speed)
	GPIO.output(BIN2,False)#BIN2
	GPIO.output(BIN1,True) #BIN1
	time.sleep(t_time)
        
def t_stop(t_time):
	L_Motor.ChangeDutyCycle(0)
	GPIO.output(AIN2,False)#AIN2
	GPIO.output(AIN1,False) #AIN1

	R_Motor.ChangeDutyCycle(0)
	GPIO.output(BIN2,False)#BIN2
	GPIO.output(BIN1,False) #BIN1
	time.sleep(t_time)
        
def t_down(speed,t_time):
	L_Motor.ChangeDutyCycle(speed)
	GPIO.output(AIN2,True)#AIN2
	GPIO.output(AIN1,False) #AIN1

	R_Motor.ChangeDutyCycle(speed)
	GPIO.output(BIN2,True)#BIN2
	GPIO.output(BIN1,False) #BIN1
	time.sleep(t_time)

def t_left(speed,t_time):
	L_Motor.ChangeDutyCycle(speed)
	GPIO.output(AIN2,True)#AIN2
	GPIO.output(AIN1,False) #AIN1

	R_Motor.ChangeDutyCycle(speed)
	GPIO.output(BIN2,False)#BIN2
	GPIO.output(BIN1,True) #BIN1
	time.sleep(t_time)

def t_right(speed,t_time):
	L_Motor.ChangeDutyCycle(speed)
	GPIO.output(AIN2,False)#AIN2
	GPIO.output(AIN1,True) #AIN1

	R_Motor.ChangeDutyCycle(speed)
	GPIO.output(BIN2,True)#BIN2
	GPIO.output(BIN1,False) #BIN1
	time.sleep(t_time)
        
GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM)
GPIO.setup(AIN2,GPIO.OUT)
GPIO.setup(AIN1,GPIO.OUT)
GPIO.setup(PWMA,GPIO.OUT)

GPIO.setup(BIN1,GPIO.OUT)
GPIO.setup(BIN2,GPIO.OUT)
GPIO.setup(PWMB,GPIO.OUT)

L_Motor= GPIO.PWM(PWMA,100)
L_Motor.start(0)

R_Motor = GPIO.PWM(PWMB,100)
R_Motor.start(0)

#创建一个线程类
def mRange():
    while True:
        # 读取帧
        (ret, frame) = camera.read()
        frame = cv2.flip(frame, 1, dst=None)  # 水平翻转镜像
        # 判断是否成功打开摄像头
        if not ret:
            print('No Camera')
            break
        # 转到HSV空间
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # 根据阈值构建掩膜
        mask = cv2.inRange(hsv, blueLower, blueUpper)
        # 腐蚀操作
        mask = cv2.erode(mask, None, iterations=2)
        # 膨胀操作，其实先腐蚀再膨胀的效果是开运算，去除噪点
        mask = cv2.dilate(mask, None, iterations=2)
        # 轮廓检测
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        # 如果存在轮廓
        if len(cnts) > 0:
            # 找到面积最大的轮廓
            c = max(cnts, key=cv2.contourArea)
            # 确定面积最大的轮廓的矩形
            x, y, w, h = cv2.boundingRect(c)
            #计算目标距离
            distance = (1024/w)*2.54 #大致距离，需要结合镜头参数再次确定
            position_x=x+w/2 # 横坐标最大640
            position_y=y+h/2 # 纵坐标最大480
            
            distance_num = str(distance)
            position_x_num = str(position_x)
            position_y_num = str(position_y)
            
            # 输出距离
            print("Distance:",distance_num)
            if distance>15 and distance<200 :
                t_up(100,0.05)
                t_stop(0.01)
                if position_x<220:
                    t_right(50,0.02)
                    t_stop(0.01)
                if position_x>420:
                    t_left(50,0.02)
                    t_stop(0.01)
            
            # 输出宽度
            print("Width:",w)
            
            # 输出目标物中心点坐标
            print("x:",position_x)
            print("y:",position_y)

            # 显示矩形框
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # 显示距离和中心坐标
            cv2.putText(frame, distance_num, (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, position_x_num, (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, position_y_num, (15, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            t_right(40,0.02)
            t_stop(0.01)
        cv2.imshow('Frame', frame)
        cv2.waitKey(1)
        # 摄像头释放
if __name__ == '__main__':
    mRange()
 