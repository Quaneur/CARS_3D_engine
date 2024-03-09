import pygame
import math
import Vectors as v
from Objects import *


        

pygame.init()
disp = pygame.display.Info()
#SIZE = (disp.current_w, disp.current_h)
SIZE = 1280, 720
FPS = 60
scale_coof = 0.5

cam = Cam(v.Vector3D(0, 0, -3), rot=v.Vector3D(0, 0, 0), zoom=(250/720*min(SIZE[0], SIZE[1]))*scale_coof/0.75)

points_cube = [v.Vector3D(-1, -1, -1), v.Vector3D(1, -1, -1), v.Vector3D(1, 1, -1), v.Vector3D(-1, 1, -1),
                   v.Vector3D(-1, -1, 1), v.Vector3D(1, -1, 1), v.Vector3D(1, 1, 1), v.Vector3D(-1, 1, 1)]

Cube = Model(points_cube, ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)) )
Cube1 = Model(points_cube, ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)) )
Plane = Model((v.Vector3D(-2, 1, -2), v.Vector3D(2, 1, -2), v.Vector3D(2, 1, 2), v.Vector3D(-2, 1, 2)), ((0, 1), (1, 2), (2, 3), (3, 0)))
Axis = Model((v.Vector3D(0, 0, 0), v.Vector3D(1, 0, 0), v.Vector3D(0, 1, 0), v.Vector3D(0, 0, 1)), ((0, 1), (0, 2), (0, 3) ) )
line = Model((v.Vector3D(-100, 0, 0), v.Vector3D(100, 0, 0)), ((0, 1), (1, 0)) )

Axis.lines[0].col = (235, 20, 20)
Axis.lines[1].col = (20, 235, 20)
Axis.lines[2].col = (20, 20, 235)
Axis.rendDots = False

Cube.center = v.Vector3D(0, 0, 3)

Cube1.center = v.Vector3D(0, 0, 3)
Cube1.scale = v.Vector3D(0.5, 0.5, 0.5)

line.rendDots = False


renders = [Cube, Cube1, Plane, Axis, line]

m_pos = v.Vector2D(0, 0)


scr = pygame.display.set_mode(SIZE, pygame.NOFRAME)
render_surf = pygame.Surface((SIZE[0]*scale_coof,SIZE[1]*scale_coof))
time = pygame.time
clock = time.Clock()

pygame.mouse.set_visible(False)
center = (SIZE[0]//2, SIZE[1]//2)
pygame.mouse.set_pos(center)

movex = 0
movey = 0
movez = 0

zoom_change = 0

font = pygame.font.SysFont("arial",16)

frame = 0
run = True
fps = FPS
speed = 3
zoom_coof = 0.5

last_mouse_pos = v.Vector2D(SIZE[0]//2, SIZE[1]//2)
anglex = 0
angley = 0
rotated = False



while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                movez += 1
            elif event.key == pygame.K_s:
                movez -= 1
            elif event.key == pygame.K_d:
                movex += 1
            elif event.key == pygame.K_a:
                movex -= 1
            elif event.key == pygame.K_SPACE:
                movey += 1
            elif event.key == pygame.K_LCTRL:
                movey -= 1
            elif event.key == pygame.K_ESCAPE:
                run = False
            elif event.key == pygame.K_EQUALS:
                zoom_change -= 1/10
            elif event.key == pygame.K_MINUS:
                    zoom_change += 1/10

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                movez -= 1
            elif event.key == pygame.K_s:
                movez += 1
            elif event.key == pygame.K_d:
                movex -= 1
            elif event.key == pygame.K_a:
                movex += 1
            elif event.key == pygame.K_SPACE:
                movey -= 1
            elif event.key == pygame.K_LCTRL:
                movey += 1
            elif event.key == pygame.K_EQUALS:
                zoom_change += 1/10
            elif event.key == pygame.K_MINUS:
                zoom_change -= 1/10
            
        elif event.type == pygame.MOUSEMOTION:
            m_pos = v.Vector2D(event.rel[0], event.rel[1])

    pygame.mouse.set_pos(center)
    attr = m_pos*5
    anglex -= attr.vec[0]/fps
    angley = max(-90, min(angley-attr.vec[1]/fps, 90))
        
    Cube.Rotate_points((60/fps, 12/fps, -9/fps))
    Cube1.Rotate_points((60/fps, 12/fps, -9/fps))
    zoom_coof += zoom_change/fps*zoom_coof
    cam.pos += v.Vector3D(movex, movey, movez).Normalise()*speed/fps
    cam.zoom = (250/720*min(SIZE[0], SIZE[1]))*scale_coof/zoom_coof
    cam.rot = v.Vector3D(0, anglex, angley)

    render_surf.fill((50, 50, 50))
    pos_rend = font.render(f"FPS:{fps}", True, (255, 255, 255), (20, 20, 20))

    cam.render(renders, render_surf, (SIZE[0]*scale_coof, SIZE[1]*scale_coof))
    scr.blit(pygame.transform.scale(render_surf, SIZE), (0, 0))
    scr.blit(pos_rend, (5, 5))

    pygame.display.update()
    clock.tick()
    frame += 1/fps
    if frame >10/FPS:
        fps = clock.get_fps()
