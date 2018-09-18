from qrwifi.functions import arr2scad, qr2array
import pyqrcode as pq

def main():
    message = """
https://my.bible.com/bible/111/NUM.6.23-26
"""
    qr = pq.create(message)
    scad = arr2scad(qr2array(qr))
    with open('example.scad', 'w+') as f:
        f.write(scad)


if __name__ == '__main__':
    main()