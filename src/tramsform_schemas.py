from pydantic import BaseModel, Field


class TransformCircleModel(BaseModel):
    height: int = Field(ge=0, default=400)
    width: int = Field(ge=0, default=400)


class TransformEffectModel(BaseModel):
    art_audrey: bool = False
    art_zorro: bool = False
    blur: bool = False
    cartoonify: bool = False
    

class TransformResizeModel(BaseModel):
    crop: bool = False
    scale: bool = False
    fill: bool = False
    pad: bool = False
    height: int = Field(ge=0, default=400)
    width: int = Field(ge=0, default=400)


class TransformTextModel(BaseModel):
    font_size: int = Field(ge=0, default=70)
    text: str = Field(max_length=100, default="")