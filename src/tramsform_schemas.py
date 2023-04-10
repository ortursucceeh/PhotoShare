from pydantic import BaseModel, Field


class TransformCircleModel(BaseModel):
    use_filter: bool = False
    height: int = Field(ge=0, default=400)
    width: int = Field(ge=0, default=400)


class TransformEffectModel(BaseModel):
    use_filter: bool = False
    art_audrey: bool = False
    art_zorro: bool = False
    cartoonify: bool = False
    blur: bool = False
    

class TransformResizeModel(BaseModel):
    use_filter: bool = False
    crop: bool = False
    fill: bool = False
    height: int = Field(ge=0, default=400)
    width: int = Field(ge=0, default=400)


class TransformTextModel(BaseModel):
    use_filter: bool = False
    font_size: int = Field(ge=0, default=70)
    text: str = Field(max_length=100, default="")


class TransformRotateModel(BaseModel):
    use_filter: bool = False
    width: int = Field(ge=0, default=400)
    degree: int = Field(ge=-360, le=360, default=45)


class TransformBodyModel(BaseModel):
    circle: TransformCircleModel
    effect: TransformEffectModel
    resize: TransformResizeModel
    text: TransformTextModel
    rotate: TransformRotateModel

