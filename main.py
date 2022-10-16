from time import sleep
from typing import Tuple
import pygame
from pygame import gfxdraw
from fetch import fetch
import gtfs_realtime_pb2
from threading import Thread
import zlib
import xml.etree.ElementTree as ET

ff = open("features.xml.zip", "rb")
fc = ff.read()
ff.close()

fd = zlib.decompress(fc)

tree = ET.fromstring(fd.decode())
tree.findall("way")

size = (700*2.3759,700)

def visible(pos: Tuple[float, float]) -> bool:
    return not (pos[0] < 0 or pos[0] > size[0] or pos[1] < 0 or pos[1] > size[1])

def vrange(min: float, max: float, value: float) -> float:
    return (value - min) / (max - min)

# Budapest coordinates
# 18.8807, 19.3359
# 47.3384, 47.6136
def translate_pos(x:float, y:float) -> Tuple[float, float]:
    x = (vrange(18.9767, 19.1271, x)) * size[0]
    y = (1-vrange(47.4697, 47.5330, y)) * size[1]
    return (x,y)

def entity_loc(entity: gtfs_realtime_pb2.FeedEntity) -> Tuple[float, float]:
    pos = translate_pos(e.vehicle.position.longitude, e.vehicle.position.latitude)
    return pos

feed: gtfs_realtime_pb2.FeedMessage = None
running = True

def task():
    while running:
        global feed
        temp = fetch()
        if feed is not None and temp.header.timestamp <= feed.header.timestamp:
            continue
        feed = temp
        sleep(1)

t = Thread(target=task)
t.start()

# Initialization
pygame.init()

pygame.display.set_caption("ocpy2d")
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

# calculate way points
ways = []
gnodes = {}

for gnode in tree.findall('node'):
    pos = translate_pos(float(gnode.attrib['lon']), float(gnode.attrib['lat']))
    gnodes.update({gnode.attrib['id']: pos})

for gway in tree.findall('way'):
    rvis = True
    hway = False
    for wtag in gway.findall('tag'):
        if wtag.attrib['k'] == "highway":
            hway = True
            if wtag.attrib['v'] in ['primary','secondary']:
                rvis = False
                break

    if not rvis or not hway:
        continue

    wp = []
    for wnode in gway.findall('nd'):
        gnode = gnodes.get(wnode.attrib['ref'])
        wp.append(gnode)
    ways.append(wp)

del gnodes

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            raise SystemExit

    screen.fill((22,22,22))

    for nodes in ways:
        if nodes.__len__() > 2:
            gfxdraw.aapolygon(screen, nodes, (40,40,40))

    if feed is not None:
        for e in feed.entity:
            loc = entity_loc(e)
            if visible(loc):
                gfxdraw.filled_circle(screen, round(loc[0]), round(loc[1]), 2, (round(118/2),round(157/2),round(255/2)))
                gfxdraw.filled_circle(screen, round(loc[0]), round(loc[1]), 1, (118,157,255))

    pygame.display.flip()
    clock.tick(60)

t.join()
