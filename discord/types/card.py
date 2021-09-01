from typing import Tuple
from PIL import Image, Image, ImageDraw


class Card:

    def __init__(self, size:Tuple = None, color:hex = None, image_path:str = None):

        color = 0x000000 if color is None else color

        if len(size) == 2 and image_path is None:
            self.card = Image.new("RGB", size, color=color)
            self.height = size[1]
            self.width = size[0]

        elif 0 not in size and len(size) != 2 and image_path is not None:
            local_card_image = Image.open(image_path)
            self.card = local_card_image
            self.width, self.height = local_card_image.size

        elif len(size) == 2 and image_path is not None:
            self.card = None
            print('<-- use image path only or craete a blank image -->')

        else:
            self.card = None
            print('<-- incorrect image dimenions or path -->')
            

        
    def add_image_with_resize(self, image_path:str = None, resize:Tuple = None, position:Tuple = None):
         
        image_path = None if image_path is None else image_path

        if image_path is not None:

            if len(resize) == 2:

                if position is None:
                    offset = ((self.width - resize[0])//2, (self.height - resize[1])//2)
                else:
                    offset = (position[0],position[1])

                added_img = Image.open(image_path).resize(resize, resample=0)
                Image.Image.paste(self.card, added_img, offset)

                return self.card

        else:
            print('<-- image source not found -->')
            


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

                    Image.Image.paste(self.card, cropped_img, offset)

                    return self.card

            else:
                print('<-- crop takes positions of 4 sides -->')


    def add_image_with_circular_crop(self, image_path:str = None, crop:Tuple = None, position:Tuple = None):
        #coming soon
        return None




    def show_image(self,img:Image):

        # for checking and testing

        if self.card != None:

            img.show()

        else:
            print('<-- error happened while creating the image -->')

