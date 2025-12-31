"""
Module 29: ASCII Art Engine
Conversion d'images en ASCII
"""
class ASCIIArt:
    def convert(self, image_path, width=100):
        from PIL import Image
        
        chars = "@%#*+=-:. "
        img = Image.open(image_path)
        img = img.resize((width, int(width * img.height / img.width / 2)))
        img = img.convert('L')
        
        ascii_str = ""
        for y in range(img.height):
            for x in range(img.width):
                gray = img.getpixel((x, y))
                ascii_str += chars[gray * len(chars) // 256]
            ascii_str += "\n"
        
        return ascii_str