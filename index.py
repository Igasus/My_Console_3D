import os
import math
import time
import keyboard
from threading import Thread




PositionX = 0
PositionY = 0
DirectionAngle = 0

StepLength = 0.05
RotationAngle = 1.5 * math.pi / 180

RenderRayStepLength = 0.015
FieldOfVision = math.pi / 2
RangeOfVision = 8
ScreenWidth = 130
ScreenHeight = 40

MinKeyReadDelay = 0.05
MinRenderAndPrintDelay = 0.05

BlockHeight = 1
BlockSymbols = [ '█', '▓', '▒', '░' ]
FloorSymbols = [ 'x', '=', '~', '-', '.' ]




MapUrl = "map.txt"
Map = []
endGame = False




class ReadKeysThread(Thread):
    def __init__(self, delay):
        self.Delay = delay
        Thread.__init__(self)

    def run(self):
        while not endGame:
            ReadKeys()
            time.sleep(self.Delay)


class RenderThread(Thread):
    def __init__(self, delay):
        self.Delay = delay
        Thread.__init__(self)

    def run(self):
        global PositionX
        global PositionY
        global DirectionAngle
        global FieldOfVision
        global RangeOfVision

        while not endGame:
            screen = Render(PositionX, PositionY, DirectionAngle, FieldOfVision, RangeOfVision)
            PrintScreen(screen)
            time.sleep(self.Delay)




def Start():
    global MinKeyReadDelay
    global MinRenderAndPrintDelay

    ReadMap(MapUrl)

    readKeysThread = ReadKeysThread(MinKeyReadDelay)
    renderThread = RenderThread(MinRenderAndPrintDelay)

    readKeysThread.start()
    renderThread.start()



def ReadMap(url):
    global Map
    global PositionX
    global PositionY

    mapFile = open(url)
    mapLines = mapFile.readlines()
    for y in range(len(mapLines)):
        column = []
        for x in range(0, len(mapLines[y])):
            if mapLines[y][x] == '@':
                PositionX = x + 0.5
                PositionY = y + 0.5
                column.append('.')
            else:
                column.append(mapLines[y][x])
        Map.append(column)
    if PositionX == 0 and PositionY == 0:
        raise Exception("Missed '@' sign in map")










def ReadKeys():
    global Map
    global endGame
    global PositionX
    global PositionY
    global StepLength
    global DirectionAngle
    global RotationAngle


    if keyboard.is_pressed("esc"):
        endGame = True
        return

    if keyboard.is_pressed("left"):
        DirectionAngle -= RotationAngle
        if RotationAngle < 0:
            DirectionAngle += 2 * math.pi

    elif keyboard.is_pressed("right"):
        DirectionAngle += RotationAngle
        if RotationAngle >= 2 * math.pi:
            DirectionAngle -= 2 * math.pi


    def MakeStep(hotkey):
        global PositionX
        global PositionY
        global DirectionAngle

        angleShift = 0
        if hotkey == "d":
            angleShift = math.pi / 2
        elif hotkey == "s":
            angleShift = math.pi
        elif hotkey == "a":
            angleShift = 3 * math.pi / 2

        xShift = StepLength * math.cos(DirectionAngle + angleShift)
        yShift = StepLength * math.sin(DirectionAngle + angleShift)
        if Map[int(PositionX + xShift)][int(PositionY + yShift)] == '.':
            PositionX += xShift
            PositionY += yShift

    if keyboard.is_pressed("w"):
        MakeStep("w")
    elif keyboard.is_pressed("s"):
        MakeStep("s")

    if keyboard.is_pressed("a"):
        MakeStep("a")
    elif keyboard.is_pressed("d"):
        MakeStep("d")










def Render(PositionX, PositionY, DirectionAngle, FieldOfVision, RangeOfVision):
    global Map
    global RenderRayStepLength
    global ScreenWidth
    global ScreenHeight
    global BlockHeight
    global BlockSymbols
    global FloorSymbols

    toScreenDistance = ScreenWidth / (2 * math.tan(FieldOfVision / 2))
    toFloorStartDistance = toScreenDistance * BlockHeight / ScreenHeight

    def GetRenderRayLength(rayAngle):
        global PositionX
        global PositionY

        rayLength = RenderRayStepLength
        while rayLength <= RangeOfVision:
            xShift = rayLength * math.cos(rayAngle)
            yShift = rayLength * math.sin(rayAngle)
            if Map[int(PositionX + xShift)][int(PositionY + yShift)] == '#':
                return rayLength
            rayLength += RenderRayStepLength

        return -1

    screen: List[List[str]] = []

    def MakeCorner(columnIndex):
        global BlockSymbols

        for y in range(len(screen[columnIndex])):
            for symbol in BlockSymbols:
                if screen[columnIndex][y] == symbol:
                    screen[columnIndex][y] = '|'
                    break

    def GetCos(vector1X, vector1Y, vector2X, vector2Y):
        scalarProduct = vector1X * vector2X + vector1Y * vector2Y
        vector1Length = math.sqrt(vector1X ** 2 + vector1Y ** 2)
        vector2Length = math.sqrt(vector2X ** 2 + vector2Y ** 2)
        result = scalarProduct / (vector1Length * vector2Length)
        return result

    angleShift = FieldOfVision / ScreenWidth
    rayAngle = DirectionAngle - FieldOfVision / 2 + angleShift / 2
    previousCornerX = -1
    previousCornerY = -1
    maxCos = -1
    maxCosColumnIndex = -1
    while rayAngle < DirectionAngle + FieldOfVision / 2:
        column = [' '] * ScreenHeight
        rayLength = GetRenderRayLength(rayAngle)

        rayPositionX = PositionX + rayLength * math.cos(rayAngle)
        rayPositionY = PositionY + rayLength * math.sin(rayAngle)

        if rayLength > 0:
            cornerX = math.floor(rayPositionX + 0.5)
            cornerY = math.floor(rayPositionY + 0.5)


            if previousCornerX != -1 and previousCornerY != -1 and (cornerX != previousCornerX or cornerY != previousCornerY):
                if maxCosColumnIndex >= 0.95:
                    MakeCorner(maxCosColumnIndex)
                maxCos = -1

            currentCos = GetCos(cornerX - PositionX, cornerY - PositionY, rayLength * math.cos(rayAngle), rayLength * math.sin(rayAngle))
            if (currentCos > maxCos):
                maxCos = currentCos
                maxCosColumnIndex = len(screen)

            previousCornerX = cornerX
            previousCornerY = cornerY
        else:
            if previousCornerX != -1 or previousCornerY != -1:
                if maxCosColumnIndex >= 0.95:
                    MakeCorner(maxCosColumnIndex)
                previousCornerX = -1
                previousCornerY = -1
                maxCos - 1


        blockProjectionHeight = min(BlockHeight * toScreenDistance / rayLength, ScreenHeight)
        if (rayLength > 0):
            blockSymbolIndex = math.ceil(len(BlockSymbols) * rayLength / RangeOfVision) - 1
            for y in range(math.floor(ScreenHeight / 2 - blockProjectionHeight / 2), math.ceil(ScreenHeight / 2 + blockProjectionHeight / 2)):
                column[int(y)] = BlockSymbols[blockSymbolIndex]
                y += 1
        else:
            blockProjectionHeight = BlockHeight * toScreenDistance / RangeOfVision

        for y in range(math.ceil(ScreenHeight / 2 + blockProjectionHeight / 2), ScreenHeight):
            floorSymbolIndex = int(len(FloorSymbols) * (toScreenDistance * BlockHeight / (2 * y + 2 - ScreenHeight)) / RangeOfVision)
            column[y] = FloorSymbols[floorSymbolIndex]

        screen.append(column)
        rayAngle += angleShift

    return screen










def PrintScreen(screen):
    def clear():
        if os.name == 'nt':
            os.system('cls')

        else:
            os.system('clear')

    global ScreenWidth
    global ScreenHeight

    screenString = ""
    for y in range(ScreenHeight):
        for x in range(ScreenWidth):
            screenString += screen[x][y]
        screenString += '\n'

    clear()
    print(screenString)





Start()