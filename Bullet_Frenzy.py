import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

targeting_system = False
first_person_mode = False
state={'points':0,'h':5,'e':0}
cam_pos=[600,600,0]
game_ended = False
avatar_characteristics={'angle':0.0, "x":0.0, "y":0.0, "z": 0.0,'h': 11.5}
projectiles = []
adversaries = []

def display_projectile(proj):
    glPushMatrix()
    glColor3f(0.9, 0.1, 0.1)
    glTranslatef(proj[1], proj[2], proj[3])
    glRotatef(proj[4], 0, 1, 0)
    glutSolidCube(5)
    glPopMatrix()
    
def update_adversary(adv):
    dx = avatar_characteristics['x'] - adv[0]
    dz = avatar_characteristics['z'] - adv[2]
    dist = math.sqrt(dx**2 + dz**2)
    if dist > 0:
        adv[0] += (dx / dist) * adv[3]
        adv[2] += (dz / dist) * adv[3]
    adv[4] += adv[5]
    if adv[4] > 1.3 or adv[4] < 0.7:
        adv[5] *= -1

def display_adversary(adv):
    if adv[6]:
        return
    glPushMatrix()
    glTranslatef(adv[0], adv[1], adv[2])
    glScalef(adv[4], adv[4], adv[4])
    glColor3f(0.8, 0.0, 0.0)
    glutSolidSphere(12, 18, 18)
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(0, 12, 0)
    glutSolidSphere(8, 14, 14)
    glPopMatrix()
    glPopMatrix()

def display_avatar():
    glPushMatrix()
    glTranslatef(avatar_characteristics['x'], 0, avatar_characteristics['z'])
    glRotatef(avatar_characteristics['angle'], 0, 1, 0)
    if game_ended:
        glRotatef(90, 1, 0, 0)
    glColor3f(0.5, 0.0, 0.9)
    for x in [6, -6]:
        glPushMatrix()
        glTranslatef(x, 18, 0)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 5, 2.5, 22, 10, 5)
        glPopMatrix()
    glColor3f(0.3, 0.7, 0.3)
    glPushMatrix()
    glTranslatef(0, 32, 0)
    glScalef(18, 28, 9)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, 55, 0)
    glutSolidSphere(9, 14, 14)
    glPopMatrix()
    glColor3f(0.7, 0.6, 0.5)
    for x in [-11, 11]:
        glPushMatrix()
        glTranslatef(x, 42, 0)
        gluCylinder(gluNewQuadric(), 3.5, 1.8, 16, 10, 2)
        glPopMatrix()
    if not game_ended:
        glColor3f(0.6, 0.6, 0.6)
        glPushMatrix()
        glTranslatef(0, 32, 5)
        glRotatef(15, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 3, 1.8, 18, 10, 2)
        glPopMatrix()
    glPopMatrix()

def first_person_draw():
    glPushMatrix()
    glTranslatef(avatar_characteristics['x'], 0, avatar_characteristics['z'])
    glRotatef(avatar_characteristics['angle'], 0, 1, 0)
    glColor3f(0.7, 0.6, 0.5)
    for x in [-8, 8]:  
        glPushMatrix()
        glTranslatef(x, 35, 10) 
        glutSolidSphere(3, 10, 10) 
        glPopMatrix()
    glColor3f(0.6, 0.6, 0.6)
    glPushMatrix()
    glTranslatef(0, 30, 20)
    glRotatef(10, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 1.8, 18, 10, 2)
    glPopMatrix()
    glPopMatrix()

def display_interface():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT), 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(0.9, 0.9, 0.9)
    y_offset = 25
    for line in [f"Player lives remaining: {state['h']}", f"Game Score: {state['points']}", f"Player Bullets missed: {state['e']}"]:
        glRasterPos2f(15, y_offset)
        for char in line:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        y_offset += 25
    if game_ended:
        glRasterPos2f(glutGet(GLUT_WINDOW_WIDTH) // 2 - 100, glutGet(GLUT_WINDOW_HEIGHT) // 2)
        for char in "Mission Failed - Press R to Retry":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def render_field():
    glPushMatrix()
    grid_width = 1500
    grid_depth = 1000
    tile_size_x = grid_width / 24
    tile_size_z = grid_depth / 24
    for i in range(-12, 12):
        for j in range(-12, 12):
            glColor3f(0.9, 0.9, 0.9) if (i + j) % 2 == 0 else glColor3f(0.5, 0.3, 0.7)
            glBegin(GL_QUADS)
            glVertex3f(i * tile_size_x, -1, j * tile_size_z)
            glVertex3f((i + 1) * tile_size_x, -1, j * tile_size_z)
            glVertex3f((i + 1) * tile_size_x, -1, (j + 1) * tile_size_z)
            glVertex3f(i * tile_size_x, -1, (j + 1) * tile_size_z)
            glEnd()
    border_x = grid_width / 2
    border_z = grid_depth / 2
    wall_height = 80
    walls = [
        ((0.8, 0.8, 0.8), [(-border_x, -1, -border_z), (border_x, -1, -border_z), (border_x, wall_height, -border_z), (-border_x, wall_height, -border_z)]),
        ((0.1, 0.8, 0.1), [(border_x, -1, -border_z), (border_x, -1, border_z), (border_x, wall_height, border_z), (border_x, wall_height, -border_z)]),
        ((0.1, 0.8, 0.8), [(border_x, -1, border_z), (-border_x, -1, border_z), (-border_x, wall_height, border_z), (border_x, wall_height, border_z)]),
        ((0.1, 0.1, 0.8), [(-border_x, -1, border_z), (-border_x, -1, -border_z), (-border_x, wall_height, -border_z), (-border_x, wall_height, border_z)])
    ]
    glBegin(GL_QUADS)
    for color, vertices in walls:
        glColor3f(*color)
        for x, y, z in vertices:
            glVertex3f(x, y, z)
    glEnd()
    glPopMatrix()

def update_game_state():
    global projectiles, adversaries, state, game_ended
    if game_ended:
        return
    active_projectiles = []
    for p in projectiles:
        advance_projectile(p)
        if not p[0]:
            active_projectiles.append(p)
        elif not p[5]:
            state['e'] += 1
            print(f"Bullet missed: {state['e']}")
            if state['e'] >= 10:
                game_ended = True
                print("Mission Terminated. Retry?")
    projectiles[:] = active_projectiles
    while len(adversaries) < 5:
        adversaries.append(place_adversary())
    new_adversaries = []
    for adv in adversaries:
        update_adversary(adv)
        dx = avatar_characteristics['x'] - adv[0]
        dz = avatar_characteristics['z'] - adv[2]
        if math.sqrt(dx**2 + dz**2) < 25:

            state['h'] -= 1
            print(f"Remaining player life: {state['h']}")
            if state['h'] <= 0:
                game_ended = True
                print("Mission Terminated. Retry?")
            new_adv = place_adversary()
            for p in projectiles:
                if p[6] == adv:
                    p[6] = new_adv
            adv[:] = new_adv
        hit = False
        for p in projectiles:
            dx = p[1] - adv[0]
            dz = p[3] - adv[2]
            if not p[0] and math.sqrt(dx**2 + dz**2) < 12:
                p[0] = p[5] = True
                adv[6] = True
                state['points'] += 1
                new_adv = place_adversary()
                for pr in projectiles:
                    if pr[6] == adv:
                        pr[6] = new_adv
                adv[:] = new_adv
                hit = True
                break
        if not hit:
            new_adversaries.append(adv)
    adversaries[:] = new_adversaries

def advance_projectile(proj):
    if proj[0]:  
        return
    velocity = 6
    boundary_x = (1500 / 2) - 10
    boundary_z = (1000 / 2) - 10
    if proj[6] and not proj[6][6]:
        tx = proj[6][0] - proj[1]  
        ty = proj[6][1] - proj[2]  
        tz = proj[6][2] - proj[3]  
        distance = math.sqrt(tx**2 + ty**2 + tz**2)
        if distance > 0.5:  
            next_x = proj[1] + (tx / distance) * velocity
            next_y = proj[6][1] 
            next_z = proj[3] + (tz / distance) * velocity
        else:
            proj[0] = True  
            return
    else:  
        tx = math.sin(math.radians(proj[4]))
        ty = 0 
        tz = math.cos(math.radians(proj[4]))
        distance = 1 
        next_x = proj[1] + tx * velocity
        next_y = proj[2]  
        next_z = proj[3] + tz * velocity
    if abs(next_x) < boundary_x and abs(next_z) < boundary_z:
        proj[1], proj[2], proj[3] = next_x, next_y, next_z
    else:
        proj[0] = True  

def view():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(65, 1.3, 0.6, 2000)  
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if first_person_mode:

        eye_level = avatar_characteristics['h'] + 32
        px, py, pz = avatar_characteristics['x'], avatar_characteristics['y'] + eye_level, avatar_characteristics['z']
        offset = 90
        tx = px + offset * math.sin(math.radians(avatar_characteristics['angle']))
        ty = py
        tz = pz + offset * math.cos(math.radians(avatar_characteristics['angle']))
        gluLookAt(px, py, pz, tx, ty, tz, 0, 1, 0)
    else:
        x,y,z=cam_pos
        gluLookAt(x, y, z, 0, 0, 0, 0, 1, 0)

def launch_projectile():
    global projectiles
    selected_target = None
    if targeting_system:
        closest_dist = float('inf')
        for a in adversaries:
            if not a[6] and not a[7]:
                dx = a[0] - avatar_characteristics['x']
                dz = a[2] - avatar_characteristics['z']
                dist = math.sqrt(dx**2 + dz**2)
                if dist < closest_dist:
                    closest_dist, selected_target = dist, a
        if selected_target:
            selected_target[7] = True
    px, py, pz = avatar_characteristics['x'] + 15 * math.sin(math.radians(avatar_characteristics['angle'])), avatar_characteristics['y'] + 30,avatar_characteristics['z'] + 20* math.cos(math.radians(avatar_characteristics['angle']))

    boundary_x = (1500 / 2) - 25
    boundary_z = (1000 / 2) - 25
    px = max(min(px, boundary_x), -boundary_x)
    pz = max(min(pz, boundary_z), -boundary_z)
    proj = [False, px, py, pz, avatar_characteristics['angle'], False, selected_target]
    projectiles.append(proj)
    print("Player Bullet Fired!")

def move_avatar(dx, dz):
    new_x = avatar_characteristics['x'] + dx
    new_z = avatar_characteristics['z'] + dz
    boundary_x = (1500 / 2) - 35
    boundary_z = (1000 / 2) - 35
    if abs(new_x) < boundary_x and abs(new_z) < boundary_z:
        avatar_characteristics['x'] = new_x
        avatar_characteristics['z'] = new_z
        
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    view()
    render_field()
    if not first_person_mode or game_ended:
        display_avatar()
    else:
        first_person_draw()
    for a in adversaries:
        display_adversary(a)
    for p in projectiles:
        if not p[0]:
            display_projectile(p)
    display_interface()
    glutSwapBuffers()

def Keyboard_Listener(key, x, y):
    global avatar_characteristics, projectiles, adversaries, targeting_system, first_person_mode, state, game_ended,cam_pos
    if game_ended:
        if key == b'r':
            avatar_characteristics={'angle':0.0, "x":0.0, "y":0.0, "z": 0.0,'h': 11.5}
            cam_pos=[600,600,0]
            projectiles = []
            adversaries = []
            targeting_system = False
            first_person_mode = False
            state={'points':0,'h':5,'e':0}
            game_ended = False
            
        return
    if key == b's':
        move_avatar(-6 * math.sin(math.radians(avatar_characteristics['angle'])), -6 * math.cos(math.radians(avatar_characteristics['angle'])))
    elif key == b'w':
        move_avatar(6 * math.sin(math.radians(avatar_characteristics['angle'])), 6 * math.cos(math.radians(avatar_characteristics['angle'])))
    elif key == b'a':
        avatar_characteristics['angle']+= 6
    elif key == b'd':
        avatar_characteristics['angle']-= 6
    elif key == b'c':
        targeting_system = not targeting_system
    elif key == b'v' and targeting_system:
        first_person_mode = not first_person_mode
def place_adversary(value=None):
    theta = random.uniform(0, 2 * math.pi)
    radius = random.uniform(200, 400)
    return [radius * math.sin(theta), 12, radius * math.cos(theta), random.uniform(0.1, 0.6), 1.0, 0.03, False, False]

def special_Key_Listener(key, x, y):
    global cam_pos
    if key == GLUT_KEY_LEFT:
        cam_pos[2] = min(cam_pos[2]+ 6,500)
    elif key == GLUT_KEY_RIGHT:
        cam_pos[2] = max(cam_pos[2] -6, -500)
    elif key == GLUT_KEY_UP:
        cam_pos[1] = min(cam_pos[1] + 12, 1000)
    elif key == GLUT_KEY_DOWN:
        cam_pos[1] = max(cam_pos[1] - 12, 200)

def mouse_Listener(btn, state, x, y):
    if btn == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        launch_projectile()
    elif btn == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        global first_person_mode
        first_person_mode = not first_person_mode

def animation():
    global avatar_characteristics
    update_game_state()
    if targeting_system and not game_ended:
        closest_enemy = None
        min_dist = float('inf')
        for a in adversaries:
            if a[6] or a[7]:
                continue
            dx = a[0] - avatar_characteristics['x']
            dz = a[2] - avatar_characteristics['z']
            dist = math.sqrt(dx**2 + dz**2)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = a
        if closest_enemy:
            dx = closest_enemy[0] - avatar_characteristics['x']
            dz = closest_enemy[2] - avatar_characteristics['z']
            enemy_angle = math.degrees(math.atan2(dx, dz)) % 360
            angle_diff = ((enemy_angle - avatar_characteristics['angle']) + 180) % 360 - 180
            avatar_characteristics['angle'] += angle_diff * 0.08
            if abs(angle_diff) < 8 and random.random() < 0.04:
                launch_projectile()
    for a in adversaries:
        if a[6] or not any(p[6] == a and not p[0] for p in projectiles):
            a[7] = False
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutInitWindowPosition(120, 120)
    glutCreateWindow(b"22201604_3d_game")
    for _ in range(5):
        adversaries.append(place_adversary())
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(Keyboard_Listener)
    glutSpecialFunc(special_Key_Listener)
    glutMouseFunc(mouse_Listener)
    glutIdleFunc(animation)
    glutMainLoop()

if __name__ == "__main__":
    main()
