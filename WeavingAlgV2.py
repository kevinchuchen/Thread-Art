from PIL import Image, ImageDraw, ImageOps
from tqdm import tqdm
import imageio
import collections
import numpy as np
import math as m
import cv2
import os
import sys

'''Function definition and classes'''
#Restart class
class RestartException(Exception):
    pass

#GIF creator
def GIFcreate(imgDir, outputDir):
    images = []
    sorting = []
    count = 0
    outputDir = outputDir + "\processGIF.gif"
    for fileName in os.listdir(imgDir):
        sorting.append(int(fileName[3:-4]))
        sorting.sort()
    for img in tqdm(sorting,desc = "Merging frames: ",unit = 'Frames'):
        sortedFileName = "IMG" + str(img) + ".png"
        filePath = os.path.join(imgDir, sortedFileName)
        images.append(imageio.imread(filePath))
        count += 1
    print("\nCreating GIF...")
    imageio.mimsave(outputDir, images)


# Crop image
def crop(height,width,image,fileName):
    height, width = image.shape[0:2]
    minEdge= min(height, width)
    topEdge = int((height - minEdge)/2)
    leftEdge = int((width - minEdge)/2)
    imgCropped = image[topEdge:topEdge+minEdge, leftEdge:leftEdge+minEdge]
    parent = os.path.dirname(os.path.abspath(fileName))
    return imgCropped

# Show image
def showImg(resized):
    print("Done.. Showing Image Preview. Close the Image Preview to continue saving the output file")
    cv2.imshow("Image Preview", resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
#Make folder to store frames in main picture's directory
def frameFolder(fileName,GIFflag):
    parentFolder = os.path.dirname(os.path.abspath(fileName)) #Move up one directory
    frameDir = os.path.splitext(parentFolder)[0] + '\FRAMES'
    if GIFflag == True:
        try:
            os.mkdir(frameDir)
        except OSError:
            print("Error creating frame folder(Is there an existing folder?)")
            input('Press Enter to exit')
            sys.exit()
        else:
            print("Creating frame folder...")
    else:
        print("Skipping frame folder(GIF creation is disabled)...")
    return frameDir,parentFolder
        
#Frame save to create GIF          
def getFrame(image, count, noOfLines, linePerFrame, frameDir):
    if count % linePerFrame == 0: #save every x frames(change linePerFrame)
        cv2.imwrite(frameDir +'\IMG' + str(count) + ".png", image)
##        print("Frame:" + str(count)+ "/" + str(noOfLines))
    count += 1
    return count
              
#cut image into a circle
def circularMask(PIXEL_WIDTH, resized, center, radius):
    x, y = np.ogrid[0:PIXEL_WIDTH,0:PIXEL_WIDTH]
    distFromCenter = np.sqrt((x - center[0])**2 + (y - center[1])**2)
    
    circleMask = distFromCenter >= radius
    resized[circleMask] = 255
    
    return resized

#Calculating the coordinates of each pin
def pinCoordinates(PIN_NO, center, radius):
    pinCoord = []
    seperationDeg = 360 / PIN_NO
    newDeg = 0
        
    while(newDeg < 360):
        newRad = m.radians((newDeg)) #convert to radians

        #finding co-ord of points on the circle    
        pinCoord.append((m.floor(radius*m.cos(newRad)+
                        center[0]),m.floor(radius*m.sin(newRad)+center[1])))
        
        #need to put list in list of pinCoordinate now
        newDeg += seperationDeg #add the seperation degree

    return pinCoord
###################################################################################

exitMessage = "Press Enter to exit"
helpMessage = """
------------------------------------------------------------------------------------------------------
Usage: python WeaveAlg -f 'FILE_PATH' -l 'LINE_NUMBER' -p 'PIN_NUMBER' -g(optional) 'LINE_PER_FRAME'

Eg: python WeaveAlg -f C:\\Users\\chuch\\Desktop\\TESTPIC.jpg -l 2500 -p 256 -g 10
Eg: python WeaveAlg -f abc.jpg -l 5000 -p 20 -g 30
Eg: python WeaveAlg -f cat.jpg -l 2345 -p 256
Note: File path must end with .jpg, .jpeg or .png extensions
------------------------------------------------------------------------------------------------------
"""

## ADD ERROR DETECTION IF PATH IS WRONG

print(helpMessage)
while True:
    try:
        userInput = list(filter(None, input('Enter input here(-h for help): ').strip().split(' ')))
        count = 0
        argNo = 0

        try:
                if userInput[0][0] == '-':
                    if userInput[0][1] == 'h' or userInput[0][1] == '?' or userInput[0][1] == 'help':
                        print(helpMessage)
                        raise RestartException
                    
                    if userInput[argNo][1:] == 'f' or userInput[argNo][1:] == 'F':
                        Input = userInput[argNo + 1]
                        if Input[-4:]!= '.png' and Input[-4:] != '.jpg' and Input[-5:] != '.jpeg':
                            print('File path must end with .png, .jpg or .jpeg extension')
                            raise RestartException
                        else:
                            try:
                                fileName = userInput[argNo + 1].strip()
                                argNo += 2
                            except IndexError:
                                print("File path not specified" )
                                raise RestartException
                    else:
                        print('Syntax -f not specified. Input -h for help')
                        raise RestartException
                    try:
                        if userInput[argNo][1:] == 'l' or userInput[argNo][1:] == 'L':
                            try:
                                try:
                                    noLine = int(userInput[argNo + 1])
                                    argNo += 2
                                except ValueError:
                                    print("Enter the number of lines(in numerical form). Input -h for help." )
                                    raise RestartException
                            except IndexError:
                                print("Number of lines not specified" )
                                raise RestartException

                        else:
                            print('Syntax -l not specified')
                            raise RestartException
                    except IndexError:
                        print("Syntax -l not specified")
                        raise RestartException
                            
                    try:
                        if userInput[argNo][1:] == 'p' or userInput[argNo][1:] == 'P':
                            try:
                                try:
                                    noPin = int(userInput[argNo+1])
                                    argNo += 2
                                except ValueError:
                                    print("Enter the number of pins(in numerical form). Input -h for help.")
                                    raise RestartException
                            except IndexError:
                                print("Number of pins not specified." )
                                raise RestartException
                        else:
                            print('Syntax -p not specified')
                            raise RestartException
                    except IndexError:
                        print("Syntax -p not specified")
                        raise RestartException
                    try:
                        if userInput[argNo][1:] == 'g' or userInput[argNo][1:] == 'G':
                            try:
                                try:
                                    linePerFrame = int(userInput[argNo + 1])
                                    GIF = True
                                    print('GIF creation enabled')
                                except ValueError:
                                    print("Enter the number of lines per frame(in numerical form). Input -h for help.")
                                    raise RestartException
                            except IndexError:
                                print("Number of lines per frame of GIF not specified")
                                raise RestartException
                            
                        else:
                            print('Unrecognized syntax, type -h for help')
                            raise RestartException
                    except IndexError:
                        print('GIF creation disabled')
                        GIF = False
                        break
                                
                else:
                    print("Input unknown, input -h for help")
                    raise RestartException
        except IndexError:
            print("No input found. Type -h for help")
            raise RestartException
        break
    except RestartException:
        continue

##################################################################

#Parameters to be changed
PIXEL_WIDTH = 500           #Size of resulting image
PIN_NO = noPin              #Number of pins needed
LINE_NO = noLine            #Number of lines needed
MIN_PREVIOUS_PINS = 20      #Minimum steps before the new pin can go back to same spot(To prevent infinite looping)
LINE_WIDTH = 15             #Thickness of line
MIN_DISTANCE = 20           #Minimum PIN distance between each line(Preventing short lines)
SCALE = 50                  #Higher number = Higher quality of render
FILE_NAME = fileName
count = 1
#Creating the folder for each frame
frameFolder = frameFolder(FILE_NAME, GIF)

#Sets the dimension
dim = (PIXEL_WIDTH,PIXEL_WIDTH)
center = [PIXEL_WIDTH/2, PIXEL_WIDTH/2]
radius = PIXEL_WIDTH/2 -1/2

#load image,crop, turn to grayscale, and resize image according to dimensions
img = cv2.imread(FILE_NAME,0)
crop = crop(img.shape[0],img.shape[1],img,FILE_NAME)
resized = cv2.resize(crop, dim)

#Mask the image to be circular
imgMasked = circularMask(PIXEL_WIDTH, resized, center, radius)
cv2.imwrite( frameFolder[1] + "\InputImage(processed).jpg", imgMasked)

#Defining the pin coordinates
pinCoord = pinCoordinates(PIN_NO, center, radius)

#Finding the coordinates between two points with minDistance
lineY = [None] * PIN_NO * PIN_NO
lineX = [None] * PIN_NO * PIN_NO

for point1 in range(PIN_NO): #point 1
    for point2 in range(point1 + MIN_DISTANCE, PIN_NO): #point 2 seperated by MIN_DISTANCE
        x0 = pinCoord[point1][0]##
        y0 = pinCoord[point1][1]##Coordinate of point 1

        x1 = pinCoord[point2][0]##
        y1 = pinCoord[point2][1]##Coordinate of point 2

        #calculate the hypotenuse distance between the two points
        hypDistance = int(m.sqrt((x1-x0)**2 + (y1-y0)**2))

        #Get the coordinates of the pixel between the points
        xCoords = np.linspace(x0, x1, hypDistance, dtype = int)
        yCoords = np.linspace(y0, y1, hypDistance, dtype = int)
        
        #Save the list of all the coordinates between two points
        #Eg: Coords of Point AB = Point BA
        lineY[point2*PIN_NO + point1] = yCoords
        lineY[point1*PIN_NO + point2] = yCoords
        lineX[point2*PIN_NO + point1] = xCoords
        lineX[point1*PIN_NO + point2] = xCoords

#Inverting the image for processing
#Black pixel corresponds to highest error
invertedImg = np.ones((imgMasked.shape)) * 255 - resized.copy()

#resultant image canvas
resultImg = np.ones(imgMasked.shape) * 255

#creating a line mask
lineMask = np.zeros(imgMasked.shape, np.float64)
result = np.ones((imgMasked.shape[0] * SCALE, imgMasked.shape[1]* SCALE), np.uint8) * 255

lineSequence = []
currentPin = 0
line = 0
previousPins = collections.deque(maxlen = MIN_PREVIOUS_PINS)

lineSequence.append(currentPin)#Adds the first pin in the list

for line in tqdm(range(LINE_NO),desc = "Creating lines: ", unit = 'Lines'):
    
    #resets maxError and bestPin every new line
    maxError = -m.inf
    bestPin  = -1
    
    #Loops and finds the next best pin in the sequence
    for difference in range(MIN_DISTANCE,PIN_NO-MIN_DISTANCE): #Goes through all the pins
        testPin = (currentPin + difference) % PIN_NO #picks the pins that are less than the PIN_NO
        if testPin in previousPins: #checks if the test pin was the previous pins
            continue
        
        #Finds the line coordinates between testPin and currentPin
        xCoords = lineX[testPin*PIN_NO + currentPin]
        yCoords = lineY[testPin*PIN_NO + currentPin]
        
        #Calculates the line error (More black pixels in original picture = higher error)
        lineError = np.sum(invertedImg[yCoords,xCoords])
        
        #Finds the highest error, and sets the test pin as a new best pin.
        if lineError > maxError:
            maxError = lineError
            bestPin = testPin
            
    #Adds the best pin in the sequence
    lineSequence.append(bestPin)

    #Reduce the error from the line
    xCoords = lineX[bestPin * PIN_NO + currentPin]#x & y coords of best line
    yCoords = lineY[bestPin * PIN_NO + currentPin]#

    #subtracts the line from the error
    lineMask.fill(0)
    lineMask[yCoords, xCoords] = LINE_WIDTH
    invertedImg = invertedImg - lineMask
    invertedImg.clip(0,255)#clips the error value to be 0-255
    
    #Draw the line (cv2.line(targetImg, (point1),(point2), colour, pixel width, type of bresenham line))
    cv2.line(result, (pinCoord[currentPin][0] * SCALE,pinCoord[currentPin][1] * SCALE),
            (pinCoord[bestPin][0] * SCALE,pinCoord[bestPin][1] * SCALE), color = 0, thickness = 4, lineType = 8)

    #get each frame for gif creation
    if GIF == True:
        resultImg = cv2.resize(result, imgMasked.shape, interpolation = cv2.INTER_AREA)
        count = getFrame(resultImg, count, LINE_NO,linePerFrame,frameFolder[0])   
##    print('Line:' + str(line+1) + '/' + str(LINE_NO))

    #Add line number and repeat
    line += 1
    previousPins.append(bestPin)
    currentPin = bestPin

#Input folder = Frame folder, Output folder = parent folder(of the original img directory)
if GIF == True:
    GIFcreate(frameFolder[0],frameFolder[1])

#Show and save output image
resultImg = cv2.resize(result, imgMasked.shape, interpolation = cv2.INTER_AREA)
showImg(resultImg)
print("Saving output image...")
cv2.imwrite( frameFolder[1] + "\output.jpg", result)

#output line Sequence file
print('Creating line sequence file...')
f = open(frameFolder[1] + "\Line Sequence.json","w+")
f.write(str(lineSequence))
f.close()

print('Completed!\n')
input('Press Enter to exit')
sys.exit()
