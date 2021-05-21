import json
import uuid

from app import db


class Video(db.Model):
    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(8), nullable=False, default='')
    user_id = db.Column(db.Integer, nullable=False)
    id_preset = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(1024), nullable=False)

    result_url = db.Column(db.String(1024), nullable=False, default='')
    result_srt = db.Column(db.String(1024), nullable=False, default='')
    image = db.Column(db.String(1024), nullable=False, default='')
    gif = db.Column(db.String(1024), nullable=True, default='')
    ready = db.Column(db.String(100), nullable=False, default='Edit')
    status = db.Column(db.String(100), nullable=False, default='Extract')
    description = db.Column(db.String(1024), nullable=False, default='')
    language_code = db.Column(db.String(10), nullable=False, default='en_EN')

    duration = db.Column(db.String(100), nullable=False, default='')
    resolution = db.Column(db.String(100), nullable=False, default='')
    captions = db.Column(db.Text, nullable=False, default='')

    def __init__(self, user_id, url, language_code):
        self.user_id = user_id
        self.url = url
        self.language_code = language_code
        self.uuid = str(uuid.uuid4().hex[:8]).upper()

    def __repr__(self):
        return '{}:{}'.format(self.user_id, self.url)


class Preset(db.Model):
    __tablename__ = 'preset'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(1024), nullable=False, default='Default')

    fontColor = db.Column(db.String(50), nullable=False, default='#ffffff')
    backgroundColor = db.Column(db.String(10), nullable=False, default='#000000')
    fontOpacity = db.Column(db.Float, nullable=False, default=1.0)
    backgroundOpacity = db.Column(db.Float, nullable=False, default=0.5)
    font = db.Column(db.String(150), nullable=False, default='Arial')
    textSize = db.Column(db.Integer, nullable=False, default=24)
    realTextSize = db.Column(db.Integer, nullable=False, default=24)
    bold = db.Column(db.Boolean, nullable=False, default=False)
    italic = db.Column(db.Boolean, nullable=False, default=False)
    fullLengthBackground = db.Column(db.Boolean, nullable=False, default=False)
    backgroundShapeSquare = db.Column(db.Boolean, nullable=False, default=True)
    verticalAlign = db.Column(db.Integer, nullable=False, default=0)
    horizontalAlign = db.Column(db.String(50), nullable=False, default='center')
    aspectRatio = db.Column(db.String(50), nullable=False, default='0')
    progressBar = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        body = {
            'fontColor': self.fontColor,
            'backgroundColor': self.backgroundColor,
            'fontOpacity': self.fontOpacity,
            'backgroundOpacity': self.backgroundOpacity,
            'font': self.font,
            'textSize': self.textSize,
            'bold': self.bold,
            'italic': self.italic,
            'fullLengthBackground': self.fullLengthBackground,
            'backgroundShapeSquare': self.backgroundShapeSquare,
            'verticalAlign': self.verticalAlign,
            'horizontalAlign': self.horizontalAlign,
            'aspectRatio': self.aspectRatio,
            'progressBar': self.progressBar,
        }
        return json.dumps(body)

class Collection(db.Model):
    __tablename__ = 'collection'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    preset_id = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, preset_id):
        self.user_id = user_id
        self.preset_id = preset_id
