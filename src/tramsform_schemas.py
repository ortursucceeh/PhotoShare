from pydantic import BaseModel, Field


class TransformCircleModel(BaseModel):
    usefull: bool = False
    height: int = Field(ge=0, default=400)
    width: int = Field(ge=0, default=400)


class TransformEffectModel(BaseModel):
    usefull: bool = False
    art_audrey: bool = False
    art_zorro: bool = False
    blur: bool = False
    cartoonify: bool = False
    

class TransformResizeModel(BaseModel):
    usefull: bool = False

    crop: bool = False
    fill: bool = False
    height: int = Field(ge=0, default=400)
    width: int = Field(ge=0, default=400)


class TransformTextModel(BaseModel):
    usefull: bool = False
    font_size: int = Field(ge=0, default=70)
    text: str = Field(max_length=100, default="")


class TransformBodyModel(BaseModel):
    circle: TransformCircleModel
    effect: TransformEffectModel
    resize: TransformResizeModel
    text: TransformTextModel

