import cv2
import numpy as np
import HandTrackingModule as htm
import time
import pyautogui

pyautogui.FAILSAFE = False  # don't abort when cursor hits a screen corner
pyautogui.PAUSE = 0         # remove built-in delay after each call

##########################
wCam, hCam = 960, 540
frameR = 100        # Frame reduction (border margin)
smoothening = 7     # Smoothing factor
#########################


pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
lastClick = 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = pyautogui.size()  # Get screen width and height (in pixels)
# wScr = screen width, hScr = screen height
# print(wScr, hScr)

while True:
    # 1. Detect hand landmarks
    success, img = cap.read()
    if not success:
        break
    img = cv2.flip(img, 1)  # Flip image horizontally (mirror)
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # 2. Get the tip positions of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        # print(fingers)
        cv2.rectangle(
            img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2
        )

        # 4. Only index finger up: moving mode
        if fingers[1] == 1 and fingers[2] == 0:
            # 5. Convert coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            # np.interp(x, xp, fp) does linear interpolation:
            #   x  = the value to map
            #   xp = the input range (known x values)
            #   fp = the output range
            # Here x1/y1 is the fingertip position in the camera image,
            # (frameR, wCam - frameR) is the active area in the image,
            # and (0, wScr)/(0, hScr) is the screen coordinate range.
            # This maps finger movement in the camera to cursor movement on screen.

            # 6. Smooth the values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            # clocX/clocY = current smoothed position, plocX/plocY = previous frame position.
            # x3/y3 = target position after interpolation, smoothening = smoothing factor.
            # Each frame the cursor moves a fraction of the way toward the target;
            # a larger smoothening value means slower, smoother movement.
            # This slightly slows the cursor but reduces jitter.
            # If it feels too slow, reduce smoothening so the cursor follows faster.

            # 7. Move the mouse
            # Since the image is flipped, use clocX directly.
            # If you don't flip the image, use (wScr - clocX) instead.
            pyautogui.moveTo(clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 8. Index and middle fingers both up: clicking mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Measure the distance between the two fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            print(length)

            # 10. If the distance is short, click the mouse
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                if time.time() - lastClick > 0.5:  # 0.5s cooldown between clicks
                    pyautogui.click()
                    lastClick = time.time()

    # 11. Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime != pTime else 0
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # 12. Display
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()