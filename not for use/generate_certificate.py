from PIL import Image, ImageDraw, ImageFont
from datetime import datetime


# Open the image file
image = Image.open("../others/certifikat.png")

# Get the width and height of the image
width, height = image.size

# Create a new ImageDraw object
draw = ImageDraw.Draw(image)

# Define the text you want to add to the image
text = "Adam Čepil"
text2 = datetime.now().strftime('X%d.X%m.%Y').replace('X0','X').replace('X','')
print(text2)
# Define the font you want to use for the text
font = ImageFont.truetype("Allison_Script.otf", 150)
font2 = ImageFont.truetype("Allison_Script.otf", 130)

# Get the size of the text
text_width, text_height = draw.textsize(text, font)
text_width2, text_height2 = draw.textsize(text2, font2)

# Calculate the x and y coordinates of the center of the image
x = (width - text_width) / 2
y = (height - text_height) / 2-30

x2 = (width - text_width2) / 4*3.7
y2 = (height - text_height2) / 4*3.6
# Draw the text in the center of the image
draw.text((x, y), text, font=font)
draw.text((x2, y2), text2, font=font2,fill=(0, 0, 0),angle=45)

# fill=(157, 139, 23)
# Save the modified image
image.save("image_with_text.png")
