__version__ = "0.0.0"
__author__ = "chomuth"

import math
import sys
from operator import itemgetter

import qi

import stk.runner
import stk.events
import stk.services
import stk.qi_logging
from PIL import Image


class SIMVision(object):
    """A SIMYAN NAOqi service providing supplemental vision services."""
    APP_ID = "org.uccs.SIMVision"

    def __init__(self, qiapp):
        # generic activity boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.qi_logging.get_logger(qiapp.session, self.APP_ID)
        # Internal variables
        self.level = 0

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        """Stop the service."""
        self.logger.info("SIMVision stopped by request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        """Cleanup (add yours if needed)"""
        self.logger.info("SIMVision finished.")

    @qi.bind(returnType=qi.List(qi.Struct), paramsType=[qi.String, qi.Struct, qi.UInt8, qi.UInt8, qi.UInt8])
    def detectPixels(self, img, pixel_color, r_range=0, g_range=0, b_range=0):
        image_path = img
        color = pixel_color
        image = Image.open(image_path, 'r')
        pixel_values = list(image.getdata())
        width, height = image.size
        pixels = [pixel_values[i * width:(i + 1) * width] for i in range(height)]
        detected_pixels = list()
        k = 0
        if r_range or g_range or b_range:
            for i in range(height):
                for j in range(width):
                    r, g, b = pixels[i][j]
                    r_expected, g_expected, b_expected = color
                    if abs(r - r_expected) <= r_range and abs(g - g_expected) <= g_range and abs(b - b_expected) <= \
                            b_range:
                        detected_pixels.append((i, j))
                        k += 1
        else:
            for i in range(height):
                for j in range(width):
                    if pixels[i][j] == color:
                        detected_pixels.append((i, j))
                        k += 1
        return detected_pixels

    @qi.bind(returnType=qi.List(qi.Struct), paramsType=[qi.List(qi.Struct)])
    def getBoundary(self, detected_pixels):
        least_x = sys.maxint
        greatest_x = 0
        least_y = sys.maxint
        greatest_y = 0
        for i, j in detected_pixels:
            if i < least_x:
                least_x = i
            if i > greatest_x:
                greatest_x = i
            if j < least_y:
                least_y = j
            if j > greatest_y:
                greatest_y = j
        # getting left boundary and right boundary
        middle_x = math.floor((greatest_x + least_x) / 2)
        interested_region = list()
        for i, j in detected_pixels:
            if abs(i - middle_x) <= 1:
                interested_region.append((i, j))
        longest_gap = 0
        left = 0, 0
        right = 0, 0
        interested_region = sorted(interested_region, key=itemgetter(1), reverse=False)
        k = 0
        for i, j in interested_region:
            if k:
                distance = j - previous[1]
                if distance > longest_gap:
                    longest_gap = distance
                    right = i, j
                    left = previous
            previous = i, j
            k += 1
        # getting top bondary and bottom boundary
        middle_y = math.floor((greatest_y + least_y) / 2)
        interested_region = list()
        for i, j in detected_pixels:
            if abs(j - middle_y) <= 1:
                interested_region.append((i, j))
        longest_gap = 0
        interested_region = sorted(interested_region, key=itemgetter(0), reverse=False)
        top = 0, 0
        bottom = 0, 0
        k = 0
        for i, j in interested_region:
            if k:
                distance = i - previous[0]
                if distance > longest_gap:
                    longest_gap = distance
                    top = i, j
                    bottom = previous
            previous = i, j
            k += 1
        return top, bottom, left, right

    @qi.bind(returnType=qi.List(qi.Struct), paramsType=[qi.List(qi.Struct), qi.List(qi.UInt8)])
    def rescale(self, edges, scale):
        rescaled_edges = list()
        for i, j, k, l in edges:
            rescaled_edges.append((i / scale[0], j / scale[1], k / scale[0], l / scale[1]))
        return rescaled_edges


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_service(SIMVision)
