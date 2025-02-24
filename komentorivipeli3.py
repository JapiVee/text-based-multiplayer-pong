import time
import sys
import math
import os
import shutil
import subprocess
import random
import msvcrt
import socket
import threading
import json
import re
def clear_input():
    while msvcrt.kbhit():
        msvcrt.getch()
try:
    import keyboard
except ImportError:
    print("keyboard module not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "keyboard"])
    print("module installed, start again to play")
    input("Press enter to close the program...")
    exit(1)
os.system('cls' if os.name == 'nt' else 'clear')

HOST = "jaromc.vallirinne.fi"  # The server's hostname or IP address
PORT = 5678  # The port used by the server

new_message = threading.Event()
new_output = threading.Event()
output_ready_to_write = threading.Event()
input_ready_to_write = threading.Event()
input_ready_to_write.set()
new_output.clear()
readbuffer = ""
onlinestate = False
connected = False
online_turn = False
ball_hidden_on_start = False
outputbuffer = ""
flickercolor = 31
ball_incoming = False
username = ""
compression = True
def read(sock):
    read_temp_buffer = b""
    while True:
        global connected, readbuffer
        try:
            recv_data = sock.recv(1024)
            if not recv_data:
                connected = False
                break
            read_temp_buffer += recv_data
            decoded_data_list = read_temp_buffer.decode().split("__end1337__")
            while (len(decoded_data_list) > 1):
                input_ready_to_write.wait(1)
                to_handle = decoded_data_list[0]
                decoded_data_list.pop(0)
                readbuffer += to_handle
                input_ready_to_write.clear()
                new_message.set()
            read_temp_buffer = bytes(decoded_data_list[0].encode())
        except:
            return
def sending_loop(sock):
    while True:
        global outputbuffer
        try:
            new_output.wait(timeout=None)
            output_ready_to_write.clear()
            message = outputbuffer
            outputbuffer = ""
            output_ready_to_write.set()
            new_output.clear()
            sock.sendall(bytes(message + "__end1337__", "utf-8"))
        except:
            return
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sending_thread = threading.Thread(target=sending_loop, args=(sock,), daemon=True)
connection = threading.Thread(target=read, args=(sock,), daemon=True)
def connect_to_server():
    global sock, connected, sending_thread, connection
    sock.connect((HOST, PORT))
    connected = True
    sending_thread.start()
    connection.start()

not_big_enough = True
losecolor = 31
startcolor = 37 #not needed to be changed
flickertime = 18 #how many ticks in between the flicker
letter = "."
bar_one_char = "|"
bar_two_char = "|"
ball_char = "O"
speed = 2
delay = 2
bat_size = 10
spin = 0.7
boostduration = 0.1
boostreload = 3
boost_speed = 0.25
boost_char = "-"
max_startangle = 1
start_clicks = 40
dying_duration = 3
width = 120
height = 30
force_dimensions = False
life_count = 0
life_letter = "*"
ball_incoming_letter = "<"


def load_variables(object):
    global letter, bar_one_char, bar_two_char, ball_char, speed, delay, bat_size, spin, boostduration, boostreload, boost_speed, boost_char, max_startangle, start_clicks, dying_duration, width, height, force_dimensions
    letter = object["background_character"]
    bar_one_char = object["racket_one_character"]
    bar_two_char = object["racket_two_character"]
    ball_char = object["ball_character"]
    speed = object["ball_starting_speed"]
    delay = object["racket_moving_wait_time"]
    bat_size = object["racket_size"]
    spin = object["racket_spin"]
    boostduration = object["boost_duration"]
    boostreload = object["boost_reload_time"]
    boost_speed = object["boost_speed"]
    boost_char = object["boost_character"]
    max_startangle = object["max_pass_angle"]
    start_clicks = object["pass_click_count"]
    dying_duration = object["losing_scene_duration"]
    width = object["width"]
    height = object["height"]
    force_dimensions = object["force_dimensions"]

def pack_settings():
    response_object = {
            "background_character":letter,
            "racket_one_character":bar_one_char,
            "racket_two_character":bar_two_char,
            "ball_character":ball_char,
            "ball_starting_speed":speed,
            "racket_moving_wait_time":delay,
            "racket_size":bat_size,
            "racket_spin":spin,
            "boost_duration":boostduration ,
            "boost_reload_time":boostreload,
            "boost_speed":boost_speed, 
            "boost_character":boost_char,
            "max_pass_angle":max_startangle,
            "pass_click_count":start_clicks,
            "losing_scene_duration":dying_duration,
            "width":width,
            "height":height,
            "force_dimensions":force_dimensions
        }
    return response_object
def interactive_select(set_dims = False):
    global letter, bar_one_char, bar_two_char, ball_char, speed, delay, bat_size, spin, boostduration, boostreload, boost_speed, boost_char, max_startangle, start_clicks, dying_duration, width, height, force_dimensions
    letter = input("Set a background character:")
    print("Success!")
    bar_one_char = input("Set a character for player one racket:")
    print("Success!")
    bar_two_char = input("Set a character for player two racket:")
    print("Success!")
    ball_char = input("Set a character for the ball:")
    print("Success!")
    new_xvel = input("Set ball speed (default:2, float):")
    speed = float(new_xvel)
    print("Success!")
    bat_speed = input("Set bat moving delay in ticks (default:2, integer):")
    delay = int(bat_speed)
    print("Success!")
    new_bat_size = input("Set bat size (default:10, integer):")
    bat_size = int(new_bat_size)
    print("Success!")
    new_startangle = float(input("Set maximum pass angle (default:1, float):"))
    max_startangle = new_startangle
    print("Success!")
    new_starclicks = input("Set click count to generate spin to a pass (default:40, integer):")
    start_clicks = int(new_starclicks)
    print("Success!")
    new_boost = input("Set new boost speed (default:0.25, float):")
    boost_speed = float(new_boost)
    print("Success!")
    if (set_dims):
        height = int(input("How high should the game area be? (default:30, integer):"))
        width = int(input("How wide should the game area be? (default:120, integer):"))
    time.sleep(0.5)    

def select_configuration(response = False, set_dims = False):
    choice = input("Do you want to use (d)efault values, load a (f)ile, or use (i)nteractive setup (d|f|i):")
    if (choice.lower() == "f"):
        fname = input("Type the configuration file name, leave empty for default file:")
        if (fname == ""):
            fname = "settings.json"
        file = open(fname)
        raw_json = file.read().split("\n")
        uncommented_json = ""
        for row in raw_json:
            uncommented_json += row.split("//")[0]
        load_variables(json.loads(uncommented_json))
    elif (choice.lower() == "i"):
        interactive_select(set_dims)
    if (response):
        return pack_settings()
    
gametype = input("Play on (l)ocal machine or (c)reate a new online gameroom or (j)oin into an existing game or (w)atch an online game(l|c|j|w):")
if (gametype.lower() == "c"):
    connect_to_server()
    settings = select_configuration(True, True)
    settings["force_dimensions"] = True
    life_count = int(input("How many lives a player should have:"))
    settings["life_count"] = life_count
    onlinestate = True
    online_turn = True
    name = input("Give a nickname to be displayed to other players:")
    username = name
    sock.sendall(bytes("03" + name + "__end1337__","utf-8"))
    new_message.wait(timeout=5)
    print(readbuffer)
    code = readbuffer
    readbuffer = ""
    input_ready_to_write.set()
    new_message.clear()
    while True:
        gameroom = input("Give 5 character name to your gameroom:")
        if (len(gameroom)==5):
            break
    columns, rows = shutil.get_terminal_size()
    settings_encoded = json.dumps(settings)
    gameroom_response = "01" + gameroom + "__server1337__" + settings_encoded
    sock.sendall(bytes(gameroom_response + "__end1337__", "utf-8"))
    new_message.wait(timeout=5)
    print(readbuffer)
    readbuffer = ""
    input_ready_to_write.set()
    new_message.clear()
    list_to_print = [code, "Your gameroom code: " + gameroom,"Waiting for other players to join. Press Ctrl + Enter to start the online game..."]
    index_object = {}
    sys.stdout.write("\033[H\033[J") 
    sys.stdout.write(f"\r{"\n".join(list_to_print)}")
    while True:
        if keyboard.is_pressed(28) and keyboard.is_pressed(29):
            print("\nStarting....")
            time.sleep(1)
            break
        if(new_message.is_set()):
            inputlist = readbuffer.split("__server1337__")
            if (inputlist[0] in index_object):
                list_to_print[index_object[inputlist[0]]] = inputlist[1]
            else:
                list_to_print.append(inputlist[1])
                index_object[inputlist[0]] = len(list_to_print) - 1
            sys.stdout.write("\033[H\033[J") 
            sys.stdout.write(f"\r{"\n".join(list_to_print)}")
            readbuffer = ""
            input_ready_to_write.set()
            new_message.clear()
elif (gametype.lower() == "j"):
    connect_to_server()
    onlinestate = True
    ball_hidden_on_start = True
    name = input("Give a nickname to be displayed to other players:")
    username = name
    sock.sendall(bytes("03" + name + "__end1337__","utf-8"))
    new_message.wait(timeout=5)
    print(readbuffer)
    readbuffer =""
    new_message.clear()
    join_code = input("Give 5 character join code (gameroom name):")
    join_code = "02" + join_code
    sock.sendall(bytes(join_code + "__end1337__", "utf-8"))
    new_message.wait(timeout=5)
    temp_list = readbuffer.split("__server1337__")
    readbuffer =""
    input_ready_to_write.set()
    new_message.clear()
    print(temp_list[0])
    transferred_settings = json.loads(temp_list[1])
    load_variables(transferred_settings)
    life_count = transferred_settings["life_count"]
    input("Press enter to continue...")
elif (gametype.lower() == "w"):
    connect_to_server()
    buffer_size = int(input("How long input buffer should you have? A longer buffer enables smoother playback with more delay. Input a integer of how many frames buffer you want to have:"))
    uni_id = input("If you want to, you can give your unique id to enchance the tv. Leave empty to skip:")
    room_code = input("Give a 5 character room name:")
    if (uni_id == ""):
        uni_id = 0
    sock.sendall(bytes("04" + room_code + "__server1337__" + str(uni_id) + "__end1337__" ,"utf-8"))
    new_message.wait(timeout=5)
    print(readbuffer.split("__server1337__")[0])
    watch_settings = json.loads(readbuffer.split("__server1337__")[1])
    readbuffer =""
    input_ready_to_write.set()
    new_message.clear()
    letter = watch_settings["background_character"]
    size_not_set = True
    watch_tick = 0
    draw_buffer = []
    host_framerate = 60
    watch_framerate = 60
    watch_target_framerate = 60
    framerate_increment = 0
    playback_started = False
    watch_frame_time = time.time()
    os.system('cls' if os.name == 'nt' else 'clear')
    win_message = ""
    print("\033[?25l", end="")
    while True:
        watch_tick_start = time.time() 
        catchup = 0
        if (size_not_set == True): #Händlää terminaalin koko
            msg = "Here you can adjust the terminal size. It should be:" + str(watch_settings["width"]) +"x"+ str(watch_settings["height"])+ " Confirm with Enter when adjusted. \n"
            columns, rows = shutil.get_terminal_size()
            msg += "Current size:" + str(columns) + "x" + str(rows) + "\n"
            draw_buffer.append([msg,60])
            if (columns == watch_settings["width"] and rows == watch_settings["height"] and keyboard.is_pressed(28)):
                    size_not_set = False
                    sys.stdout.write("\033[H\033[J")
                    draw_buffer = [["You're all set!",60]]
                    outputbuffer += "08"
                    new_output.set()
        if keyboard.is_pressed(1):
            sock.close()
            exit(1)
        if(new_message.is_set()):
            if (readbuffer[:2]=="03"):
                draw_buffer = draw_buffer + json.loads(readbuffer[2:])
            elif(readbuffer[:2] == "04"):
                win_message = readbuffer[2:]
                break
            if (readbuffer[:2] == "05"):
                sys.stdout.write("\033[H\033[J")
                draw_buffer = []
                draw_buffer += json.loads(readbuffer[2:])
            if (len(draw_buffer)>buffer_size + 20):
                framerate_increment = 3
            else:
                framerate_increment = 0
            if (len(draw_buffer) > buffer_size + 120):
                draw_buffer = draw_buffer[-buffer_size:]
            readbuffer = ""
            input_ready_to_write.set()
            new_message.clear()
        if (len(draw_buffer) > buffer_size or (playback_started and len(draw_buffer) > 0)):
            playback_started = True
            if (isinstance(draw_buffer[0][0],list)):
                draw_buffer[0][0] = "".join([x[0]+x[1]*letter for x in draw_buffer[0][0]])
            sys.stdout.write("\033[H")
            sys.stdout.write(f"\r{draw_buffer[0][0]}")#draw_buffer[0][0][:len(draw_buffer[0][0])-20] + str(int(len(draw_buffer))) + draw_buffer[0][0][len(draw_buffer[0][0])-12:]
            sys.stdout.flush()
            if (watch_tick%30==29):
                watch_framerate=30/(time.time() - watch_frame_time)
                watch_frame_time = time.time()
            watch_tick += 1
            
            watch_target_framerate = int(draw_buffer[0][1] + framerate_increment)
            if (watch_target_framerate < 45):
                watch_target_framerate = 50
            watch_tick_duration = time.time() - watch_tick_start
            if ((watch_tick_duration)<1/watch_target_framerate): #Käytä juuri oikean framen frameratea ja sen lisäksi aseta mahdollinen kirimisaikataulu vähennys muuttuja. 
                time.sleep((1/watch_target_framerate)-(watch_tick_duration))
            elif (watch_tick_duration<1/watch_target_framerate):
                catchup -= ((1/watch_target_framerate)-watch_tick_duration)
            else:
                catchup += -1*((1/watch_target_framerate)-watch_tick_duration)
            draw_buffer.pop(0)
        else:
            playback_started = False
            watch_tick += 1
            watch_tick_duration = time.time() - watch_tick_start
            if (watch_tick_duration<1/60):
                time.sleep((1/60)-watch_tick_duration)
    sock.close()
    os.system('cls' if os.name == 'nt' else 'clear')
    input( win_message + " Press enter to close...")
    exit(1)
elif(gametype.lower() == "l"):
    select_configuration()
    
print("\033[?25l", end="")
score_one = 0
score_two = 0
framerate = 0
frame_time = 0

def ball_reset_callback():
    global flickercolor, losecolor
    ball.reset()
    flickercolor = 31
    losecolor = 31
def show_ball_callback():
    global ball_incoming
    ball.hidden = False
    ball_incoming = False
class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.output = (height*width-1)*letter
        self.flickertimer = 0
        self.setflicker = False
        self.flicker = ""
        self.flicker_start = []
        self.flicker_end = []
        self.flicker_callback = None
    def update(self, width, height):
        self.width = width
        self.height = height
        self.output = (height*width-1)*letter
    def project_flicker(self):
        start = self.flicker_start
        end = self.flicker_end
        color = losecolor
        if self.flickertimer > 0:
            for i in range (start[1], end[1]):   
                self.output = self.output[:((i*self.width + start[0] - 1) + i*9)] + "\033["+str(color) + "m" + self.output[((i*self.width + start[0])+i*9-1):((i*self.width + end[0] - 1)+i*9)+1] + "\033[0m" + self.output[((i*self.width + end[0])+i*9):]
            self.flickertimer -= 1
        elif not self.flicker_callback == None:
            self.setflicker = False
            self.flicker_callback()
            self.flicker_callback = None

    def change_letters(self, start, end, character):
        for i in range (start[1], end[1] + 1):
            self.output = self.output[:(i*self.width + start[0] - 1)] + character * (end[0] - start[0] + 1) + self.output[(i*self.width + end[0]):]
    def clear(self):
        if (onlinestate):
            self.output = life_letter*life_count + str(life_count)+(self.width-life_count-len(str(life_count)))*letter + (int((self.height-1)*self.width- 4 - len(username) - 5))*letter + str(username) + 5*letter + str(int(framerate)) + letter
        else:
            self.output = str(score_one) + (self.width-2)*letter + str(score_two) + (int((self.height-1)*self.width- 4))*letter + str(int(framerate)) + letter
    def setFlicker(self, start, end, callback):
        self.setflicker = True
        self.flicker_callback = callback
        self.flicker_start = start
        self.flicker_end = end
gameboard = Board(1, 1)

class Bat:
    def __init__(self, x, y, size, char, boost_x):
        self.x = x
        self.x_base = x
        self.size = size
        self.char = char
        self.y = y
        self.maxdelay = delay
        self.delay = 0
        self.boost = False
        self.boostdelay = int(-1*boostduration*60)
        self.boostx = boost_x
        self.startangle = 0
    def project(self):
        gameboard.change_letters([self.x,self.y],[self.x,(self.y + self.size - 1)], self.char)
    def update(self):
        self.project()
        if (self.delay>0):
            self.delay -= 1
        if (self.boost):
            if(tick%4==0):
                self.x += 1
            if(tick%4==2):
                self.x -= 1
            if (self.boostdelay == 0):
                self.boost = False
                self.x = self.x_base
        
        if (self.boostdelay > int(-1*boostduration*60)):
            gameboard.change_letters([self.boostx, int((gameboard.height-1)-(self.boostdelay+boostduration*60)/(boostreload*60+boostduration*60)*(gameboard.height-1))],[self.boostx, gameboard.height-2],boost_char)
            self.boostdelay+=1
            if (self.boostdelay > int(boostreload*60 -(boostduration*60))):
                self.boostdelay = int(-1*boostduration*60)
    def move_up(self):
        if (self.y > 0 and self.delay == 0):
                self.y -= 1
                self.delay = self.maxdelay
                self.project()
    def move_down(self):
        if (self.y < (gameboard.height - self.size) and self.delay == 0):
                self.y += 1
                self.delay = self.maxdelay
                self.project()
    def startboost(self):
        if (self.boostdelay == int(-1*boostduration*60)):
            self.x_base = self.x
            self.boost = True
            self.boostdelay += 1

bat_one = Bat(2, 6, bat_size, bar_one_char, 1)
bat_two = Bat(10, 6, bat_size, bar_two_char, 1)
flickercoords = [0,0]
class Ball:
    def __init__(self,x,y,char,hidden):
        self.x = x
        self.y = y
        self.char = char
        self.xvel = speed
        self.speed = speed
        self.yvel = 0
        self.life_count = 1
        self.hidden = hidden
    def project(self):
        if (self.hidden):
            return
        gameboard.change_letters([int(self.x),int(self.y)],[int(self.x), int(self.y)],self.char)
    def raycast(self, bat, bounce):
        previous_x = self.x - self.xvel
        previous_y = self.y - self.yvel
        k = 0
        if (self.x < previous_x):
            k = (previous_y-self.y)/(previous_x-self.x)
        else:
            k = (self.y-previous_y)/(self.x-previous_x)
        cuty = k*bat.x-k*self.x+self.y
        starty = bat.y
        endy = bat.y + bat.size
        if (starty - 0.5 <= cuty <= endy + 0.5):
            distance = self.speed - math.hypot((self.x-previous_x),(self.y-previous_y))
            self.yvel += ((cuty-(bat.y-0.5))/(bat.size+1)-0.5)*spin
            if (bat.boost):
                self.speed += boost_speed
            self.check_speed(bounce)
            bouncedistance = self.speed - distance
            self.x = bat.x + (bouncedistance*self.xvel)/self.speed
            self.y = cuty + (bouncedistance*self.yvel)/self.speed

    def check_speed(self, bounce):
        if (self.yvel >= (self.speed - 0.1) or self.yvel<= (-1*self.speed + 0.1)):
            self.speed = abs(self.yvel) + 0.2
        self.xvel = bounce*((self.speed**2-self.yvel**2)**(1/2))
                    
    def update(self):
        global flickercoords, score_one, score_two, running, life_count
        if (self.hidden):
            return
        bounce = -1#+((random.random()-0.45)*0.01)
        self.x += self.xvel
        self.y += self.yvel
        if (self.y >= gameboard.height):
            self.yvel *= bounce
            self.y = gameboard.height + (gameboard.height - self.y)
        elif (self.y <= 0):
            self.yvel *= bounce
            self.y *= -1
        if (self.x<=2 ):
            if (gameboard.setflicker == False):
                    self.raycast(bat_one, 1)
        if (self.x>=gameboard.width and not onlinestate):
            if (gameboard.setflicker == False):
                self.raycast(bat_two, -1)
        if (self.x > gameboard.width):
            if (onlinestate):
                self.x = gameboard.width
                self.send()
            else:
                self.xvel=0
                self.yvel=0
                self.x = gameboard.width
                flickercoords = [[int(gameboard.width/2),0],[gameboard.width,gameboard.height]]
                gameboard.flickertimer = dying_duration*60
                gameboard.setFlicker(flickercoords[0], flickercoords[1],ball_reset_callback)
                score_one += 1
                if (score_one == 10):
                    running = False
        elif (self.x < 1):
            self.xvel = 0
            self.yvel=0
            self.x = 1
            flickercoords = [[1,0],[int(gameboard.width/2),gameboard.height]]
            gameboard.flickertimer = dying_duration*60
            gameboard.setFlicker(flickercoords[0], flickercoords[1],ball_reset_callback)
            if (onlinestate):
                life_count -= 1
                if (life_count == 0):
                    self.send()
            else:
                score_two += 1
                if (score_two == 10):
                    running = False
        self.project()
    def reset(self):
        self.hidden = False
        self.speed = speed 
        if (self.x == 1):
            if (bat_one.startangle >= start_clicks or bat_one.startangle <= -1*start_clicks):
                self.yvel = math.copysign(max_startangle,bat_one.startangle)
            else:
                self.yvel = math.copysign(max_startangle*(bat_one.startangle/start_clicks), bat_one.startangle)
            bat_one.startangle = 0
            self.check_speed(1)
            self.x = 2.1
            self.y = bat_one.y + bat_one.size/2
        else:
            if (bat_two.startangle >= start_clicks or bat_two.startangle <= -1*start_clicks):
                self.yvel = math.copysign(max_startangle,bat_two.startangle)
            else:
                self.yvel = math.copysign(max_startangle*(bat_two.startangle/start_clicks), bat_two.startangle)
            bat_two.startangle = 0
            self.check_speed(-1)
            self.x = gameboard.width - 1.1
            self.y = bat_two.y + bat_two.size/2
    def receive(self, data):
        global online_turn, losecolor, ball_incoming, flickercolor
        if (not data["life_count"] == 0):
            self.x = data["x"]
            self.y = data["y"]
            self.xvel = data["xvel"]
            self.yvel = data["yvel"]
            self.speed = data["speed"]
            online_turn = True
            flickercoords = [[gameboard.width,0],[gameboard.width,gameboard.height]]
            gameboard.flickertimer = 2*60
            gameboard.setFlicker(flickercoords[0], flickercoords[1],show_ball_callback)
            ball_incoming = True
        else:
            self.x = 1
            losecolor = 32
            flickercolor = 32
            flickercoords = [[1,0],[int(gameboard.width/2),gameboard.height]]
            gameboard.flickertimer = dying_duration*60
            gameboard.setFlicker(flickercoords[0], flickercoords[1],ball_reset_callback)
            online_turn = True
    def send(self):
        global outputbuffer, online_turn, frames_buffer, framerate, life_count, running
        online_turn = False
        self.xvel *= -1
        self.life_count = life_count
        state_object = json.dumps(self, default=lambda o: o.__dict__)  
        output_ready_to_write.clear()
        status_number = "06"
        if (life_count == 0):
            status_number = "07"
        outputbuffer += status_number + state_object
        new_output.set()
        output_ready_to_write.wait(1)
        json_frames = [[frame, framerate] for frame in frames_buffer]
        outputbuffer += "05"+ json.dumps(json_frames)
        new_output.set()
        frames_buffer = []
        self.hidden = True
        if (life_count == 0):
            running = False
ball = Ball(10,10,ball_char,ball_hidden_on_start)
game_not_started = True
output = ""
running = True
i=0
locks = {30:True, 32:True, 75:True, 77:True}
def release(key):
    locks[key.scan_code] = True
keyboard.on_release_key(30, lambda event: release(event))
keyboard.on_release_key(32, lambda event: release(event))
keyboard.on_release_key(75, lambda event: release(event))
keyboard.on_release_key(77, lambda event: release(event))
frames_buffer = []
frame_time = time.time() 
not_started = True
os.system('cls' if os.name == 'nt' else 'clear')
while(running):
    tick_start = time.time()
    tick = i
    output = ""
    if (not_big_enough == True):
        output += "Here you can adjust the terminal size. "
        if (force_dimensions):
            output += "It should be exactly " + str(width) + "x" + str(height)
        else:
            output += str(width) + "x" + str(height) + " is suggested for this mode. "
        output +="Confirm with Enter when adjusted. \n"
        columns, rows = shutil.get_terminal_size()
        output += "Current size:" + str(columns) + "x" + str(rows) + "\n"
        if (keyboard.is_pressed(28) and (not force_dimensions or (columns == width and rows == height))):
            sys.stdout.write("\033[H\033[J")
            output = ""
            not_big_enough = False
            gameboard.update(columns, rows)
    elif(game_not_started == True):
        output += "Start game by pressing \033["+str(startcolor)+"mspace\033[0m. You can end the game whenever you like by pressing \033["+str(startcolor)+"mesc\033[0m!"
    if (tick%flickertime == 0):
        if (startcolor == 37):
            startcolor = 30
            losecolor = 30
        else:
            startcolor = 37
            losecolor = flickercolor
    if (game_not_started == False):
        if (new_message.is_set()):
            if (readbuffer[:2] == "01" or readbuffer[:2] == "02"): 
                stripped_data = readbuffer[2:]
                received_object = json.loads(stripped_data)
                ball.receive(received_object)
                if (readbuffer[:2] == "02" and received_object["life_count"] == 0):
                    running = False
            readbuffer = ""
            input_ready_to_write.set()
            new_message.clear()    
        output = gameboard.output
        if (keyboard.is_pressed(72)):
            bat_two.move_up()
            if (onlinestate):
                bat_one.move_up()
        if (keyboard.is_pressed(80)):
            bat_two.move_down()
            if (onlinestate):
                bat_one.move_down()
        if (keyboard.is_pressed(17)):
            bat_one.move_up()
        if (keyboard.is_pressed(31)):
            bat_one.move_down()
        if (gameboard.setflicker):
            if (keyboard.is_pressed(32)):
                if (locks[32]):
                    locks[32] = False
                    bat_one.startangle += 1
            if (keyboard.is_pressed(30)):
                if (locks[30]):
                    locks[30] = False
                    bat_one.startangle -= 1
            if (keyboard.is_pressed(75)):
                if (locks[75]):
                    locks[75] = False    
                    bat_two.startangle += 1
            if (keyboard.is_pressed(77)):
                if (locks[77]):
                    locks[77] = False
                    bat_two.startangle -= 1
        else:
            if (keyboard.is_pressed(32)):
                bat_one.startboost()
            if (keyboard.is_pressed(75)):
                bat_two.startboost()
        gameboard.clear()
        if (not onlinestate):
            bat_two.update()
        bat_one.update()
        ball.update()
        if (ball_incoming):
            gameboard.change_letters([gameboard.width, 0],[gameboard.width, gameboard.height-2],ball_incoming_letter)
        gameboard.project_flicker()
    if (keyboard.is_pressed(1)):
        running = False
        sock.close()
        exit(1)
    if (keyboard.is_pressed(57) and not_big_enough == False and not_started):
        not_started = False
        if (not force_dimensions):
            columns, rows = shutil.get_terminal_size()
            gameboard.update(columns, rows)
        game_not_started = False
        bat_one.y = int(gameboard.height/2 - int(bat_one.size/2))
        bat_one.project()
        bat_two.x = gameboard.width - 1
        bat_two.y = int(gameboard.height/2 - int(bat_two.size/2))
        bat_two.boostx = gameboard.width
        bat_two.project()
        ball.x = gameboard.width/2
        ball.y = gameboard.height/2
        if (onlinestate and not ball_hidden_on_start):
            flickercolor = 32
            losecolor = 32
            ball.hidden = True
            ball.x = 1
            flickercoords = [[1,0],[int(gameboard.width/2),gameboard.height]]
            gameboard.flickertimer = dying_duration*60
            gameboard.setFlicker(flickercoords[0], flickercoords[1],ball_reset_callback)
        if (onlinestate and not online_turn):
            outputbuffer += "08"
            new_output.set()
    if online_turn:
        if compression:
            match_list = re.findall(fr"([^\{letter}l]+)(\{letter}+|$)", output)
            compressed_list = []
            for tuple in match_list:
                compressed_list.append([tuple[0], len(tuple[1])])
            frames_buffer.append(compressed_list)
        else:
            frames_buffer.append(output)
    sys.stdout.write("\033[H")       
    sys.stdout.write(f"\r{output}")
    sys.stdout.flush()
    if (tick%30==29): #käyttäjän asetettava frame buffer muuttuja. 
        framerate = 30/(time.time() - frame_time) 
        frame_time = time.time() 
        
    if (online_turn and tick%3==2):
        output_ready_to_write.wait(0.1)
        json_frames = [[frame, framerate] for frame in frames_buffer]
        outputbuffer += "05"+ json.dumps(json_frames)
        new_output.set()
        frames_buffer = []
    i += 1
    tick_duration = time.time() - tick_start
    if (tick_duration<1/60):
        time.sleep((1/60)-tick_duration)
os.system('cls' if os.name == 'nt' else 'clear')
clear_input()
print("\033[?25h")
if (score_one>score_two and (score_one == 10 or score_two == 10)):
    print("Congratulations player One! Player One winned this match. Better luck next time player Two")
elif(score_one<score_two and (score_one == 10 or score_two == 10)):
    print("Congratulations player Two! Player Two winned this match. Better luck next time player One")
if (life_count == 0 and onlinestate):
    print("You died!")
    time.sleep(1)
    sock.close()
else:
    print("You won the game!")
    time.sleep(1)
    sock.close()
a = input("Press enter to exit...")
if (a == "hello"):
    print("hello??? GO AWAY PLZ! Program closes🤷‍♂️")
