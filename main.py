import math
import random
import sys
import os
import numpy as np

from PIL import Image, ImageDraw, ImageFile


FILEPATH = os.path.abspath(__file__)
FILEDIR = FILEPATH.replace(os.path.basename(FILEPATH),'')
ImageFile.LOAD_TRUNCATED_IMAGES = True


def getArea(x1,x2,x3, y1,y2,y3):
    return abs((x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2))/2)


def MakeTriangle(xy1, xy2, xy3, color, im):
    D = ImageDraw.Draw(im)
    D.polygon([xy1,xy2,xy3], fill=color)
    return im


def getDiffrence(rgb1, rgb2):
    return math.sqrt((rgb2[0]-rgb1[0])**2 + (rgb2[1]-rgb1[1])**2 + (rgb2[2]-rgb1[2])**2)


def score(OrgImg, ScoreImg):
    w, h = OrgImg.size
    w1, h1 = ScoreImg.size

    if w1 != w or h1 != h:
        print("Error at Score funciton\n\n")
        exit()

    pix1=np.array(OrgImg, dtype=np.uint64).reshape((h, w, 3))[:, :, :3]
    pix2 = np.array(ScoreImg, dtype=np.uint64).reshape((h1, w1, 3))

    diff = (np.sqrt(np.square(pix1 - pix2).sum(axis=-1)).sum())



    return diff

def GetPrevious():
    return Image.open(FILEDIR+'best.png')


def randPos(w, h):
    return (random.randint(0, w), random.randint(0, h))


def randColor(preBest=None):
    if preBest == None or True:
        return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    else:
        return (preBest[3][0] + random.randint(-200,200), preBest[3][1] + random.randint(-200,200),preBest[3][2] + random.randint(-200,200))


def drawOutlined(xy1, xy2, xy3, c, outlineC, thickness, im, name):
    D = ImageDraw.Draw(im)
    D.polygon([xy1,xy2,xy3],fill=c)
    D.line((xy1,xy2),outlineC,thickness)
    D.line((xy2,xy3),outlineC,thickness)
    D.line((xy3,xy1),outlineC,thickness)
    im.save(name)


def condvert(imggg, pixelo):
    he = pixelo
    img = Image.open(imggg)

    print("resizing from {}/{}".format(img.size[0],img.size[1]))
    w, h = img.size
    wpercent = he / float(h)
    hsize = int(float(w) * float(wpercent))
    img = img.resize((hsize, he), Image.ANTIALIAS)
    print("resized to {}/{}".format(img.size[0],img.size[1]))
    img.save(imggg)


try:
    condvert(FILEDIR+'Image.png', 160)
    Real_IM = Image.open(FILEDIR+'Image.png', 'r')
except FileNotFoundError:
    print('[!] You gotta put a Image.png in this directory!')
    exit()

w, h = Real_IM.size
print('> Converted the image to the dimensions of: %s x %s'%(w,h))

blank = Image.new('RGB', (w,h), (255,255,255))



cycles = 0
generations = 0
Bests = []
Scores = []

try:
    
    m = Image.open(FILEDIR+'best.png', 'r')
    w1 , h1 = m.size
    if w1 != w or h1 != h:
        blank.save(FILEDIR+'best.png')
        blank.save(FILEDIR+'gbest.png')
except FileNotFoundError:
    blank.save(FILEDIR+'best.png')

try:
    Best = Image.open(FILEDIR+'best.png')
    m = open(FILEDIR+'gbest.png', 'r')
    Scores.append(score(Real_IM,Best))
except FileNotFoundError:
    blank.save(FILEDIR+'gbest.png')


Draw = ImageDraw.Draw(Best)

accuracy = 5
if accuracy >= 1000:
    print('[!] The accuracy cannot be over 999!')
    exit()

cycleRate = accuracy*2
colorTry = accuracy
imgList = []



while True:
    RM = Image.open(FILEDIR+'best.png').load()
    GhostBest = Image.new('RGB', (w,h), (255,255,255))
    GG = GhostBest.load()
    
    for x1 in range(w):
        for y1 in range(h):
            GG[x1,y1] = RM[x1,y1]
    count = 0
    
    jobs = []
    print('starting gen...')
    for i1 in range(cycleRate):
        def inArea(lis, img):
            for i in lis:
                try:
                    z = img[i[0],i[1]]
                except:
                    return False
            return True
                
        def get(w, h, img):
            #try:
            rand1 = randPos(w, h)
            rand2 = (rand1[0]+random.randint(-100,100), rand1[1]+random.randint(-100,100))
            rand3 = (rand2[0]+random.randint(-100,100), rand2[1]+random.randint(-100,100))

            area = getArea(rand1[0],rand1[1],rand2[0],rand2[1],rand3[0],rand3[1])

            if ((float(area) / (w*h))*100) > 2  or not inArea([rand1,rand2,rand3], img):
                return get(w, h, img)
            else:
                return (rand1, rand2, rand3)
            #except:
                #print(e)
                #exit()
        
        Norm = Image.open(FILEDIR+'best.png')

        rand = get(w,h,GG)
        rand1 = rand[0]
        rand2 = rand[1]
        rand3 = rand[2]

        for i2 in range(colorTry):
            if Bests == []:
                col = randColor()
            else:
                zBests = list(Bests)
                zBests.reverse()
                col = randColor(zBests[0])
            
            img = MakeTriangle(rand1, rand2, rand3, col, Norm)
            imgList.append([score(Real_IM,img), (rand1,rand2,rand3,col)])
        cycles += 1
        count += 1

    b = 100000000000000000000000000000000000000000000000000000
    b1 = []

    for i1 in imgList:
        if i1[0] < b:
            b = i1[0]
            b1 = i1[1]

    Bests.append(b1)
    
    DrawG = ImageDraw.Draw(GhostBest)
    DrawG.polygon([b1[0],b1[1],b1[2]], fill=b1[3])
    GhostBest.save(FILEDIR+'gbest.png')
    scoreG = score(Real_IM, GhostBest)

    if len(Scores) != 0:
        if scoreG <= Scores[len(Scores)-1]:
            Draw.polygon([b1[0],b1[1],b1[2]], fill=b1[3])
            Best.save(FILEDIR+'best.png')
        else:
            Best.save(FILEDIR+'best.png')
            print('\n\n--------------------\n\nSkipping and undoing Error --- Image (Undo) Error: %d '%(scoreG))
            continue
    else:
        Draw.polygon([b1[0],b1[1],b1[2]], fill=b1[3])
        Best.save(FILEDIR+'best.png')
    
    drawOutlined(b1[0],b1[1],b1[2],b1[3], (255,0,0), 3, GhostBest, FILEDIR+'gbest.png')
    GhostBest.save(FILEDIR+'gbest.png')
    imgList = []
    generations += 1

    scoreR = score(Real_IM, Best)
    print('\n\n--------------------\n\nGeneration: %s \tCycles: %s\t Chose Best. Image error: %s'%(generations,cycles,scoreR))
    Scores.append(scoreR)
