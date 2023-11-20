import sys
sys.path.append("/app/app/k_fashion_detection")

from detect_model_hold import KF_Detector
from PIL import Image
image = Image.open('data/images/bus.jpg')
# print(type(image))

detector = KF_Detector(device="cuda")
print(detector.predict(image, nosave=False))