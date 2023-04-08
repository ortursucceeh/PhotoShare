body = {
  "circle": {
    "usefull": False,
    "height": 400,
    "width": 400
  },
  "effect": {
    "usefull": False,
    "art_audrey": False,
    "art_zorro": False,
    "blur": False,
    "cartoonify": False
  },
  "resize": {
    "usefull": False,
    "crop": False,
    "fill": False,
    "height": 400,
    "width": 400
  },
  "text": {
    "usefull": False,
    "font_size": 70,
    "text": ""
  }
}


a = body["text"]["text"]
print(a)

# import cloudinary
# from src.conf.config import init_cloudinary
# from cloudinary.uploader import destroy
# import cloudinary.uploader


# def dell():
#   init_cloudinary()
#   cloudinary.uploader.destroy("Vasya")
# dell()

# init_cloudinary()
# transformation = [{'gravity': "face", 'height': 400, 'width': 400, 'crop': "thumb"}, {'radius': "max"}, {"effect": "art:audrey"}, {'color': "#FFFF00", 'overlay': {'font_family': "Times", 'font_size': 70, 'font_weight': "bold", 'text': "Cooooool"}}, {'flags': "layer_apply", 'gravity': "south", 'y': 20}]
# url = cloudinary.CloudinaryImage("Amber").build_url(
#                 transformation=transformation
#             )
# print(url)