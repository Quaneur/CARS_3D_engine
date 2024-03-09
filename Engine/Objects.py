import Vectors as v
import pygame
import random

class Object:
    pass


class Dot:
    def __init__(self, pos = v.Vector3D(0, 0, 0), scale: float|int = 0.25, color: tuple|list = (255, 255, 255)):
        self.pos = pos
        self.scale = scale
        self.col = color
    
    def render(self, color = None):
        if color != None:
            return ["p", self.pos.Clone(), color, self.scale]
        return ["p", self.pos.Clone(),self.col, self.scale]

class Line:
    def __init__(self, dot1, dot2, color = (255, 255, 255), width = 0.1):
        self.p1 = dot1
        self.p2 = dot2
        self.col = color
        self.width = width

    def render(self, color = None):
        if color != None:
            return ["l", self.p1.pos.Clone(), self.p2.pos.Clone(), color, self.width]
        return ["l", self.p1.pos.Clone(), self.p2.pos.Clone(), self.col, self.width]




class Model:

    def __init__(self, points, lines):
        '''Create a only-vertex-line model with base params
        '''
        if type(points[0]) == v.Vector3D:
            self.points = []
            for pos in points:
                self.points.append(Dot(pos, 0.25, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))))
        else:
            self.points = points
        self.lines = []
        for line in lines:
            self.lines.append(Line(self.points[line[0]], self.points[line[1]], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))))
        self.planes = []
        center = v.Vector3D(0, 0, 0)
        for point in self.points:
            center += point.pos
        self.center = center / len(points)
        for point in self.points:
            point.pos -= center
        self.rot = (0, 0, 0)
        self.scale = v.Vector3D(1, 1, 1)
        self.rendDots = True
        self.rendLines = True

    def Rotate_points(self, angles):
        for p in self.points:
            p.pos.Rotate_Euler(angles)

    def render_dat(self):
        '''Get the render data.
Structure:
    data[n][0]: type.
    data[n][j-1]: Base size. -> Float
    data[n][j-2]: color. -> Tuple: len = 3
    data[n][1..j-3] - points for render in 3D. -> Vector3D

Type codes:
    p - point
    l - line
    pl - plane

If data[n][0]=="pl": data[n][1..j-3] - points. -> Vector3D
                     data[n][j-2] - normal vector. -> Vector3D
                     data[n][j-1] - color. -> Tuple: len = 3
'''
        predat = []
        if self.rendDots:
            for p in self.points:
                p.pos.Rotate_Euler(self.rot)
                p.pos = p.pos*self.scale+self.center
                predat.append(p)

        if self.rendLines:
            for l in self.lines:
                predat.append(l)
        for pl in self.planes:
            predat.append(pl)

        dat = []
        for d in predat:
            dat.append(d.render())
        
        if self.rendDots:
            for p in self.points:
                p.pos.Rotate_Euler((-self.rot[0], -self.rot[1], -self.rot[2]))
                p.pos = (p.pos-self.center)/v.Vector3D(self.scale[0], self.scale[1], self.scale[2])

        return dat


class Cam:
    def __init__(self, pos, zoom, pivot_targ: Dot|None = None, rot: v.Vector3D = v.Vector3D(0, 0, 0), angle: v.Vector3D = v.Vector3D(0,0,0)):
        if pivot_targ != None:
            self.targ = pivot_targ
        self.pos = pos
        self.zoom = zoom
        self.rot = rot

    def _cam_rot_new(self, vec):
        res = vec.Rotate_Euler_new((0, 0, self.rot[1]))
        res.Rotate_Euler((0, self.rot[2], 0))
        res.Rotate_Euler((self.rot[0], 0, 0))
        return res

    def _cam_rot(self, vec):
        vec.Rotate_Euler((0, 0, self.rot[0]))
        vec.Rotate_Euler((0, self.rot[1], 0))
        vec.Rotate_Euler((self.rot[2], 0, 0))

    def render(self, objects, scr, screen_size = (480, 480)):
        render_dat = []
        for obj in objects:
            for dat in obj.render_dat():
                render_dat.append(dat)

        for rd in render_dat:
            if rd[0] == "p":
                rd[1] -= self.pos
                self._cam_rot(rd[1])
                rd.append(rd[1])
            elif rd[0] == "l":
                rd[1] -= self.pos
                rd[2] -= self.pos
                self._cam_rot(rd[1])
                self._cam_rot(rd[2])
                center = (rd[1]+rd[2])/2
                rd.append(center)

        render_dat.sort(key=lambda x: -x[len(x)-1].vec[2])

        for data in render_dat:
            if data[len(data)-1].vec[2] <= 0:
                continue
            if data[0] == "p":
                scr_pos = v.Vector2D(data[1].vec[0]/data[1].vec[2], -data[1].vec[1]/data[1].vec[2])
                
                size = data[3]/data[1].vec[2]*self.zoom
                scr_pos *= self.zoom
                scr_pos += v.Vector2D(screen_size[0], screen_size[1])/2
                if -size <= scr_pos.vec[0] <= screen_size[0]+size and -size <= scr_pos.vec[1] <= screen_size[1]+size:
                    pygame.draw.circle(scr, data[len(data)-3], (round(scr_pos.vec[0]), round(scr_pos.vec[1])), round(size))
            elif data[0] == "l":

                if data[1].vec[2] <= 0:
                    p1 = data[1]
                    p2 = data[2]

                    z_coof = 1-p1.vec[2]

                    p2_scr_norm = (v.Vector2D(p1.vec[0]/(p1.vec[2]+z_coof), -p1.vec[1]/(p1.vec[2]+z_coof))-v.Vector2D(p2.vec[0]/(p2.vec[2]+z_coof), -p2.vec[1]/(p2.vec[2]+z_coof))).Normalise()
                    p2_scr = v.Vector2D(p2.vec[0]/p2.vec[2], -p2.vec[1]/p2.vec[2])
                    p2_scr = p2_scr*self.zoom + v.Vector2D(screen_size[0], screen_size[1])/2
                    if p2_scr_norm.dot(v.Vector2D(1, 0)) > 0:
                        hor_len = abs(abs(screen_size[0]-p2_scr.vec[0])/p2_scr_norm.vec[0])
                    else:
                        hor_len = abs(p2_scr.vec[0]/p2_scr_norm.vec[0])

                    if p2_scr_norm.dot(v.Vector2D(0, 1)) > 0:
                        ver_len = abs(abs(screen_size[1]-p2_scr.vec[1])/p2_scr_norm.vec[1])
                    else:
                        ver_len = abs(p2_scr.vec[1]/p2_scr_norm.vec[1])

                    length = min(hor_len, ver_len)
                    p1_scr = p2_scr+p2_scr_norm*length

                elif data[2].vec[2] <= 0:
                    p1 = data[1]
                    p2 = data[2]

                    z_coof = 1-p2.vec[2]

                    p1_scr_norm = (v.Vector2D(p2.vec[0]/(p2.vec[2]+z_coof), -p2.vec[1]/(p2.vec[2]+z_coof))-v.Vector2D(p1.vec[0]/(p1.vec[2]+z_coof), -p1.vec[1]/(p1.vec[2]+z_coof))).Normalise()
                    p1_scr = v.Vector2D(p1.vec[0]/p1.vec[2], -p1.vec[1]/p1.vec[2])
                    p1_scr = p1_scr*self.zoom + v.Vector2D(screen_size[0], screen_size[1])/2
                    if p1_scr_norm.dot(v.Vector2D(1, 0)) > 0:
                        hor_len = abs(abs(screen_size[0]-p1_scr.vec[0])/p1_scr_norm.vec[0])
                    else:
                        hor_len = abs(p1_scr.vec[0]/p1_scr_norm.vec[0])

                    if p1_scr_norm.dot(v.Vector2D(0, 1)) > 0:
                        ver_len = abs(abs(screen_size[1]-p1_scr.vec[1])/p1_scr_norm.vec[1])
                    else:
                        ver_len = abs(p1_scr.vec[1]/p1_scr_norm.vec[1])

                    length = min(hor_len, ver_len)
                    p2_scr = p1_scr+p1_scr_norm*length
                else:

                    p1_scr = v.Vector2D(data[1].vec[0]/data[1].vec[2], -data[1].vec[1]/data[1].vec[2])
                    p2_scr = v.Vector2D(data[2].vec[0]/data[2].vec[2], -data[2].vec[1]/data[2].vec[2])
                
                    p1_scr = p1_scr*self.zoom + v.Vector2D(screen_size[0], screen_size[1])/2
                    p2_scr = p2_scr*self.zoom + v.Vector2D(screen_size[0], screen_size[1])/2

                width = data[4]/data[len(data)-1].vec[2]*self.zoom

                clip_p = pygame.Rect((0, 0), screen_size).clipline(p1_scr.vec, p2_scr.vec)
                if clip_p != ():
                    pygame.draw.line(scr, data[3], (round(clip_p[0][0]),round(clip_p[0][1])), (round(clip_p[1][0]),round(clip_p[1][1])), round(width))



if __name__ == "__main__":
    obj = Model((Dot(v.Vector3D(-1, -1, -1)), Dot(v.Vector3D(1, -1, -1)),
                 Dot(v.Vector3D(1, 1, -1)), Dot(v.Vector3D(-1, 1, -1)),
                 Dot(v.Vector3D(-1, -1, 1)), Dot(v.Vector3D(1, -1, 1)),
                 Dot(v.Vector3D(1, 1, 1)), Dot(v.Vector3D(-1, 1, 1))), ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)))
    obj.center += v.Vector3D(0, 0, 0)
    for i in obj.render_dat():
        print(i)

    Model()