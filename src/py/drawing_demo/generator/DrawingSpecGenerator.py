import cv2

class DrawingSpecGenerator:

    def __init__(self):
        pass
    
    def get_edges(self, image_path):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        return edges