import base64
import urllib.request
import urllib.parse
import json

IMGBB_API_KEY = "01d4e13ce09166077b3f74004ee91206"
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"


def upload_to_imgbb(image_file) -> str:
    """Upload a file-like object to ImgBB and return the public display URL."""
    image_data = base64.b64encode(image_file.read()).decode("utf-8")
    payload = urllib.parse.urlencode({
        "key": IMGBB_API_KEY,
        "image": image_data,
    }).encode("utf-8")
    req = urllib.request.Request(IMGBB_UPLOAD_URL, data=payload, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    if not result.get("success"):
        raise ValueError("ImgBB upload failed")
    return result["data"]["display_url"]
