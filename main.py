import tkinter as tk
from tkinter import dialog, filedialog, ttk
from cv2 import cv2
from PIL import Image, ImageTk
import numpy as np
import os


def videoCapture():
    #读取摄像头捕捉到的图片
    flag, img1_BGR = camera.read()  #第二个参数是一帧一帧读取的图片
    if flag:
        img1_RGBA = cv2.cvtColor(img1_BGR,
                                 cv2.COLOR_BGR2RGBA)  #把读入的BGR格式转换成RGB格式
        return flag, img1_RGBA
    else:
        print('Please check your camera!')
        return False, None


def faceRecognition(img1_RGBA, path_of_facerecognition_package, face_param):
    #进行脸部识别，返回脸部相应参数
    faceCascade = cv2.CascadeClassifier(path_of_facerecognition_package)
    faces = faceCascade.detectMultiScale(img1_RGBA,
                                         scaleFactor=1.2,
                                         minNeighbors=5,
                                         minSize=(32, 32))
    #scaleFactor表示每次图像尺寸减小的比例minNeighbors表示每一个目标至少要被检测到3次才算是真的目标(因为周围的像素和不同的窗口大小都可以检测到人脸)minSize为目标的最小尺寸
    if isinstance(faces, np.ndarray):
        if isinstance(face_param, bool):
            face_param = list(faces[0][:3])
        elif abs(face_param[0] - faces[0][0]) > 15 or abs(face_param[1] -
                                                          faces[0][1]) > 15:
            face_param = list(faces[0][:3])
        return face_param
    else:
        print("Unable to recognize face!")
        return False


def outputAddedImg(img1_RGBA, label):
    #把图片转化成tkinter能输出的格式
    current_image = Image.fromarray(img1_RGBA)  #转换为pillow图像
    imgtk = ImageTk.PhotoImage(image=current_image)  #转换为与tkinter兼容的照片图像
    label.imgtk = imgtk
    label.config(image=imgtk)


def videoLoop():
    global img1_RGBA, face_param
    flag, img1_RGBA = videoCapture()
    path = r'D:\Anaconda\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml'
    if flag:
        face_param = faceRecognition(img1_RGBA, path, face_param)
        if face_param:
            spaceFlags = []
            for sticker in stickers:
                spaceFlag, img1_RGBA = sticker.addTwoImgs(
                    img1_RGBA, face_param)
                spaceFlags.append(spaceFlag)
            if not False in spaceFlags:
                outputAddedImg(img1_RGBA, ImgOutput)
    HatFamily.check()
    root.after(40, videoLoop)  #每40毫秒循环一次这个主程序


def save_file():
    #保存图片
    img1_BGR = cv2.cvtColor(img1_RGBA, cv2.COLOR_RGBA2BGR)
    choice = dialog.Dialog(
        None, {
            'title': 'File Modified',
            'text': '注意路径中不能含有中文字符！',
            'bitmap': 'warning',
            'default': 0,
            'strings': ('OK', 'Cancel')
        })
    if choice.num == 0:
        file_path = filedialog.asksaveasfilename(title=u'保存文件')
        try:
            print('保存文件：', file_path)
            cv2.imwrite(filename=file_path, img=img1_BGR)
            dialog.Dialog(
                None, {
                    'title': 'File Modified',
                    'text': '保存完成',
                    'bitmap': 'warning',
                    'default': 0,
                    'strings': ('OK', 'Cancle')
                })
            print('保存完成')
        except:
            print('Close by user.')


def open_file():
    #读取读者自定义的贴纸
    choice = dialog.Dialog(
        None, {
            'title': 'File Modified',
            'text': '图片路径中不能含有中文字符！',
            'bitmap': 'warning',
            'default': 0,
            'strings': ('OK', 'Cancle')
        })
    if choice == 0:
        global selfcustomizeSticker
        selfcustomizesticker_path = tk.filedialog.askopenfilename(
            title=u'打开贴图')
        selfcustomizeSticker = Sticker(name='selfcustomizeSticker',
                                       path=selfcustomizesticker_path,
                                       faceSpot=[0, 0],
                                       stickerSpot=[0, 0])
        selfcustomizeSticker.createButton()
        label = tk.Label(root, text="从此处按住开始拖动自定义贴纸")
        label.grid()
        label.bind("<B1-Motion>", moveimg)


def moveimg(event):
    selfcustomizeSticker.stickerSpot[0] = -event.x
    selfcustomizeSticker.stickerSpot[1] = -event.y


class StickerFamily:
    def __init__(self, familyname, contents):
        self.familyname = familyname
        self.contents = contents

    def createfamilyButton(self, row, column):
        self.v = tk.IntVar()
        self.button = tk.Checkbutton(root,
                                     text=self.familyname,
                                     variable=self.v,
                                     command=self.openToplevel)  #多选框
        self.button.grid(row=row, column=column, sticky='W' + 'E' + 'N' + 'S')

    def openToplevel(self):
        if self.v.get() == 1:  #如果相应的多选框被选中
            self.toplevel = tk.Toplevel()
            self.toplevel.title = self.familyname
            for content in self.contents:
                im = Image.open(content.path)
                content.img1 = ImageTk.PhotoImage(im)
                content.label = tk.Label(self.toplevel)
                content.label.grid()
                content.label.config(image=content.img1)
                content.v = tk.IntVar()
                content.button = tk.Checkbutton(self.toplevel,
                                                text=content.name,
                                                variable=content.v,
                                                command=content.addToImg)  #单选框
                content.button.grid(sticky='W' + 'E' + 'N' + 'S')
            self.toplevel.mainloop()

    def check(self):
        flag = False
        for Sticker in stickers:
            if Sticker in self.contents:
                flag = True
        if flag == False:
            self.v.set(0)
        else:
            self.v.set(1)


class Sticker:
    def __init__(self, name, path, faceSpot, stickerSpot):
        self.name = name
        self.path = path
        self.faceSpot = faceSpot
        self.stickerSpot = stickerSpot
        #faceSpot是脸部用于定位的点，输入一个list，含有两个值
        #定义脸部的左上角为脸部原点
        #第一个值是脸部原点到该点横向距离占脸部总宽度的比例
        #第二个值是脸部原点到该点纵向距离占脸部总高度的比例
        #stickerSpot是贴图用于定位的点，是预置好的数值
        #自定义贴图无预置数值，可以由使用者手动操作

    def createButton(self):
        self.v = tk.IntVar()
        self.button = tk.Checkbutton(root,
                                     text=self.name,
                                     variable=self.v,
                                     command=self.addToImg)
        self.button.grid(sticky='W' + 'E' + 'N' + 'S')

    def addToImg(self):
        if self.v.get() == 1:  #如果相应的多选框被选中
            stickers.append(self)
        else:
            stickers.remove(self)

    def addTwoImgs(self, img1_RGBA, face_param):
        #将贴纸贴到图片上
        self.img = cv2.imread(self.path)
        try:
            self.rows, self.cols = self.img.shape[:2]
        except:
            print('Fail in loading sticker!')
        self.getStickerPosition(face_param)
        if self.x1 >= 0 and self.x2 <= img1_RGBA.shape[
                1] and self.y1 >= 0 and self.y2 <= img1_RGBA.shape[0]:
            #制作掩膜
            roi = img1_RGBA[self.y1:self.y2, self.x1:self.x2]
            sticker_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(sticker_gray, 10, 255, cv2.THRESH_BINARY)
            del ret  #没什么意义，不想出现黄色报错而已
            mask_inv = cv2.bitwise_not(mask)
            img1_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
            self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGBA)
            dst = cv2.add(img1_bg, self.img)
            img1_RGBA[self.y1:self.y2, self.x1:self.x2] = dst
            return True, img1_RGBA
        else:
            print("No enough space for stickers!")
            return False, None

    def getStickerPosition(self, face_param):
        #将贴图与图片定位：在贴图和照片上各选取一个点，使得这两个点重合
        self.img_x = self.faceSpot[0] * face_param[2] + face_param[0]
        self.img_y = self.faceSpot[1] * face_param[2] + face_param[1]
        self.stickerSpot_x = self.stickerSpot[0]
        self.stickerSpot_y = self.stickerSpot[1]
        self.x1 = int(self.img_x - self.stickerSpot_x)
        self.y1 = int(self.img_y - self.stickerSpot_y)
        self.x2 = int(self.x1 + self.cols)
        self.y2 = int(self.y1 + self.rows)


if __name__ == '__main__':
    camera = cv2.VideoCapture(0)  #打开摄像头
    root = tk.Tk()
    root.title('FaceTube')
    ImgOutput = tk.Label(root)  #创建图形输出标签
    ImgOutput.grid(row=0, column=0, rowspan=10, columnspan=10)
    root.config(cursor="arrow")
    saveButton = tk.Button(root, text='保存文件', command=save_file)
    saveButton.grid(row=11, column=0)
    loadButton = tk.Button(root, text='自定义贴图', command=open_file)
    loadButton.grid(row=11, column=1)
    stickers = []  #记载需要放入图中的贴纸有哪几项
    Hat = Sticker(name='Hat',
                  path='Hat.png',
                  faceSpot=[0.5, 0],
                  stickerSpot=[169, 200])
    ChristmasHat = Sticker(name='ChristmasHat',
                           path='ChristmasHat.png',
                           faceSpot=[0.5, 0],
                           stickerSpot=[77, 154])
    HatFamily = StickerFamily('Hat', [ChristmasHat, Hat])
    HatFamily.createfamilyButton(0, 10)
    face_param = [0, 0, 0]
    videoLoop()
    root.mainloop()
    camera.release()
    cv2.destroyAllWindows()
