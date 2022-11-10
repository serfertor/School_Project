from PIL import Image
import numpy as np
import cv2 as cv
import pytesseract
import vk_api
import requests


def scan (people):
    # параметры цветового фильтра
    hsv_min = np.array((143, 95, 75), np.uint8)
    hsv_max = np.array((179, 255, 255), np.uint8)
    
    
    fn = 'blankscan.png' # путь к файлу с картинкой
    img0 = cv.imread(fn)
    img = img0
    hsv = cv.cvtColor( img, cv.COLOR_BGR2HSV ) # меняем цветовую модель с BGR на HSV 
    thresh = cv.inRange( hsv, hsv_min, hsv_max ) # применяем цветовой фильтр
    
    # ищем контуры и заносим их в переменную contours
    contours, hierarchy = cv.findContours(thresh.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        
    img = cv.drawContours(img, contours, -1, (0,255,0), 3, cv.LINE_AA, hierarchy, 1)
    contours.clear()
    
    # параметры цветового фильтра (2)
    hsv1_min = np.array((0, 176, 153), np.uint8)
    hsv1_max = np.array((255, 255, 255), np.uint8)
    
    hsv = cv.cvtColor( img, cv.COLOR_BGR2HSV ) # меняем цветовую модель с BGR на HSV (2)
    thresh = cv.inRange ( hsv, hsv1_min, hsv1_max ) # применяем цветовой фильтр (2)
    
    # ищем контуры и заносим их в переменную contours (2)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    corners = []
    coord=[]
    # с помощью метода моментов высчитываем координаты специальных меток
    for c in contours:
        M = cv.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        print (cX,cY)
        corners.append ((cX,cY))
        coord.append(cX)
        coord.append(cY)
    crop = img0[coord[-1]:coord[1],coord[-2]:coord[0]] #вырезаем рабочую область
    cv.imwrite ("itog.jpg",crop)
    print (corners)
    itog = []
    k = 0
    q = -1
    sr = 0
    answ=[]
    for i in range (1,27):
        q+=1
        for j in range(0,people):
            a = crop [q:i][k:j]
            itog.append (pytesseract.image_to_string(a))
            k+=1
        for z in itog:
            if z == '+':
                w = 1
            elif z == '-':
                w = 0
            else:
                w = int(z)
            sr +=w
        answ.append (int(sr/people*100))
        itog = []
    meta = ''
    for i in range(1,len(answ)+1):
        meta+= str(i) + ')' + ' ' + str(answ[i-1]) + '%' + '\n'
    return meta
                 
    
    
token='****'

vk=vk_api.VkApi(token=token)
vk._auth_token()

value = {
    'offset':0,
    'count':20,
    'filter':'unanswered'
    }

while True:
    messages = vk.method('messages.getConversations',value)
    if messages['count']>=1:
        body = messages['items'][0]['last_message']['text']
        id = messages['items'][0]['last_message']['from_id']
        inu=[]
        a = str(body)
        inu= a.split(' ')
        
        try:
            urlt = messages['items'][0]['last_message']['attachments'][0]['photo']['sizes'][2]['url']
            p = requests.get(urlt)
            f = open('blankscan.jpg','wb')
            f.write(p.content)
            f.close()
            people = body.split('')[0]
            meta = scan(people)
            uploader = vk_api.upload.VkUpload(vk)
            data = {
                'peer_id':id,
                'random_id':0,
                'message' : meta
             }
            vk.method('messages.send', data)
        except:
            vk.method('messages.send',{'peer_id':id,'random_id':0,'message':'falses'})


