from random import randint
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFile


FILEPATH = os.path.abspath(__file__)
FILEDIR = FILEPATH.replace(os.path.basename(FILEPATH),'')
ImageFile.LOAD_TRUNCATED_IMAGES = True


def getArea(x1,x2,x3, y1,y2,y3):
        return abs((x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2))/2)


def makeTriangle(points, color, img):
    D = ImageDraw.Draw(img)
    D.polygon(points, fill=color)


def score(OrgImg, ScoreImg):
    w1, h1 = ScoreImg.size
    if w1 != w or h1 != h:
        print("Error at Score funciton\n\n")
        exit()

    pix1=np.array(OrgImg, dtype=np.uint64).reshape((h, w, 3))[:, :, :3]
    pix2 = np.array(ScoreImg, dtype=np.uint64).reshape((h1, w1, 3))

    return np.sqrt(np.square(pix1 - pix2).sum(axis=-1)).sum()


def randPos(w, h):
    return (randint(0, w), randint(0, h))


def randColor(preBest=None):
    if not preBest:
        return (randint(0,255),randint(0,255),randint(0,255))
    return (preBest[3][0] + randint(-200,200), preBest[3][1] + randint(-200,200),preBest[3][2] + randint(-200,200))


def drawOutlined(t, outlineC, thickness, img, name):
    D = ImageDraw.Draw(img)
    D.polygon(t[:3],fill=t[3])
    D.line((t[0],t[1],t[2],t[0]),outlineC,thickness)
    img.save(name)


#func returning copy of an image resized to desired heigth (dh) keeping the proportions
def condvert(img, dh):
    w, h = img.size
    print("resizing from {}/{}".format(w,h))

    hRatio = dh/h
    dw = int(w*hRatio)
    img = img.resize((dw, dh), Image.ANTIALIAS)

    print("resized to {}/{}".format(dw,dh))
    return img


def inArea(lis, img):
    for i in lis:
        try:
            z = img[i[0],i[1]]
        except:
            return False
    return True

        
def get(w, h, img):
    rand1 = randPos(w, h)
    rand2 = (rand1[0]+randint(-100,100), rand1[1]+randint(-100,100))
    rand3 = (rand2[0]+randint(-100,100), rand2[1]+randint(-100,100))

    area = getArea(rand1[0],rand1[1],rand2[0],rand2[1],rand3[0],rand3[1])

    if area / (w*h) * 100 > 2  or not inArea([rand1,rand2,rand3], img):
        return get(w, h, img)

    return (rand1, rand2, rand3)


try:
    Real_IM = condvert(Image.open(FILEDIR+'Image.png', 'r'), 160)
except FileNotFoundError:
    print('[!] You gotta put a Image.png in this directory!')
    exit()


w, h = Real_IM.size

#message below in unnessesary - prints in condvert func say the same thing
print('> Converted the image to the dimensions of: %s x %s'%(w,h))


blank = Image.new('RGB', (w,h), (255,255,255))
cycles = 0
generations = 0
Bests = []
Scores = []
imgList = []

try:
    m = Image.open(FILEDIR+'best.png', 'r')
    if (w,h) != m.size:
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
if accuracy > 999:
    print('[!] The accuracy cannot be over 999!')
    exit()

cycleRate = accuracy*2
colorTry = round(accuracy/2.0)


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
        
        Norm = Image.open(FILEDIR+'best.png')

        rand = get(w,h,GG)

        for i2 in range(colorTry):
            if Bests == []:
                col = randColor()
            else:
                zBests = list(Bests)
                zBests.reverse()
                col = randColor(zBests[0])
            
            makeTriangle(rand, col, Norm)
            imgList.append([score(Real_IM, Norm), (rand[0],rand[1],rand[2],col)])
        cycles += 1
        count += 1

    b = 10**62
    b1 = []

    for i1 in imgList:
        if i1[0] < b:
            b = i1[0]
            b1 = i1[1]

    Bests.append(b1)
    
    DrawG = ImageDraw.Draw(GhostBest)
    DrawG.polygon(b1[:3], fill=b1[3])
    GhostBest.save(FILEDIR+'gbest.png')
    scoreG = score(Real_IM, GhostBest)

    if len(Scores) != 0:
        if scoreG <= Scores[len(Scores)-1]:
            Draw.polygon(b1[:3], fill=b1[3])
            Best.save(FILEDIR+'best.png')
        else:
            Best.save(FILEDIR+'best.png')
            print('\n\n--------------------\n\nSkipping and undoing Error --- Image (Undo) Error: %d '%(scoreG))
            continue
    else:
        Draw.polygon(b1[:3], fill=b1[3])
        Best.save(FILEDIR+'best.png')
    
    drawOutlined(b1, (255,0,0), 3, GhostBest, FILEDIR+'gbest.png')
    GhostBest.save(FILEDIR+'gbest.png')
    imgList = []
    generations += 1

    scoreR = score(Real_IM, Best)
    print('\n\n--------------------\n\nGeneration: %s \tCycles: %s\t Chose Best. Image error: %s'%(generations,cycles,scoreR))
    Scores.append(scoreR)
