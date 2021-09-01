'''

New Card feature to return instantly manipulated image

'''


import io
from typing import Tuple
from PIL import Image, ImageDraw



class Card:

    def __init__(self, size:Tuple = None, color:hex = None, image_path:str = None):

        color = 0x000000 if color is None else color

        if size is not None and len(size) == 2 and image_path is None:
            card = Image.new("RGB", size, color=color)
            buff = io.BytesIO()
            card.save(buff, 'png')
            buff.seek(0)
            self.card = buff
            self.height = size[1]
            self.width = size[0]

        elif size is None and image_path is not None:
            local_card_image = Image.open(image_path)
            buff = io.BytesIO()
            local_card_image.save(buff, 'png')
            buff.seek(0)
            self.card = buff
            self.width, self.height = local_card_image.size

        elif size is not None and image_path is not None:
            local_card_image = Image.open(image_path).resize(size, resample=0)
            buff = io.BytesIO()
            local_card_image.save(buff,'png')
            buff.seek(0)
            self.card = buff

        else:
            self.card = None
            print('<-- incorrect image dimensions or path -->')



    def add_image_with_resize(self, image_path:str = None, resize:Tuple = None, position:Tuple = None):

        image_path = None if image_path is None else image_path

        if image_path is not None:

            if len(resize) == 2:

                if position is None:
                    offset = ((self.width - resize[0])//2, (self.height - resize[1])//2)
                else:
                    offset = (position[0],position[1])

                added_img = Image.open(image_path).resize(resize, resample=0)
                card = Image.open(self.card)
                Image.Image.paste(card, added_img, offset)

                buff = io.BytesIO()
                card.save(buff,'png')
                buff.seek(0)
                return buff

        else:
            print('<-- image source not found -->')
            return None




    def add_image_with_crop(self, image_path:str = None, crop:Tuple = None, position:Tuple = None):

        image_path = None if image_path is None else image_path

        if image_path is not None:
            added_img = Image.open(image_path)

            if len(crop) == 4:
                cropped_img = added_img.crop(crop)
                h = cropped_img.height
                w = cropped_img.width
                size = (w, h)

                if len(size) == 2:

                    if position is None:
                        offset = ((self.width - size[0])//2, (self.height - size[1])//2)
                    else:
                        offset = (position[0],position[1])

                    card = Image.open(self.card)

                    Image.Image.paste(card, cropped_img, offset)

                    buff = io.BytesIO()
                    card.save(buff,'png')
                    buff.seek(0)

                    return buff

            else:
                print('<-- crop takes positions ( LEFT, TOP, RIGHT, BOTTOM) -->')
                return None


    def add_image_with_circular_crop(self, image_path:str = None, crop:Tuple = None, position:Tuple = None):
        #coming soon
        return None
    
