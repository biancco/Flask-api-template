# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
import argparse
import os
import platform
import sys
import yaml
from pathlib import Path
from PIL import Image

import time
from time import localtime, strftime

import torch
import numpy

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams, LoadByteImages
from utils.general import (LOGGER, Profile, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, smart_inference_mode

class KF_Detector():
    def __init__(self,
                 weights = 'app/k_fashion_detection/weights/best.pt',
                 data = 'app/k_fashion_detection/data/k-fashion_2.yaml',
                #  weights = 'weights/best.pt',
                #  data = 'data/k-fashion_2.yaml',
                 device = "cpu",
                 dnn = False,
                 half = False,
                 extract = True
                 ):
        # self.device = select_device(device)
        self.device = torch.device(device)
        self.model = DetectMultiBackend(weights, device=self.device, dnn=dnn, data=data, fp16=half)
        self.data = data
        self.extract = extract        
        
    '''
    Expected output example:
    [['dog', [0.21, 64.61, 383.16, 494.14], 0.999], ['dog', [328.2, 125.86, 714.74, 461.77], 0.995]]
    '''
    @smart_inference_mode()
    def predict(self,
            # weights=ROOT / 'yolov5s.pt',  # model.pt path(s)
            # source=ROOT / 'data/images',  # file/dir/URL/glob, 0 for webcam
            
            image:Image,     # image must be delivered by caller
            
            # data=ROOT / 'data/coco128.yaml',  # dataset.yaml path
            imgsz=(640, 640),  # inference size (height, width)
            conf_thres=0.25,  # confidence threshold
            iou_thres=0.45,  # NMS IOU threshold
            max_det=1000,  # maximum detections per image
            # device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
            # view_img=False,  # show results
            save_txt=False,  # save results to *.txt
            save_conf=False,  # save confidences in --save-txt labels
            save_crop=False,  # save cropped prediction boxes
            nosave=True,  # do not save images/videos
            classes=None,  # filter by class: --class 0, or --class 0 2 3
            agnostic_nms=False,  # class-agnostic NMS
            augment=False,  # augmented inference
            visualize=False,  # visualize features
            update=False,  # update all models
            project=ROOT / 'runs/server',  # save results to project/name
            # name='exp',  # save results to project/name
            exist_ok=False,  # existing project/name ok, do not increment
            line_thickness=3,  # bounding box thickness (pixels)
            hide_labels=False,  # hide labels
            hide_conf=False,  # hide confidences
            # half=False,  # use FP16 half-precision inference
            # dnn=False,  # use OpenCV DNN for ONNX inference
            vid_stride=1,  # video frame-rate stride
            # extract=False
    ):
        model = self.model
        device = self.device
        extract = self.extract
        data = self.data
        
        # Time as Path
        t_local = localtime(time.time())
        time_format = '%Y-%m-%d_%H:%M:%S'
        time_str = strftime(time_format,t_local)
        name = time_str
        save_img = not nosave
        webcam = False

        # Directories
        save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # increment run
        (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

        # Load model
        # device = select_device(device)
        # model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
        stride, names, pt = model.stride, model.names, model.pt
        if 'k-fashion' in data:
            if isinstance(data, (str, Path)):
                with open(data) as f:
                    data = yaml.safe_load(f)  # dictionary
                names2 = data['names2']
        else:
            names2 = None
        imgsz = check_img_size(imgsz, s=stride)  # check image size
        path = 'clinet_img.jpg'

        # Dataloader
        image = numpy.array(image)
        image = image[:, :, ::-1]  # BGR2RGB
        dataset = LoadByteImages(image, path, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
        bs = 1  # batch_size

        # Run inference
        model.warmup(imgsz=(1 if pt else bs, 3, *imgsz))  # warmup
        seen, windows, dt = 0, [], (Profile(), Profile(), Profile())
        for path, im, im0s, vid_cap, s in dataset:
            with dt[0]:
                im = torch.from_numpy(im).to(device)
                im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
                im /= 255  # 0 - 255 to 0.0 - 1.0
                if len(im.shape) == 3:
                    im = im[None]  # expand for batch dim
                    

            # Inference
            with dt[1]:
                visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
                pred = model(im, augment=augment, visualize=visualize, extract=extract)
            
                
            # NMS
            with dt[2]:
                ####### EXTRACT FEATURES #######
                # 특정 사진의 경우 여기서 에러가 발생함 (ex. tests/test.jpg)
                if extract:
                    pred, features = non_max_suppression(
                        pred[:2], conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det, features=pred[2:],
                        nc2=len(names2) if names2 else None
                    )
                ################################
                else:
                    pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

            # Second-stage classifier (optional)
            # pred = utils.general.apply_classifier(pred, classifier_model, im, im0s)
            
            # Process predictions
            for i, det in enumerate(pred):  # per image
                seen += 1
                if webcam:  # batch_size >= 1
                    p, im0, frame = path[i], im0s[i].copy(), dataset.count
                    s += f'{i}: '
                else:
                    p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)

                p = Path(p)  # to Path
                save_path = str(save_dir / p.name)  # im.jpg
                txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # im.txt
                s += '%gx%g ' % im.shape[2:]  # print string
                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                imc = im0.copy() if save_crop else im0  # for save_crop
                annotator = Annotator(im0, line_width=line_thickness, example=str(names))
                if len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                    # Return results
                    res_tuple = []

                    for j in range(det.size(0)):
                        det2 = det.detach().cpu().numpy()
                        det2 = [float(i) for i in det2[j]]
                        xyxy = list(det2[:4])
                        conf1, cls1, conf2, cls2 = det2[4:8]
                        cls1 = names[int(cls1)]     # 옷
                        cls2 = names2[int(cls2)]    # 색상
                    
                        box = [round(i, 2) for i in xyxy]
                        res_tuple.append((cls1, round(conf1, 2), cls2, round(conf2, 2), box))
                    
                    # Write results
                    # for *xyxy, conf, cls in reversed(det):
                    for j in range(det.size(0)):
                        xyxy, conf, cls = list(reversed(det)[j, :4]), reversed(det)[j, 4], reversed(det)[j, 5]
                        if names2:
                            conf2, cls2 = reversed(det)[j, 6], reversed(det)[j, 7]
                        if save_txt:  # Write to file
                            xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                            line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                            with open(f'{txt_path}.txt', 'a') as f:
                                f.write(('%g ' * len(line)).rstrip() % line + '\n')

                        if save_img or save_crop:  # Add bbox to image
                            c = int(cls)  # integer class
                            label_str = f'{names[c]} {names2[int(cls2)]} {conf:.2f}' if names2 else f'{names[c]} {conf:.2f}'
                            label = None if hide_labels else (names[c] if hide_conf else label_str)
                            annotator.box_label(xyxy, label, color=colors(c, True))
                        if save_crop:
                            save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg', BGR=True)

                # Save results (image with detections)
                if save_img:
                    im0 = annotator.result()
                    if dataset.mode == 'image':
                        cv2.imwrite(save_path, im0)
                
                
                # Reponse
                return res_tuple
