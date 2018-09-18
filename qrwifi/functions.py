import numpy as np
import pyqrcode as pq
from solid import color, cube, scad_render, translate, union


def wifi_qr(ssid: str, security: str, password: str):
    """
    Creates the WiFi QR code object.
    """
    qr = pq.create(f"WIFI:S:{ssid};T:{security};P:{password};;")
    return qr


def qr2array(qr):
    """
    Convert a QR code object into its array representation.
    """
    arr = []
    for line in qr.text().split("\n"):
        if len(line) != 0:
            arr.append([int(bit) for bit in line])
    return np.vstack(arr)


def png_b64(qr, scale: int = 10):
    """
    Return the base64 encoded PNG of the QR code.
    """
    return qr.png_data_uri(scale=scale)


def arr2scad(arr, HEIGHT:int = 2):
    """
    Convert an array `arr` into valid OpenSCAD text.
    """

    SCALE = 2  # output defaults to 1 mm per unit; this lets us increase the size of objects proportionally.
    cubes = [translate([i*SCALE, j*SCALE, 0])(color('black')(cube(size=[SCALE, SCALE, HEIGHT])))
             for i, row in enumerate(arr)
             for j, col in enumerate(row)
             if arr[i, j] == 1]

    base_plate = color('white')(cube(size=(arr.shape[0] * SCALE, arr.shape[1] * SCALE, HEIGHT / 2)))
    qrobj = union()(*cubes, base_plate)

    return scad_render(qrobj)
