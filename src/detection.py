import cv2
import threading
import time
import torch

from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

def send_email():
  print("Correo enviado, se detecto!")

class ObjectDetection:
  def __init__(self, source, model, **kwargs):
    # Initializes an ObjectDetection instance with a given camera index
    self.capture = cv2.VideoCapture(source)
    self.run = False
    self.current_frame = None
    self.loop_thread = None
    self.lock = threading.Lock()
    self.email_send = False
    self.model = YOLO(model)

    # Model information
    self.config = {
      "stream": False,
      "conf": 0.8,
      "iou": 0.7,
      "imgsz": 320,
      "device": 0,
      "vid_stride": 1,
      "stream_buffer": False,
      "visualize": False,
      "augment": False,
      "agnostic_nms": False,
      "classes": None,
      "show": False,
      "save": False,
      "save_frames": False,
      "save_txt": False,
      "save_conf": False,
      "save_crop": False,
      "show_labels": False,
      "show_conf": False,
      "show_boxes": False,
      "verbose": True
    }

    for k, v in kwargs.items():
      self.config[k] = v

    # Visual information
    self.annotator = None
    self.start_time = 0
    self.end_time = 0

    # Device information
    self.device = "cuda" if torch.cuda.is_available() else "cpu"

  def predict(self, frame):
    # Run prediction using a YOLO model for the input image 'frame'
    results = self.model(frame, **self.config)
    return results

  def display_fps(self, frame):
    # Display the FPS on a image 'frame' by calculating and overlaying as white text on a black rectange
    self.end_time = time.time()
    fps = 1 / round(self.end_time - self.start_time, 2)
    text = f"FPS: {int(fps)}"
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
    gap = 10
    cv2.rectangle(
      frame,
      (20 - gap, 70 - text_size[1] - gap),
      (20 + text_size[0] + gap, 70 + gap),
      (255, 255, 255),
      -1
    )
    cv2.putText(frame, text, (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

  def plot_bboxes(self, results, frame):
    # Plots bounding boxes on an image given detection resutls; returns annotated image and class IDs
    class_ids = []
    self.annotator = Annotator(frame, 3, results[0].names)
    boxes = results[0].boxes.xyxy.cpu()
    clss = results[0].boxes.cls.cpu().tolist()
    names = results[0].names
    for box, cls in zip(boxes, clss):
      class_ids.append(cls)
      self.annotator.box_label(box, label=names[int(cls)], color=colors(int(cls), True))
    return frame, class_ids

  def thread_loop(self):
    while self.run:
      ret, frame = self.capture.read()
      assert ret
      with self.lock:
        self.current_frame = frame
      time.sleep(0.01)

  def start_capture(self):
    self.run = True
    self.loop_thread = threading.Thread(target=self.thread_loop)
    self.loop_thread.start()

  def stop_capture(self):
    self.run = False
    self.loop_thread.join()

  def get_frame(self):
    with self.lock:
      return self.current_frame

  def __call__(self):
    # Run object detection on video frames from a camera stream, plotting and showing the results
    assert self.capture.isOpened()
    self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config["imgsz"])
    self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config["imgsz"])
    self.start_capture()
    frame_count = 0
    while True:
      self.start_time = time.time()
      frame = self.get_frame()
      if frame is None:
        continue

      results = self.predict(frame)
      frame, class_ids = self.plot_bboxes(results, frame)

      # if len(class_ids) > 0:
      if 1 in class_ids:
        if not self.email_send:
          send_email()
          self.email_send = True
      else:
        self.email_send = False

      self.display_fps(frame)
      cv2.imshow("PPE Detectoin", frame)
      frame_count += 1
      if cv2.waitKey(5) & 0xFF == 27:
        break
    self.stop_capture()
    self.capture.release()
    cv2.destroyAllWindows()

detector = ObjectDetection(0, "models/best.pt", imgsz=640, conf=0.8, classes=[0,1], verbose=False, iou=0.7)
detector()