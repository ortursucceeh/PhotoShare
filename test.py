import pyqrcode
import io
import base64
from starlette.responses import StreamingResponse

url = "/home/vasya/Завантаження/Telegram Desktop/bilka.jpg"

url_input = "https://res.cloudinary.com/dybgf2pue/image/upload/c_thumb,g_face,h_400,w_400/r_max/4"

def gg(url_input):
    img = pyqrcode.create(url_input)
    s = io.BytesIO()
    img.png(s,scale=6)
    encoded = base64.b64encode(s.getvalue()).decode("ascii")
    return StreamingResponse(encoded, media_type="image/jpeg")
print(gg(url_input))
