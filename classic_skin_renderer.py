import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

# =============================
# Texture Loader
# =============================
def load_texture(path):
    img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
    img_data = img.convert("RGBA").tobytes()
    width, height = img.size

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    return tex_id

# =============================
# UV Helper
# =============================
def uv(x, y):
    return x / 64, 1 - y / 64  # flip V to match Minecraft skin origin

# =============================
# Generic Box Drawer
# =============================
def draw_box(w, h, d, front, back, left, right, top, bottom):
    w /= 2
    h /= 2
    d /= 2

    def face(coords, verts):
        u1, v1 = uv(coords[0], coords[1])
        u2, v2 = uv(coords[2], coords[3])
        for (u, v), (x, y, z) in zip(
            [(u1,v1),(u2,v1),(u2,v2),(u1,v2)],
            verts
        ):
            glTexCoord2f(u, v)
            glVertex3f(x, y, z)

    glBegin(GL_QUADS)
    # Front
    face(front, [(-w,-h,d),(w,-h,d),(w,h,d),(-w,h,d)])
    # Back
    face(back, [(w,-h,-d),(-w,-h,-d),(-w,h,-d),(w,h,-d)])
    # Left
    face(left, [(-w,-h,-d),(-w,-h,d),(-w,h,d),(-w,h,-d)])
    # Right
    face(right, [(w,-h,d),(w,-h,-d),(w,h,-d),(w,h,d)])
    # Top
    face(top, [(-w,h,d),(w,h,d),(w,h,-d),(-w,h,-d)])
    # Bottom
    face(bottom, [(-w,-h,-d),(w,-h,-d),(w,-h,d),(-w,-h,d)])
    glEnd()

# =============================
# Body Parts
# =============================
def draw_head():
    # --- local UV flip for head only ---
    def uv_head(x, y):
        return x / 64, 1 - (y / 64)  # flip Y

    # --- local box drawer using uv_head ---
    def draw_box_head(w, h, d, front, back, left, right, top, bottom):
        w /= 2
        h /= 2
        d /= 2

        def face(coords, verts):
            u1, v1 = uv_head(*coords[:2])
            u2, v2 = uv_head(*coords[2:])
            for (u, v), (x, y, z) in zip(
                [(u1, v1), (u2, v1), (u2, v2), (u1, v2)],
                verts
            ):
                glTexCoord2f(u, v)
                glVertex3f(x, y, z)

        glBegin(GL_QUADS)
        y_shift = 10
        # Front
        face(front, [(-w, -h+y_shift, d), (w, -h+y_shift, d), (w, h+y_shift, d), (-w, h+y_shift, d)])
        # Back
        face(back, [(w, -h+y_shift, -d), (-w, -h+y_shift, -d), (-w, h+y_shift, -d), (w, h+y_shift, -d)])
        # Left
        face(left, [(-w, -h+y_shift, -d), (-w, -h+y_shift, d), (-w, h+y_shift, d), (-w, h+y_shift, -d)])
        # Right
        face(right, [(w, -h+y_shift, d), (w, -h+y_shift, -d), (w, h+y_shift, -d), (w, h+y_shift, d)])
        # Top
        face(top, [(-w,-h+y_shift,d),(w,-h+y_shift,d),(w,-h+y_shift,-d),(-w,-h+y_shift,-d)])
        # Bottom
        face(bottom, [(-w,h+y_shift,-d),(w,h+y_shift,-d),(w,h+y_shift,d),(-w,h+y_shift,d)])
        glEnd()

    # --- Draw the head flipped vertically ---
    glPushMatrix()
    glTranslatef(0, 4, 0)      # pivot at bottom center of head
    glScalef(1, -1, 1)         # flip head vertically
    draw_box_head(
        8, 8, 8,
        front=(8, 8, 16, 16),
        back=(24, 8, 32, 16),
        left=(0, 8, 8, 16),
        right=(16, 8, 24, 16),
        top=(8, 0, 16, 8),
        bottom=(16, 0, 24, 8)
    )
    glPopMatrix()

def draw_head_layer():
    def uv_head(x, y):
        return x / 64, 1 - (y / 64)

    def draw_box_head(w, h, d, front, back, left, right, top, bottom):
        w /= 2; h /= 2; d /= 2
        def face(coords, verts):
            u1, v1 = uv_head(*coords[:2])
            u2, v2 = uv_head(*coords[2:])
            for (u, v), (x, y, z) in zip([(u1,v1),(u2,v1),(u2,v2),(u1,v2)], verts):
                glTexCoord2f(u, v)
                glVertex3f(x, y, z)

        glBegin(GL_QUADS)
        y_shift = 30  # same as base head
        face(front, [(-w,-h+y_shift,d),(w,-h+y_shift,d),(w,h+y_shift,d),(-w,h+y_shift,d)])
        face(back, [(w,-h+y_shift,-d),(-w,-h+y_shift,-d),(-w,h+y_shift,-d),(w,h+y_shift,-d)])
        # Swap top/bottom and rotate 180 to match base
        face(bottom, [(-w,h+y_shift,d),(w,h+y_shift,d),(w,h+y_shift,-d),(-w,h+y_shift,-d)])
        face(top,    [(-w,-h+y_shift,-d),(w,-h+y_shift,-d),(w,-h+y_shift,d),(-w,-h+y_shift,d)])
        face(left, [(-w,-h+y_shift,-d),(-w,-h+y_shift,d),(-w,h+y_shift,d),(-w,h+y_shift,-d)])
        face(right, [(w,-h+y_shift,d),(w,-h+y_shift,-d),(w,h+y_shift,-d),(w,h+y_shift,d)])
        glEnd()

    glPushMatrix()
    glTranslatef(0, 22+4, 0)  # player origin + head pivot
    glScalef(1.0625, -1.0625, 1.0625)
    draw_box_head(
        8, 8, 8,
        front=(40,8,48,16),
        back=(56,8,64,16),
        left=(32,8,40,16),
        right=(48,8,56,16),
        top=(40,0,48,8),
        bottom=(48,0,56,8)
    )
    glPopMatrix()

def draw_body():
    def uv_body(x, y):
        return x / 64, 1 - (y / 64)

    def draw_box_body(w, h, d, front, back, left, right, top, bottom):
        w /= 2; h /= 2; d /= 2
        def face(coords, verts):
            u1, v1 = uv_body(*coords[:2])
            u2, v2 = uv_body(*coords[2:])
            for (u, v), (x, y, z) in zip(
                [(u1,v1),(u2,v1),(u2,v2),(u1,v2)], verts
            ):
                glTexCoord2f(u,v)
                glVertex3f(x,y,z)
        glBegin(GL_QUADS)
        y_shift = -6
        face(front, [(-w,-h+y_shift,d),(w,-h+y_shift,d),(w,h+y_shift,d),(-w,h+y_shift,d)])
        face(back, [(w,-h+y_shift,-d),(-w,-h+y_shift,-d),(-w,h+y_shift,-d),(w,h+y_shift,-d)])
        face(left, [(-w,-h+y_shift,-d),(-w,-h+y_shift,d),(-w,h+y_shift,d),(-w,h+y_shift,-d)])
        face(right, [(w,-h+y_shift,d),(w,-h+y_shift,-d),(w,h+y_shift,-d),(w,h+y_shift,d)])
        face(top, [(-w,h+y_shift,d),(w,h+y_shift,d),(w,h+y_shift,-d),(-w,h+y_shift,-d)])
        face(bottom, [(-w,-h+y_shift,-d),(w,-h+y_shift,-d),(w,-h+y_shift,d),(-w,-h+y_shift,d)])
        glEnd()

    glPushMatrix()
    glScalef(1, -1, 1)
    draw_box_body(
        8, 12, 4,
        front=(20, 20, 28, 32),
        back=(32, 20, 40, 32),
        left=(16, 20, 20, 32),
        right=(28, 20, 32, 32),
        top=(20, 16, 28, 20),
        bottom=(28, 16, 36, 20)
    )
    glPopMatrix()

def draw_body_layer():
    def uv_body(x, y):
        return x / 64, 1 - (y / 64)

    def draw_box_body(w, h, d, front, back, left, right, top, bottom):
        w /= 2; h /= 2; d /= 2
        def face(coords, verts):
            u1, v1 = uv_body(*coords[:2])
            u2, v2 = uv_body(*coords[2:])
            for (u, v), (x, y, z) in zip([(u1,v1),(u2,v1),(u2,v2),(u1,v2)], verts):
                glTexCoord2f(u,v)
                glVertex3f(x, y, z)
        glBegin(GL_QUADS)
        y_shift = -6
        face(front, [(-w,-h+y_shift,d),(w,-h+y_shift,d),(w,h+y_shift,d),(-w,h+y_shift,d)])
        face(back, [(w,-h+y_shift,-d),(-w,-h+y_shift,-d),(-w,h+y_shift,-d),(w,h+y_shift,-d)])
        face(left, [(-w,-h+y_shift,-d),(-w,-h+y_shift,d),(-w,h+y_shift,d),(-w,h+y_shift,-d)])
        face(right, [(w,-h+y_shift,d),(w,-h+y_shift,-d),(w,h+y_shift,-d),(w,h+y_shift,d)])
        face(top, [(-w,h+y_shift,d),(w,h+y_shift,d),(w,h+y_shift,-d),(-w,h+y_shift,-d)])
        face(bottom, [(-w,-h+y_shift,-d),(w,-h+y_shift,-d),(w,-h+y_shift,d),(-w,-h+y_shift,d)])
        glEnd()

    glPushMatrix()
    glScalef(1.0625, -1.0625, 1.0625)
    draw_box_body(
        8, 12, 4,
        front=(20,36,28,48),
        back=(32,36,40,48),
        left=(16,36,20,48),
        right=(28,36,32,48),
        top=(20,32,28,36),
        bottom=(28,32,36,36)
    )
    glPopMatrix()

def draw_arm(offset_x):
    mirror = offset_x > 0

    def uv_arm(x, y):
        return x / 64, 1 - (y / 64)

    def draw_box_arm(w, h, d, front, back, left, right, top, bottom):
        w /= 2; h /= 2; d /= 2

        def face(coords, verts):
            u1, v1 = uv_arm(*coords[:2])
            u2, v2 = uv_arm(*coords[2:])
            if mirror:
                u1, u2 = u2, u1  # mirror UV horizontally
            for (u, v), (x, y, z) in zip(
                [(u1,v1),(u2,v1),(u2,v2),(u1,v2)],
                verts
            ):
                glTexCoord2f(u, v)
                glVertex3f(x, y, z)

        glBegin(GL_QUADS)
        # front/back/left/right unchanged
        face(front, [(-w,-h,d),(w,-h,d),(w,h,d),(-w,h,d)])
        face(back, [(w,-h,-d),(-w,-h,-d),(-w,h,-d),(w,h,-d)])
        face(left, [(-w,-h,-d),(-w,-h,d),(-w,h,d),(-w,h,-d)])
        face(right, [(w,-h,d),(w,-h,-d),(w,h,-d),(w,h,d)])
        # swap top/bottom vertices to match glScalef(1,-1,1)
        face(top, [(-w,-h,-d),(w,-h,-d),(w,-h,d),(-w,-h,d)])
        face(bottom, [(-w,h,d),(w,h,d),(w,h,-d),(-w,h,-d)])
        glEnd()

    glPushMatrix()
    glTranslatef(offset_x, 6, 0)
    glScalef(1, -1, 1)
    draw_box_arm(
        4, 12, 4,
        front=(44, 20, 48, 32),
        back=(52, 20, 56, 32),
        left=(40, 20, 44, 32),
        right=(48, 20, 52, 32),
        top=(44, 16, 48, 20),
        bottom=(48, 16, 52, 20)
    )
    glPopMatrix()

def draw_arm_layer(offset_x):
    mirror = offset_x > 0

    def uv_arm(x, y):
        return x / 64, 1 - (y / 64)

    def draw_box_arm(w, h, d, front, back, left, right, top, bottom):
        w /= 2; h /= 2; d /= 2

        def face(coords, verts):
            u1, v1 = uv_arm(*coords[:2])
            u2, v2 = uv_arm(*coords[2:])
            if mirror:
                u1, u2 = u2, u1  # mirror horizontally
            for (u, v), (x, y, z) in zip([(u1,v1),(u2,v1),(u2,v2),(u1,v2)], verts):
                glTexCoord2f(u, v)
                glVertex3f(x, y, z)

        glBegin(GL_QUADS)
        y_shift = 0
        # front/back unchanged
        face(front, [(-w,-h+y_shift,d),(w,-h+y_shift,d),(w,h+y_shift,d),(-w,h+y_shift,d)])
        face(back, [(w,-h+y_shift,-d),(-w,-h+y_shift,-d),(-w,h+y_shift,-d),(w,h+y_shift,-d)])
        # left/right
        if mirror:
            face(right, [(-w,-h+y_shift,-d),(-w,-h+y_shift,d),(-w,h+y_shift,d),(-w,h+y_shift,-d)])
            face(left, [(w,-h+y_shift,d),(w,-h+y_shift,-d),(w,h+y_shift,-d),(w,h+y_shift,d)])
        else:
            face(left, [(-w,-h+y_shift,-d),(-w,-h+y_shift,d),(-w,h+y_shift,d),(-w,h+y_shift,-d)])
            face(right, [(w,-h+y_shift,d),(w,-h+y_shift,-d),(w,h+y_shift,-d),(w,h+y_shift,d)])
        # swap top/bottom vertices to match flipped Y
        face(top, [(-w,-h,-d),(w,-h,-d),(w,-h,d),(-w,-h,d)])
        face(bottom, [(-w,h,d),(w,h,d),(w,h,-d),(-w,h,-d)])
        glEnd()

    glPushMatrix()
    glTranslatef(offset_x, 6, 0)
    glScalef(1.0625, -1.0625, 1.0625)  # layer scale + Y-flip
    draw_box_arm(
        4, 12, 4,
        front=(44,36,48,48),
        back=(52,36,56,48),
        left=(40,36,44,48),
        right=(48,36,52,48),
        top=(44,32,48,36),
        bottom=(48,32,52,36)
    )
    glPopMatrix()
def draw_leg(offset_x):
    mirror = offset_x > 0

    def uv_leg(x, y):
        return x / 64, 1 - (y / 64)

    def draw_box_leg(w, h, d, front, back, left, right, top, bottom):
        w /= 2; h /= 2; d /= 2

        def face(coords, verts):
            u1, v1 = uv_leg(*coords[:2])
            u2, v2 = uv_leg(*coords[2:])
            if mirror:
                u1, u2 = u2, u1  # mirror horizontally
            for (u,v),(x,y,z) in zip([(u1,v1),(u2,v1),(u2,v2),(u1,v2)], verts):
                glTexCoord2f(u,v)
                glVertex3f(x,y,z)

        glBegin(GL_QUADS)
        y_shift = 0
        if mirror:
            face(right,[(-w,-h+y_shift,-d),(-w,-h+y_shift,d),(-w,h+y_shift,d),(-w,h+y_shift,-d)])
            face(left, [(w,-h+y_shift,d),(w,-h+y_shift,-d),(w,h+y_shift,-d),(w,h+y_shift,d)])
        else:
            face(left, [(-w,-h+y_shift,-d),(-w,-h+y_shift,d),(-w,h+y_shift,d),(-w,h+y_shift,-d)])
            face(right, [(w,-h+y_shift,d),(w,-h+y_shift,-d),(w,h+y_shift,-d),(w,h+y_shift,d)])
        face(front, [(-w,-h+y_shift,d),(w,-h+y_shift,d),(w,h+y_shift,d),(-w,h+y_shift,d)])
        face(back, [(w,-h+y_shift,-d),(-w,-h+y_shift,-d),(-w,h+y_shift,-d),(w,h+y_shift,-d)])
        face(top, [(-w,h+y_shift,d),(w,h+y_shift,d),(w,h+y_shift,-d),(-w,h+y_shift,-d)])
        face(bottom, [(-w,-h+y_shift,-d),(w,-h+y_shift,-d),(w,-h+y_shift,d),(-w,-h+y_shift,d)])
        glEnd()

    glPushMatrix()
    glTranslatef(offset_x, -6, 0)
    glScalef(1, -1, 1)
    draw_box_leg(
        4, 12, 4,
        front=(4, 20, 8, 32),
        back=(12, 20, 16, 32),
        left=(0, 20, 4, 32),
        right=(8, 20, 12, 32),
        top=(4, 16, 8, 20),
        bottom=(8, 16, 12, 20)
    )
    glPopMatrix()

def draw_leg_layer(offset_x):
    mirror = offset_x > 0

    def uv_leg(x, y):
        return x / 64, 1 - (y / 64)

    def draw_box_leg(w, h, d, front, back, left, right, top, bottom):
        w /= 2; h /= 2; d /= 2
        def face(coords, verts):
            u1, v1 = uv_leg(*coords[:2])
            u2, v2 = uv_leg(*coords[2:])
            if mirror:
                u1, u2 = u2, u1
            for (u,v),(x,y,z) in zip([(u1,v1),(u2,v1),(u2,v2),(u1,v2)], verts):
                glTexCoord2f(u,v)
                glVertex3f(x,y,z)
        glBegin(GL_QUADS)
        y_shift = 6
        if mirror:
            face(right,[(-w,-h+y_shift,-d),(-w,-h+y_shift,d),(-w,h+y_shift,d),(-w,h+y_shift,-d)])
            face(left, [(w,-h+y_shift,d),(w,-h+y_shift,-d),(w,h+y_shift,-d),(w,h+y_shift,d)])
        else:
            face(left, [(-w,-h+y_shift,-d),(-w,-h+y_shift,d),(-w,h+y_shift,d),(-w,h+y_shift,-d)])
            face(right, [(w,-h+y_shift,d),(w,-h+y_shift,-d),(w,h+y_shift,-d),(w,h+y_shift,d)])
        face(front, [(-w,-h+y_shift,d),(w,-h+y_shift,d),(w,h+y_shift,d),(-w,h+y_shift,d)])
        face(back, [(w,-h+y_shift,-d),(-w,-h+y_shift,-d),(-w,h+y_shift,-d),(w,h+y_shift,-d)])
        face(top, [(-w,h+y_shift,d),(w,h+y_shift,d),(w,h+y_shift,-d),(-w,h+y_shift,-d)])
        face(bottom, [(-w,-h+y_shift,-d),(w,-h+y_shift,-d),(w,-h+y_shift,d),(-w,-h+y_shift,d)])
        glEnd()

    glPushMatrix()
    glTranslatef(offset_x, 0, 0)
    glScalef(1.0625, -1.0625, 1.0625)
    draw_box_leg(
        4, 12, 4,
        front=(4,36,8,48),
        back=(12,36,16,48),
        left=(0,36,4,48),
        right=(8,36,12,48),
        top=(4,32,8,36),
        bottom=(8,32,12,36)
    )
    glPopMatrix()

# =============================
# Player Assembly
# =============================
def draw_player(show_layers=False):
    # Head
    glPushMatrix()
    glTranslatef(0,22,0)  # player origin at feet
    draw_head()
    if show_layers:
        draw_head_layer()
    glPopMatrix()

    # Body
    draw_body()
    if show_layers:
        draw_body_layer()

    # Arms
    draw_arm(-6)
    draw_arm(6)
    if show_layers:
        draw_arm_layer(-6)
        draw_arm_layer(6)

    # Legs
    draw_leg(-2)
    draw_leg(2)
    if show_layers:
        draw_leg_layer(-2)
        draw_leg_layer(2)

# =============================
# Main Loop with Mouse Drag Rotation
# =============================
def main():
    pygame.init()
    display = (300,500)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_CULL_FACE)  # prevent missing faces

    gluPerspective(45,(display[0]/display[1]),0.1,100.0)
    glTranslatef(0.0,-10,-60)

    texture = load_texture("skin.png")

    # --- rotation state ---
    rotation_x = 0.0  # pitch
    rotation_y = 0.0  # yaw
    mouse_down = False
    last_mouse_pos = (0, 0)
    sensitivity = 0.3  # adjust as needed

    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    mouse_down = True
                    last_mouse_pos = pygame.mouse.get_pos()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    x, y = pygame.mouse.get_pos()
                    dx = x - last_mouse_pos[0]
                    dy = y - last_mouse_pos[1]
                    last_mouse_pos = (x, y)

                    rotation_y += dx * sensitivity
                    rotation_x += dy * sensitivity

                    # optional: clamp pitch so model doesn't flip
                    rotation_x = max(min(rotation_x, 90), -90)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glBindTexture(GL_TEXTURE_2D, texture)

        glPushMatrix()
        glRotatef(rotation_x, 1, 0, 0)  # pitch (up/down)
        glRotatef(rotation_y, 0, 1, 0)  # yaw (left/right)
        glTranslatef(0, 8, 0)
        draw_player(show_layers=True)
        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

main()