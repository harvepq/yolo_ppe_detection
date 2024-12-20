# Import libraries
import cv2
import threading
import time
import torch

from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

from config import CAM_USER, CAM_PASSWORD, CAM_IP

def send_email():
  """Send a email notification when a some ppe is not detected"""
  print("The email was sent!")

class PPEMonitoring:
  """
  A class to manage the monitoring of personal protective equipment.

  This class provides functions to monitor helmet, safety vest, and
  safety harness usage in a frame, send email notifications when
  specific time thresholds are exceeded, and annotate the output frame
  for visualization.
  """
  def __init__(self, source, model, **kwargs):
    """Initializes an ObjectDetection instance with a given camera index."""
    # Capture configuration
    self.capture = cv2.VideoCapture(source) # video capture object
    self.current_frame = None
    self.class_ids = []

    # Model configuration
    self.model = YOLO(model)

    # General locker
    self.lock = threading.Lock()

    # Capture thread configuration
    self.run_capture = False
    self.capture_loop_thread = None

    # Alert configuration
    self.monitoring_time = 10 # time threshold
    self.detection_amount = 6 # instance threshold
    self.detections_count = 0 # detection numbers
    self.run_alert = False
    self.alert_thread = None

    # Default arguments values for model
    self.config = {
      "stream": False,
      "conf": 0.8,
      "iou": 0.7,
      "imgsz": (640, 640),
      "device": None,
      "augment": False,
      "agnostic_nms": False,
      "classes": None,
      "verbose": True
    }
    for k, v in kwargs.items():
      self.config[k] = v

    # Visualization configuration
    self.annotator = None
    self.start_time = 0
    self.end_time = 0

    # Device configuration
    self.device = "cuda" if torch.cuda.is_available() else "cpu"

  # Capture method
  def capture_loop(self):
    while self.run_capture:
      ret, frame = self.capture.read()
      if not ret:
        print("Capture frame is empty")
        continue
      # Lock until current frame will be update
      with self.lock:
        self.current_frame = frame
      time.sleep(0.05)

  # Start capture thread
  def start_capture(self):
    self.run_capture = True
    self.capture_loop_thread = threading.Thread(target=self.capture_loop)
    self.capture_loop_thread.start()

  # Stop capture thread
  def stop_capture(self):
    self.run_capture = False
    self.capture_loop_thread.join() # Wait until capture thread finishes

  # Get updated frame
  def get_frame(self):
    with self.lock: # Lock update the current frame
      return self.current_frame

  # Get predictions
  def predict(self, frame):
    """"Run detection using a YOLO model for the input image 'frame'"""
    results = self.model(frame, **self.config)
    return results

  # Plot bboxes
  def plot_bboxes(self, results, frame):
    """Plots bounding boxes on an image given detection resutls; returns annotated image and class IDs"""
    class_ids = []
    self.annotator = Annotator(frame, 2, results[0].names)
    boxes = results[0].boxes.xyxy.cpu()
    clss = results[0].boxes.cls.cpu().tolist()
    names = results[0].names
    for box, cls in zip(boxes, clss):
      class_ids.append(cls)
      self.annotator.box_label(box, label=names[int(cls)], color=colors(int(cls), True))
    return frame, class_ids

  # Plot fps
  def display_fps(self, frame):
    # Display the FPS on a image 'frame' by calculating and overlaying as white text on a black rectange
    self.end_time = time.time()
    self.fps = 1 / round(self.end_time - self.start_time, 2)
    text = f"FPS: {int(self.fps)}"
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    gap = 10
    cv2.rectangle(
      frame,
      (20 - gap, 50 - text_size[1] - gap),
      (20 + text_size[0] + gap, 50 + gap),
      (255, 255, 255),
      -1
    )
    cv2.putText(frame, text, (20,50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
  # Update id classes
  def update_class_ids(self, class_ids):
    with self.lock:
      self.class_ids = class_ids

  # Alert monitor Loop
  def alert_monitoring_loop(self):
    """Monitors detection of non-use of PPE for 10 seconds."""
    start_time = time.time()
    while (time.time() - start_time < self.monitoring_time) and self.run_alert:
      with self.lock:
        if 1 in self.class_ids:
          self.detections_count += 1
      time.sleep(1)  # Monitors every second

    # Compare detections counts with threshold (detection_amount)
    if self.detections_count >= self.detection_amount:
      send_email()
    self.run_alert = False  # realease the thread

  # Start the alert monitor
  def start_alert(self):
    """Start a thread to monitor for 10 seconds."""
    self.run_alert = True
    self.detections_count = 1
    self.alert_thread = threading.Thread(target=self.alert_monitoring_loop)
    self.alert_thread.start()

  # Stop the alert monitor
  def stop_alert(self):
    self.run_alert = False
    self.alert_thread.join()

  # Initialize the personal protective equipment
  def __call__(self):
    """Run object detection on video frames from a camera stream, plotting and showing the results"""
    assert self.capture.isOpened()
    self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config["imgsz"][0])
    self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config["imgsz"][1])
    # Start the capture
    self.start_capture()
    while True:
      self.start_time = time.time()
      frame = self.get_frame()
      if frame is None:
        continue
      results = self.predict(frame)
      frame, class_ids = self.plot_bboxes(results, frame)
      self.update_class_ids(class_ids)
      if (1 in class_ids) and not self.run_alert:
        self.start_alert()
      self.display_fps(frame)
      cv2.imshow("PPE Detectoin", frame)

      if cv2.waitKey(5) & 0xFF == 27:
        break

    if self.alert_thread:
      self.stop_alert()
    self.stop_capture()
    self.capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
  # camera = f"rtsp://{CAM_USER}:{CAM_PASSWORD}@{CAM_IP}/Streaming/channels/101"
  camera = 0
  detector = PPEMonitoring(camera, "models/best.pt", device=0, imgsz=(2048, 1152), conf=0.8, iou=0.7, verbose=False)
  detector()