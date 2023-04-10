import base64
import cloudinary
import pyqrcode
import io

from sqlalchemy.orm import Session

from src.database.models import Post, User
from src.conf.config import init_cloudinary
from src.tramsform_schemas import TransformBodyModel


async def transform_metod(post_id: int, body: TransformBodyModel, user: User, db: Session) -> Post | None:
    post= db.query(Post).filter(Post.user_id == user.id, Post.id == post_id).first()
    if post:
        transformation = []
        
        if body.circle.use_filter and body.circle. height and body.circle.width:
            trans_list = [{'gravity': "face", 'height': f"{body.circle.height}", 'width': f"{body.circle.width}", 'crop': "thumb"},
            {'radius': "max"}]
            [transformation.append(elem) for elem in trans_list]
        
        if body.effect.use_filter:
            effect = ""
            if body.effect.art_audrey:
                effect = "art:audrey"
            if body.effect.art_zorro:
                effect = "art:zorro"
            if body.effect.blur:
                effect = "blur:300"
            if body.effect.cartoonify:
                effect = "cartoonify"
            if effect:
                transformation.append({"effect": f"{effect}"})

        if body.resize.use_filter and body.resize.height and body.resize.height:
            crop = ""
            if body.resize.crop:
                crop = "crop"
            if body.resize.fill:
                crop = "fill"
            if crop:
                trans_list = [{"gravity": "auto", 'height': f"{body.resize.height}", 'width': f"{body.resize.width}", 'crop': f"{crop}"}]
                [transformation.append(elem) for elem in trans_list]

        if body.text.use_filter and body.text.font_size and body.text.text:
            trans_list = [{'color': "#FFFF00", 'overlay': {'font_family': "Times", 'font_size': f"{body.text.font_size}", 'font_weight': "bold", 'text': f"{body.text.text}"}}, {'flags': "layer_apply", 'gravity': "south", 'y': 20}]
            [transformation.append(elem) for elem in trans_list]

        if body.rotate.use_filter and body.rotate.width and body.rotate.degree:
            trans_list = [{'width': f"{body.rotate.width}", 'crop': "scale"}, {'angle': "vflip"}, {'angle': f"{body.rotate.degree}"}]
            [transformation.append(elem) for elem in trans_list]

        if transformation:
            init_cloudinary()
            url = cloudinary.CloudinaryImage(post.public_id).build_url(
                transformation=transformation
            )
            post.transform_url = url
            db.commit()

        return post


async def show_qr(post_id: int, user: User, db: Session) -> Post | None:
    post= db.query(Post).filter(Post.user_id == user.id, Post.id == post_id).first()
    if post:
        if post.transform_url:   
            img = pyqrcode.create(post.transform_url)
            buffered = io.BytesIO()
            img.png(buffered,scale=6)
            encoded_img = base64.b64encode(buffered.getvalue()).decode("ascii")
    
            return encoded_img
