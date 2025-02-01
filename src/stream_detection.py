# Import libraries
import cv2
import threading
import time
import torch

from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

from config import CAM_USER, CAM_PASSWORD, CAM_IP

def test_send_email(instance):
  """Send a email notification when a some ppe is not detected"""
  if instance == 1:
    print("Helmet not found! The email was sent!")
  elif instance == 2:
    print("Harness not found! The email was sent!")
  elif instance == 3:
    print("Vest not found! The email was sent!")

class PPEMonitoring:
  """
  A class to manage the monitoring of personal protective equipment.

  This class provides functions to monitor helmet, safety vest, and
  safety harness usage in a frame, send email notifications when
  specific time thresholds are exceeded, and annotate the output frame
  for visualization.
  """
  def __init__(self, source, model, monit_instances, **kwargs):
    """Initializes an ObjectDetection instance with a given camera index."""
    # Prediction configuration
    self.source = source
    self.class_ids = []

    # Model configuration
    self.model = YOLO(model)

    # Device configuration
    self.device = "0" if torch.cuda.is_available() else "cpu"

    # General locker
    self.lock = threading.Lock()

    # Alert configuration
    self.monit_instances = monit_instances # Intances to active the alert (no_helment, no_safety_vest, no_safety_harness)
    self.monitoring_index = {
      "1": 0, # No helmet
      "2": 1, # No Harness
      "3": 2, # No Vest
    }
    self.monitoring_conf = [
      {
        "monitoring_time": 10,
        "detection_amount": 6,
        "detection_count": 0,
        "run_alert": False,
        "alert_thread": None
      },
      {
        "monitoring_time": 60,
        "detection_amount": 12,
        "detection_count": 0,
        "run_alert": False,
        "alert_thread": None
      },
      {
        "monitoring_time": 30,
        "detection_amount": 15,
        "detection_count": 0,
        "run_alert": False,
        "alert_thread": None
      }
    ]

    # Default arguments values for model
    self.config = {
        "stream": True,
        "conf": 0.8,
        "iou": 0.7,
        "imgsz": (640,640),
        "device": None,
        "vid_stride": 1,
        "stream_buffer": False,
        "visualize": False,
        "augment": False,
        "agnostic_nms": False,
        "classes": None,
        "show": False,
        "show_labels": True,
        "show_conf": True,
        "show_boxes": True,
        "verbose": True
    }
    for k, v in kwargs.items():
      self.config[k] = v
    # self.config["device"] = self.device

    # Visualization configuration
    self.annotator = None
    self.start_time = 0
    self.end_time = 0

  # Plot bboxes
  def plot_bboxes(self, result, frame):
    """Plots bounding boxes on an image given detection resutls; returns annotated image and class IDs"""
    self.annotator = Annotator(frame, 2, result.names)
    boxes = result.boxes.xyxy.cpu()
    clss = result.boxes.cls.cpu().tolist()
    names = result.names
    for box, cls in zip(boxes, clss):
      self.annotator.box_label(box, label=names[int(cls)], color=colors(int(cls), True))
    return frame

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
  def alert_monitoring_loop(self, instance, monit_index):
    """Monitors detection of non-use of PPE for 10 seconds."""
    print("No detected", instance)
    start_time = time.time()
    while (time.time() - start_time < self.monitoring_conf[monit_index]["monitoring_time"]) and self.monitoring_conf[monit_index]["run_alert"]:
      with self.lock:
        if instance in self.class_ids:
          print("count of", instance, self.monitoring_conf[monit_index]["detection_count"])
          self.monitoring_conf[monit_index]["detection_count"] += 1
      time.sleep(1)  # Monitors every second

    # Compare detections counts with threshold (detection_amount)
    if self.monitoring_conf[monit_index]["detection_count"] >= self.monitoring_conf[monit_index]["detection_amount"]:
      test_send_email(instance)
    self.monitoring_conf[monit_index]["run_alert"] = False  # realease the thread
    self.monitoring_conf[monit_index]["detection_count"] = 0

  # Start the alert monitor
  def start_alert(self, instance, monit_index):
    """Start a thread to monitor for 10 seconds."""
    self.monitoring_conf[monit_index]["run_alert"] = True
    self.monitoring_conf[monit_index]["detection_count"] = 1
    self.monitoring_conf[monit_index]["alert_thread"] = threading.Thread(target=self.alert_monitoring_loop, args=(instance, monit_index))
    self.monitoring_conf[monit_index]["alert_thread"].start()

  # Stop the alert monitor
  def stop_alert(self, index):
    self.monitoring_conf[index]["run_alert"] = False
    self.monitoring_conf[index]["alert_thread"].join()

  # Initialize the personal protective equipment
  def __call__(self):
    """Run object detection on video frames from a camera stream, plotting and showing the results"""
    # Define the model generator
    results = self.model(self.source, **self.config)
    while True:
      self.start_time = time.time()
      result = next(results)
      frame = result.orig_img
      class_ids = result.boxes.cls.cpu().tolist()
      self.update_class_ids(class_ids)

      frame = self.plot_bboxes(result, frame)

      for i in self.monit_instances:
        monit_index = self.monitoring_index[str(i)]
        if (i in class_ids) and not self.monitoring_conf[monit_index]["run_alert"]:
          self.start_alert(i, monit_index)

      # Control fps time
      # elapse_time = time.time() - self.start_time
      # if elapse_time < 0.12:
      #   time.sleep(0.12 - elapse_time)

      self.display_fps(frame)
      # print(frame.shape)
      cv2.imshow("PPE Monitoring - Streaming", frame)

      if cv2.waitKey(5) & 0xFF == 27:
        break

    for index, _ in enumerate(self.monitoring_conf):
      if self.monitoring_conf[index]["alert_thread"]:
        self.stop_alert(index)

    cv2.destroyAllWindows()

if __name__ == "__main__":
  try:
    # camera = f"rtsp://{CAM_USER}:{CAM_PASSWORD}@{CAM_IP}/Streaming/channels/101"
    camera = 0
    detector = PPEMonitoring(camera, "models/trained/best.pt", [1, 2], stream=True, device=0, imgsz=(1536, 864), conf=0.5, iou=0.7, show=False, verbose=False)
    detector()
  except:
    for index, _ in enumerate(detector.monitoring_conf):
      if detector.monitoring_conf[index]["alert_thread"]:
        detector.stop_alert(index)