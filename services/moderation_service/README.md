# AI Moderation Microservice (YOLO)

This is a dedicated, lightweight Django REST Framework microservice that operates independently to perform AI-based moderation on product images using a local YOLOv8 weights file.

## 📥 Setup Instructions

**1. Install Dependencies**
```bash
cd services/moderation_service
pip install -r requirements.txt
```

**2. Place the YOLO Model**
Place your custom trained weights file **directly** into this `moderation_service/` directory and name it `best.pt`.
> Example Path: `C:\Users\raouf\PycharmProjects\microservice\exposure\services\moderation_service\best.pt`

Our custom wrapper inside `moderation/ai_moderator.py` dynamically loads this model into memory as a Singleton on startup so it only ever boots ONCE instead of re-loading per request.

**3. Run the Service (Port 8001)**
We suggest running this on port `8001` or `8005` to avoid conflicting with the main Store Service on `8000`.
```bash
python manage.py migrate
python manage.py runserver 8001
```

## 🚀 API Definition

All API requests are open internally—**No Authentication Required.**

### `POST /api/moderate/`

**Request:** `multipart/form-data`
- `image`: The binary image file to scan.

**Success Response (JSON) (200 OK or 400 Bad Request):**
```json
{
  "approved": false,
  "reason": "Image contains restricted illegal items.",
  "detections": [
    {
      "class": "guns",
      "confidence": 0.893
    }
  ]
}
```

The model automatically fails any image if it detects the standard classes `"guns", "swords", "drugs", "bombs"` with a confidence above 50% (`> 0.5`).
If the image file is purely uninterpretable or missing, it defaults to approving or bypassing.
