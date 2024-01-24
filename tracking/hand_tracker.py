# Beginning test code from:
# https://www.section.io/engineering-education/creating-a-hand-tracking-module/
# install mediapipe : pip3 install mediapipe
# do this shit : https://stackoverflow.com/questions/71759248/importerror-cannot-import-name-builder-from-google-protobuf-internal
# and it works. 


import cv2
import mediapipe as mp

class handTracker():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5,modelComplexity=1,trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,self.modelComplex,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        

        print('\033[92m', "Hand tracker initialized",  '\033[0m')


    def handsFinder(self,image,draw=True):
        imageRGB = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imageRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:

                if draw:
                    self.mpDraw.draw_landmarks(image, handLms, self.mpHands.HAND_CONNECTIONS)
        return image

    def positionFinder(self,image, handNo=0, draw=True):
        lmlist = []
        if self.results.multi_hand_landmarks:
            Hand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(Hand.landmark):
                h,w,c = image.shape
                cx,cy = int(lm.x*w), int(lm.y*h)
                lmlist.append([id,cx,cy])
            if draw:
                cv2.circle(image,(cx,cy), 15 , (255,0,255), cv2.FILLED)

        return lmlist

def track_hands(frame, tracker):
    #cap = cv2.VideoCapture(0)
    #tracker = handTracker()

    #success,image = cap.read()
    frame = tracker.handsFinder(frame)
    lmList = tracker.positionFinder(frame)
    if len(lmList) != 0:
        print('\033[92m', lmList[4], '\033[0m')

    
    
if __name__ == "__main__":
    
    cap = cv2.VideoCapture(0)
    track_hands(cap)
