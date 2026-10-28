from pico2d import load_image
from settings import RESOURCE_DIR


class Grass:
    def __init__(self):
        self.image = load_image(str(RESOURCE_DIR / 'grass.png'))

    def draw(self):
        self.image.draw(400, 30)

    def update(self):
        pass
