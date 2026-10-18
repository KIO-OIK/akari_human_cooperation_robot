#client.py
#ソケット通信でRaspberry Piからのじょうほうを受け取る

import socket
import time
import json

from datetime import datetime

HOST_NUMBER = "172.31.14.16"

arduino_ip = None


def JudgementClient():

    #接続先のサーバ
    HOST = HOST_NUMBER
    PORT = 7001     #ポート番号（数字）


    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                while True:

                    print("------------------------------------")

                    print("サーバーから指示が来るのを待っています。")


                    json_data = s.recv(1024)
                    data = json.loads(json_data.decode())#decodeでbyteからstrに、loadsで辞書型に
                    print("No0")
                    print(data)#{"judgement_data":{judgement_soil:00, "judgement_temp:00, judgement_suntime:00"}}

                    #json_data2 = s.recv(1024)
                    #data2 = json.loads(json_data2.decode())
                    #print("No1")
                    #print(data2)

                    judgement_soil = 0
                    judgement_temp = 0
                    judgement_suntime = 0



                    # 指示待ちです。
                    # No0
                    # {'time_judgement': 1}
                    # judgement_soil: 0
                    # judgement_temp: 0
                    # judgement_suntime: 1
                    # [18443010117C031300] [1.5] [1.003] [system] [warning] ColorCamera IMX214: capping FPS for selected resolution to 35
                    # stop_event: True

                    
                    #judgement_data = data["data"]#""はサーバーに合わせる
                    #print("No2")
                    #print(judgement_data)

                    if "time_judgement" in data:
                        judgement_suntime = data["time_judgement"]

                    if "soil_judgement" in data:
                        judgement_soil = data["soil_judgement"]

                    if "tempC_judgement" in data:
                        judgement_temp = data["tempC_judgement"]
                    



                    # tempC = sensor["tempC"]#温度
                    #hum = json_data["hum"]#湿度
                    # soil = sensor["soil"]#土壌
                    #HIC = json_data["HIC"]#体感温度
                    #light = json_data["light"]#光
                    # judgement = sensor["judgement"]#int型
                    #print("judgement:" + str(judgement))



                    # timestamp = sensor["timestamp"]
                    # dt = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")



                    #print(dt)
                    #name = members["name"]
                    #status = members["status"]

                    if not json_data:
                        print("サーバとの接続が切れました")
                        break

                    #print(json_data)

                    return judgement_soil,judgement_temp,judgement_suntime

        except (ConnectionRefusedError, ConnectionResetError, OSError):
            print("作動指示待機中")
            time.sleep(1)






def AboutCooperation(name, accept, reject) -> None:

    senddata = None


     #接続先のサーバ
    HOST = HOST_NUMBER
    PORT = 4001     #ポート番号（数字）


    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                #while True:#この無限ループは意味がない


                if accept == 1:

                    senddata = name + " accept"

                    s.send(senddata.encode("utf-8"))#ソケット通信で送信できるのはbyte列のみなので、data.encode("utf-8")によって文字列をバイト列に変換

                    return 

                if reject == 1:

                    senddata = name + " reject"

                    s.send(senddata.encode("utf-8"))#ソケット通信で送信できるのはbyte列のみなので、data.encode("utf-8")によって文字列をバイト列に変換

                    return







        except (ConnectionRefusedError, ConnectionResetError):
            print("接続されません")
            time.sleep(1)



def NotFind():

    HOST = HOST_NUMBER
    PORT = 5002

    while True:

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))

                json_data = s.recv(1024)

                # 接続が切れた場合は終了
                if not json_data:
                    print("5002番ポートとの接続が切れました")
                    return None

                data = json_data.decode()

                if data != "":
                    return data

                return None

        except (
            ConnectionRefusedError,
            ConnectionResetError
        ):
            print("一周完了通知に接続されません")
            time.sleep(1)


# def NotFind():

#     #接続先のサーバ
#     HOST = HOST_NUMBER
#     PORT = 5002     #ポート番号（数字）


#     while True:
#         try:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.connect((HOST, PORT))

#                 json_data = s.recv(1024)
#                 data = json_data.decode()

#                 if data != "":
#                     print("一周したことを教えるデータ「" + data + "」")


#                     return data


def AboutKachaka(go):

    #接続先のサーバ
    HOST = HOST_NUMBER
    PORT = 8001     #ポート番号（数字）

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))


                    #break



                if go == 2:

                    senddata = "kachaka back"

                    s.send(senddata.encode("utf-8"))#ソケット通信で送信できるのはbyte列のみなので、data.encode("utf-8")によって文字列をバイト列に変換
                    
                    break


                if go == 1:

                    senddata = "kachaka go"

                    s.send(senddata.encode("utf-8"))#ソケット通信で送信できるのはbyte列のみなので、data.encode("utf-8")によって文字列をバイト列に変換
                    
                    break


                if go == 0:

                    senddata = "kachaka stop"

                    s.send(senddata.encode("utf-8"))#ソケット通信で送信できるのはbyte列のみなので、data.encode("utf-8")によって文字列をバイト列に変換

                    break

        except (ConnectionRefusedError, ConnectionResetError):
            print("kachaka指示ポートに接続されません")
            time.sleep(1)




def PlantKachaka(go) -> None:

    #接続先のサーバ
    HOST = HOST_NUMBER
    PORT = 4002     #ポート番号（数字）

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))

                # if go == 3:

                #     receive_data = s.recv(1024)
                #     data = receive_data.decode()

                #     print(data)

                #     return data



                if go == 2:

                    senddata = "back plant"

                    s.send(senddata.encode("utf-8"))#ソケット通信で送信できるのはbyte列のみなので、data.encode("utf-8")によって文字列をバイト列に変換
                    
                    break


                if go == 1:

                    senddata = "come plant"

                    s.send(senddata.encode("utf-8"))#ソケット通信で送信できるのはbyte列のみなので、data.encode("utf-8")によって文字列をバイト列に変換
                    
                    break


                if go == 0:

                    senddata = "stop plant"

                    s.send(senddata.encode("utf-8"))#ソケット通信で送信できるのはbyte列のみなので、data.encode("utf-8")によって文字列をバイト列に変換

                    break

        except (ConnectionRefusedError, ConnectionResetError):
            print("植物kachaka指示ポートに接続されません")
            time.sleep(1)



def ReDocking(receive):

    HOST = HOST_NUMBER
    PORT = 4003

    while True:

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))

                if receive == 1:

                    json_data = s.recv(1024)

                    # 接続が切れた場合は終了
                    if not json_data:
                        print("4003番ポートとの接続が切れました")
                        time.sleep(1)

                    data = json_data.decode().strip()

                    print("data:"+ data)

                    return data

        except (
            ConnectionRefusedError,
            ConnectionResetError
        ):
            print("AKARIシェルフドッキングポートに接続されません")
            time.sleep(1)




def PlantArrive(receive):

    HOST = HOST_NUMBER
    PORT = 4004

    while True:

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))

                if receive == 1:

                    json_data = s.recv(1024)

                    # 接続が切れた場合は終了
                    if not json_data:
                        print("4004番ポートとの接続が切れました")
                        time.sleep(1)

                    data = json_data.decode().strip()

                    print("data:"+ data)

                    return data

        except (
            ConnectionRefusedError,
            ConnectionResetError
        ):
            print("植物到着ポートに接続されません")
            time.sleep(1)