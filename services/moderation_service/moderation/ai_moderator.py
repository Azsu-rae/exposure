import os
from ultralytics import YOLO

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'best.pt')

BANNED_CLASSES = {'guns', 'swords', 'bombs', 'drugs'}

class Moderator:
    def __init__(self):
        self.model = None
        self.loaded = False
        
        try:
            if os.path.exists(MODEL_PATH):
                self.model = YOLO(MODEL_PATH)
                self.loaded = True
                print(f"✅ YOLO Model loaded successfully from {MODEL_PATH}")
            else:
                print(f"⚠️ Warning: best.pt not found at {MODEL_PATH}. Moderation will approve by default until provided.")
        except Exception as e:
            print(f"❌ Critical YOLO Error during load: {e}")

    def moderate_image(self, image_source):
        """
        Accepts a PIL Image or purely in-memory buffer.
        Returns a dict indicating approval, reason, and any detections.
        """
        if not self.loaded:
            return {
                "approved": True, 
                "reason": "Model best.pt is missing - bypassing AI moderation.",
                "detections": []
            }

        try:
            results = self.model(image_source, verbose=False)
            
            detections = []
            flagged = False
            
            for result in results:
                # YOLOv8 Boxes object natively contains bounding box info
                boxes = result.boxes
                for box in boxes:
                    conf = float(box.conf[0])
                    if conf > 0.5:
                        cls_index = int(box.cls[0])
                        class_name = result.names[cls_index].lower()
                        
                        detections.append({
                            "class": class_name,
                            "confidence": round(conf, 4)
                        })
                        
                        if class_name in BANNED_CLASSES:
                            flagged = True

            if flagged:
                return {
                    "approved": False,
                    "reason": "Image contains restricted illegal items.",
                    "detections": detections
                }
            
            return {
                "approved": True,
                "reason": "Image passed moderation scan.",
                "detections": detections
            }
            
        except Exception as e:
            return {
                "approved": False,
                "reason": f"AI Engine Exception: {str(e)}",
                "detections": []
            }

# Singleton Instance
AI = Moderator()
