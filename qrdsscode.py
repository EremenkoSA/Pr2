import qrcode
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
value = input('Ссылка: ')
value2 = input('Название qrcode: ')
img = qrcode.make(value)
pdf.image(img.get_image(), x=50, y=50)
pdf.output(value2) 