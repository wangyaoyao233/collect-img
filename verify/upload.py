import time
import requests
import os
from dotenv import load_dotenv
from io import BytesIO
import mimetypes

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
FOLDER_PATH = os.getenv("FOLDER_PATH")


def download_upload_img(img_objects):
    for img in img_objects:
        print(f"Downloading: {img['src']}")
        print(f"Uploading: {img['name']}")
        # download img
        response = requests.get(img["src"], stream=True)
        response.raise_for_status()
        image_data = BytesIO(response.content)

        # upload img
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        mime_type, _ = mimetypes.guess_type(img["name"])
        files = {
            "document": (
                img["name"],
                image_data,
                mime_type or "application/octet-stream",
            )
        }
        data = {"chat_id": CHANNEL_ID}
        response = requests.post(url, data=data, files=files)
        print(response.json())
        time.sleep(1)


img_objects = [
    {
        "src": "https://static.staff-start.com/img/staff/icon/177/8661c36a4128981ea82f933f3d22787e-53630/80c4ddd6e102ccf09bd4515bb09c2c06.jpg",
        "name": "icon.jpg",
    },
]
download_upload_img(img_objects)

# Output:
"""
Downloading: https://static.staff-start.com/img/staff/icon/177/8661c36a4128981ea82f933f3d22787e-53630/80c4ddd6e102ccf09bd4515bb09c2c06.jpg
Uploading: icon.jpg
{
    "ok": True,
    "result": {
        "message_id": 5484,
        "sender_chat": {
            "id": -1002288238924,
            "title": "sachiko.photo",
            "type": "channel",
        },
        "chat": {"id": -1002288238924, "title": "sachiko.photo", "type": "channel"},
        "date": 1733961526,
        "document": {
            "file_name": "icon.jpg",
            "mime_type": "image/jpeg",
            "thumbnail": {
                "file_id": "AAMCBQADIQYABIhjwUwAAhVsZ1onN2iO4-pNrOGDyKw91CHwW2kAAvEOAAIsCtlWKEs_-u_d-Y8BAAdtAAM2BA",
                "file_unique_id": "AQAD8Q4AAiwK2VZy",
                "file_size": 34438,
                "width": 320,
                "height": 320,
            },
            "thumb": {
                "file_id": "AAMCBQADIQYABIhjwUwAAhVsZ1onN2iO4-pNrOGDyKw91CHwW2kAAvEOAAIsCtlWKEs_-u_d-Y8BAAdtAAM2BA",
                "file_unique_id": "AQAD8Q4AAiwK2VZy",
                "file_size": 34438,
                "width": 320,
                "height": 320,
            },
            "file_id": "BQACAgUAAyEGAASIY8FMAAIVbGdaJzdojuPqTazhg8isPdQh8FtpAALxDgACLArZVihLP_rv3fmPNgQ",
            "file_unique_id": "AgAD8Q4AAiwK2VY",
            "file_size": 118696,
        },
    },
}
"""
