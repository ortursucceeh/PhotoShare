import base64
import cloudinary
import pyqrcode
import io

from sqlalchemy.orm import Session

from src.database.models import Post, User
from src.conf.config import init_cloudinary
from src.tramsform_schemas import TransformBodyModel


async def transform_metod(post_id: int, body: TransformBodyModel, user: User, db: Session) -> Post | None:
    """
    The transform_metod function takes in a post_id, body, user and db as parameters.
    It then queries the database for the post with that id and if it exists it creates an empty list called transformation.
    If any of the filters are used in body (circle, effect, resize or text) then they are added to transformation list. 
    If there is anything in transformation list then cloudinary is initialized and url is created using build_url function from cloudinary library. 
    The url contains all transformations that were added to transofrmation list before this step was executed.
    
    :param post_id: int: Identify the post that will be transformed
    :param body: TransformBodyModel: Get the data from the request body
    :param user: User: Get the user id from the database
    :param db: Session: Access the database
    :return: A post with the applied transformations
    """
    post= db.query(Post).filter(Post.user_id == user.id, Post.id == post_id).first()
    if post:
        transformation = []
        
        if body.circle.use_filter and body.circle.height and body.circle.width:
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
    """
    The show_qr function takes in a post_id and user object, and returns the QR code for that post.
        Args:
            post_id (int): The id of the Post to be shown.
            user (User): The User who is requesting to see this Post's QR code.
    
    :param post_id: int: Specify the post id of the qr code that needs to be shown
    :param user: User: Get the user's id
    :param db: Session: Access the database
    :return: A base64 encoded image of the qr code
    """
    post= db.query(Post).filter(Post.user_id == user.id, Post.id == post_id).first()
    if post:
        if post.transform_url:   
            img = pyqrcode.create(post.transform_url)
            buffered = io.BytesIO()
            img.png(buffered,scale=6)
            encoded_img = base64.b64encode(buffered.getvalue()).decode("ascii")
    
            return encoded_img
        
