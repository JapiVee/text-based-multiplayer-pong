import socket
import selectors
import types
import json
import traceback
sel = selectors.DefaultSelector()

host = '0.0.0.0'
port = 5678
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)
id = 1

yourturn_big = """ ...         ...   .............   ...         ...  ............            ...................  ...         ...  ............     ......         ...
  ...       ...   ...         ...  ...         ...  ...       ....                  ...          ...         ...  ...       ....   ... ...        ...
   ...     ...    ...         ...  ...         ...  ...        ...                  ...          ...         ...  ...        ...   ...  ...       ...
    ...   ...     ...         ...  ...         ...  ...       ...                   ...          ...         ...  ...       ...    ...   ...      ...
      .....       ...         ...  ...         ...  ...........                     ...          ...         ...  ...........      ...    ...     ...
       ...        ...         ...  ...         ...  ...     ...                     ...          ...         ...  ...     ...      ...     ...    ...
       ...        ...         ...  ...         ...  ...      ...                    ...          ...         ...  ...      ...     ...      ...   ...
       ...        ...         ...  ...         ...  ...       ...                   ...          ...         ...  ...       ...    ...       ...  ...
       ...        ...         ...  ...         ...  ...        ...                  ...          ...         ...  ...        ...   ...        ... ...
       ...         .............    .............   ...         ...                 ...           .............   ...         ...  ...         ......""".replace(".","|") #149x10

yourturn_small = """..    ..  ......  ..    .. .......     .......... ..    .. .......   ...    ..
 ..  ..  ..    .. ..    .. ..    ...       ..     ..    .. ..    ... ....   ..
  ....   ..    .. ..    .. ..    ..        ..     ..    .. ..    ..  .. ..  ..
   ..    ..    .. ..    .. .......         ..     ..    .. .......   ..  .. ..
   ..    ..    .. ..    .. ..   ..         ..     ..    .. ..   ..   ..   ....
   ..     ......   ......  ..    ..        ..      ......  ..    ..  ..    ...""".replace(".","|") #78x6

class gameroom: #luo multiprosessing säie aina uudelle gameroomille, jossa voidaan händlätä yhden roomin tyyppejä
    def __init__(self, name, owner, index, ownername, settings):
        self.name = name
        self.owner = owner
        self.owner_updates = ""
        self.index = index
        self.clients = [owner]
        self.tv_clients = []
        self.ownername = ownername
        self.stream_buffer = []
        self.tv_client_states = {}
        self.nextclient = 0
        self.balldata = ""
        self.settings = settings
        self.closed = False
        self.closed_tv_clients = []
        self.id_to_name = {}
        self.win_message = ""
        self.clients_ready = []
    def getInfo(self, id):
        if (not self.closed):
            if (id == self.owner):
                if (len(self.owner_updates) > 0):
                    response = self.owner_updates
                    self.owner_updates = ""
                    return response
            if (id in self.tv_clients):
                if (len(self.stream_buffer) - 3 >= self.tv_client_states[id]):
                    response_text = json.dumps(self.stream_buffer[self.tv_client_states[id]:])
                    self.tv_client_states[id] = len(self.stream_buffer)
                    return "03" + response_text
            if (id == self.clients[self.nextclient] and not self.balldata == ""):
                if (len(self.clients)<=2):
                    response_2 = "02" + self.balldata
                else:
                    response_2 = "01" + self.balldata
                self.balldata = ""
                self.setnextclient()
                return response_2
        elif (id in self.tv_clients and not id in self.closed_tv_clients):
            self.closed_tv_clients.append(id)
            return "04" + self.win_message
        return True
    def strip_buffer(self):
        if (len(self.tv_client_states) == 0):
            self.stream_buffer = []
            return
        smallest_video_playback_frame = min(self.tv_client_states.values())
        for state in self.tv_client_states:
            self.tv_client_states[state] -= smallest_video_playback_frame
        self.stream_buffer = self.stream_buffer[smallest_video_playback_frame:]
    def setnextclient(self):
        if (self.nextclient == len(self.clients)-1):
            self.nextclient = 0
        else:
            self.nextclient += 1

gameroom_collection = [] 

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                data.inb += recv_data


                def handle_a_message(message):
                    response = ""
                    action_id = message[0:2]
                    real_data = message[2:]
                    if action_id == "01":
                        roomname = real_data.split("__server1337__")[0]
                        game_settings = json.loads(real_data.split("__server1337__")[1])
                        new_gameroom = gameroom(roomname, data.id, len(gameroom_collection), data.name, game_settings)
                        gameroom_collection.append(new_gameroom)
                        new_gameroom.id_to_name[data.id] = data.name
                        data.gameroom = len(gameroom_collection) - 1
                        response = f"Successfully created gameroom named:{new_gameroom.name}"
                        # Turvallinen muunnos
                    if action_id == "02":
                        for room in gameroom_collection:
                            if room.name == real_data:
                                data.gameroom = room.index
                                room.id_to_name[data.id] = data.name
                                room.clients.append(data.id)
                                room.nextclient = 1
                                room.owner_updates = str(data.id) + "__server1337__" + data.name + " joined into your room\033[31m - Not ready\033[0m"
                                response = f"Successfully joined to a gameroom:{room.name} of owner:{room.ownername}" + "__server1337__" + json.dumps(room.settings)
                                break
                        else:
                            response = "Unfortunately gameroom with such name did not found"
                    if (action_id == "03"):
                        data.name = real_data
                        response = "Your unique id is:" +str(data.id) + " It is used to handle tv correctly." 
                    if (action_id == "04"):
                        room_name = real_data.split("__server1337__")[0]
                        uni_id = int(real_data.split("__server1337__")[1])
                        data.secondary_id =uni_id
                        for room in gameroom_collection:
                            if room.name == room_name:
                                data.gameroom = room.index
                                room.tv_clients.append(data.id)
                                room.tv_client_states[data.id] = 0
                                room.owner_updates = str(data.id) + "__server1337__" + "A tv instance joined into your room\033[31m - Not ready\033[0m"
                                response = f"Successfully watching game at gameroom:{room.name} of owner:{room.ownername}" + "__server1337__" + json.dumps(room.settings)
                                break
                        else:
                            response = "Unfortunately gameroom with such name did not found"
                    if (action_id == "05"):
                        gameroom_collection[data.gameroom].stream_buffer.extend(json.loads(real_data))
                        gameroom_collection[data.gameroom].strip_buffer()
                    if (action_id == "06" or action_id == "07"):
                        ball_room = gameroom_collection[data.gameroom]
                        ball_room.balldata = real_data
                        if (action_id == "07"):
                            if (data.id in ball_room.clients):
                                index = ball_room.clients.index(data.id)
                                index += 1
                                if (index == len(ball_room.clients)):
                                    index = 0
                            else:
                                index = 0
                            ball_room.win_message = "Player " + ball_room.id_to_name[ball_room.clients[index]] + " won the game!\n"
                    if (action_id == "08"):
                        ready_gameroom = gameroom_collection[data.gameroom]
                        if (data.id in ready_gameroom.tv_clients):
                            ready_gameroom.owner_updates = str(data.id) + "__server1337__" + "A tv instance joined into your room\033[32m - Ready\033[0m"
                        elif data.id in ready_gameroom.clients:
                            ready_gameroom.owner_updates = str(data.id) + "__server1337__" + data.name + " joined into your room\033[32m - Ready\033[0m"
                    if (not response == ""):
                        data.outb += response.encode("utf-8") + "__end1337__".encode("utf-8")

                decoded_data = data.inb.decode()
                decoded_data_list = decoded_data.split("__end1337__")

                if (len(decoded_data_list) > 1 ):
                    while (len(decoded_data_list)>1):
                        handle_a_message(decoded_data_list[0])
                        decoded_data_list.pop(0)
                    data.inb = bytes("__end1337__".join(decoded_data_list[0]).encode())
                else:
                    return
                
            else:
                raise ConnectionResetError  # Pakotetaan käsittelemään kuin virheellinen yhteys
        except ConnectionResetError:
            print(f"Connection reset by peer: {data.addr}")
            if (not data.gameroom == -1):
                theroom = gameroom_collection[data.gameroom]
                if (data.id in theroom.clients):
                    index = theroom.clients.index(data.id)
                    theroom.clients.remove(data.id)
                    if (theroom.nextclient >= index):
                        theroom.nextclient -= 1
                    if len(theroom.clients) == 0:
                        theroom.closed = True
                        if (len(theroom.tv_clients) == 0):
                            del gameroom_collection[data.gameroom]
                    if len(theroom.clients) == 1:
                        theroom.nextclient = 0
                elif (data.id in theroom.tv_clients):
                    theroom.tv_clients.remove(data.id)
                    if (len(theroom.tv_clients) == 0 and len(theroom.clients) == 0):
                        del gameroom_collection[data.gameroom]
            sel.unregister(sock)
            sock.close()
            return  # Lopetetaan käsittely suljetulle yhteydelle
        except Exception as e:
            tb = traceback.format_exc()
            print(f"Error handling connection {data.addr}: {e}\n{tb}")
            sel.unregister(sock)
            sock.close()
            return  # Suljetaan yhteys ja lopetetaan käsittely
    if mask & selectors.EVENT_WRITE:
        if (len(gameroom_collection)>0 and not data.gameroom == -1):
            current_gameroom = gameroom_collection[data.gameroom]
            gameroom_update = current_gameroom.getInfo(data.id)
            if (not gameroom_update == True):
                if (data.id in current_gameroom.tv_clients and not current_gameroom.closed == True):
                    if (data.secondary_id == current_gameroom.clients[current_gameroom.nextclient - 1] and not data.secondary_id == 0):
                        if (current_gameroom.settings["width"] >= 149 and current_gameroom.settings["height"] >= 10):
                            list_turn = yourturn_big.split("\n")
                            padding = (int((current_gameroom.settings["width"]-149)/2))
                            response_turn = int(((current_gameroom.settings["height"]-10)/2))*"\n"
                            for i in range (0,len(list_turn)):
                                 response_turn += " "*padding + list_turn[i] + "\n"
                        elif (current_gameroom.settings["width"] >= 78 and current_gameroom.settings["height"] >= 6):
                            list_turn = yourturn_small.split("\n")
                            padding = (int((current_gameroom.settings["width"]-78)/2))
                            response_turn = int(((current_gameroom.settings["height"]-6)/2))*"\n"
                            for i in range (0,len(list_turn)):
                                 response_turn += " "*padding + list_turn[i] + "\n"
                        else:
                            response_turn = "YOUR TURN"
                        data.outb += bytes("05" + json.dumps([[response_turn, 60]]) + "__end1337__", "utf-8")
                        return
                data.outb += bytes(str(gameroom_update) + "__end1337__", "utf-8")
        if data.outb:
            #print(f"sending {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

def accept_wrapper(sock):
    global id
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"", id=id, gameroom=-1, name="", secondary_id = 0)
    id+=1
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
