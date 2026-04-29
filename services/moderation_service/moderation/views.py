from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from  .ai_moderator import AI
from PIL import Image
import io

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def moderate_product_image(request):
    image_file = request.FILES.get('image')

    if not image_file:
        return Response({
            "approved": True,
            "reason": "No image provided for moderation.",
            "detections": []
        })

    try:
        # Load directly into Pillow image without writing to disk
        image_bytes = image_file.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        result = AI.moderate_image(pil_image)
        
        return Response(result, status=200 if result["approved"] else 400)

    except Exception as e:
        return Response({
            "approved": False,
            "reason": f"Corrupted image or parse error: {str(e)}",
            "detections": []
        }, status=400)
