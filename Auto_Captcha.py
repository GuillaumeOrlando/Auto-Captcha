from PIL import Image
from PIL import ImageFilter
import pytesseract
import requests
import cv2
import io
import base64
import time

start_time = time.time()

# Init
url = "http://challenge01.root-me.org/programmation/ch8/"
junk = '/><br><br><form action="" method="POST"><input type="text" name="cametu" /><input type="submit" value="Try" /></form></body></html>'
tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
headers = {'User-Agent': 'Mozilla/5.0'}
cookie = {'PHPSESSID': 'value', 'spip_session': '72305_3fa41a2b4e30d223a1d180f1b7c63385', 'msg_history': 'explication_site_multilingue%3B'}

# get the 'page' object
page = requests.get(url)
if page.status_code != 200:
    print("[-] Error getting the webpage")
    exit(0)
else:
    print("[+] Web page successfully request")

page_cookie = str(page.cookies).replace("=","")
page_cookie = page_cookie.split("PHPSESSID")
page_cookie = page_cookie[1][:-50]
print("[+] Got cookie")

cookie['PHPSESSID'] = page_cookie

# Parse the image link from the html page
link = str(page.content)
link = link.split('src="')
link = link[1].replace(junk,"")[:-3]
data = link.replace('data:image/png;base64,',"")
print("[+] Image link retreive")

im = Image.open(io.BytesIO(base64.b64decode(data.split(',')[0])))
im.save("img/1_original.png")
print("[+] Captcha image saved")

img = Image.open('img/1_original.png')
img = img.convert("RGBA")

pixdata = img.load()

# Clean the background noise, if color != black, then set to white.
for y in range(img.size[1]):
    for x in range(img.size[0]):
        if pixdata[x, y] == (0, 0, 0, 255):
            pixdata[x, y] = (255, 255, 255, 255)

img.save("img/2_without_dots.png", "PNG")
print("[+] Background noise removed")

# Convert in black and white
image_file = Image.open("img/2_without_dots.png")
image_file = image_file.convert('L')
image_file.save('img/3_black_and_white.png')
print("[+] Convert in black and white")

#   Make the image bigger (needed for OCR)
im_orig = Image.open('img/3_black_and_white.png')
big = im_orig.resize((1000, 200), Image.NEAREST)
big.save("img/4_big.png")
print("[+] Make the image bigger")

# Apply smooth filters
image = Image.open("img/4_big.png")
moreSmoothenedImage = image.filter(ImageFilter.SMOOTH_MORE)
moreSmoothenedImage.save("img/5_smooth.png")
print("[+] Make the image smoother")

img = cv2.imread('img/4_big.png')
result = pytesseract.image_to_string(img)
if " " in result:
    result = result.replace(" ","")
    print("[+] Result : " + result)
else:
    print("[+] Result : " + result)

payload = {'cametu':result}

# Send the result back to the root-me server

page = requests.post(url,cookies=cookie, headers=headers, data=payload)

print(page.content)

interval = time.time() - start_time
print('Total time in seconds:', interval)