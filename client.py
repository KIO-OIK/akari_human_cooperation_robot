#client.py
#ソケット通信でRaspberry Piからのじょうほうを受け取る

import socket
import time
import json

from datetime import datetime

HOST_NUMBER = "172.31.14.11"

arduino_ip = None

# def IndicationClient():#指示待ち状態から動かすための情報取得

#     #接続先のサーバ
#     HOST = HOST_NUMBER
#     PORT = 7001     #ポート番号（数字）


#     while True:
#         try:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.connect((HOST, PORT))
#                 while True:


#                     json_data = s.recv(1024)
#                     data = json.loads(json_data.decode())
#                     print("No0")
#                     print(data)

#                     #json_data2 = s.recv(1024)
#                     #data2 = json.loads(json_data2.decode())
#                     #print("No1")
#                     #print(data2)

                    
#                     # sensor = data["data"]

#                     # print("No2")
#                     # print(sensor)


#                     #members = data2["data"]

#                     #print("No3")
#                     #print(members)



#                     #tempC = sensor["tempC"]#温度
#                     #hum = json_data["hum"]#湿度
#                     #soil = sensor["soil"]#土壌
#                     #HIC = json_data["HIC"]#体感温度
#                     #light = json_data["light"]#光
#                     #judgement = sensor["judgement"]#int型
#                     #print("judgement:" + str(judgement))



#                     #timestamp = sensor["timestamp"]
#                     #dt = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")



#                     #print(dt)
#                     #name = members["name"]
#                     #status = members["status"]

#                     if not json_data:
#                         print("サーバとの接続が切れました")
#                         break

#                     #print(json_data)

#                     return data

#         except (ConnectionRefusedError, ConnectionResetError, OSError):
#             print("接続されません")
#             time.sleep(1)


def JudgementClient():

    #接続先のサーバ
    HOST = HOST_NUMBER
    PORT = 7001     #ポート番号（数字）


    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                while True:

                    print("指示待ちです。")


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


#soildata = RasPiClient()
#print(soildata)
#RasPiClient()






# def SensorClient():

#     #接続先のサーバ
#     HOST = HOST_NUMBER
#     PORT = 7000     #ポート番号（数字）


#     while True:
#         try:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.connect((HOST, PORT))
#                 conn, addr = s.accept()
#                 while True:


#                     json_data1 = s.recv(1024)
#                     data = json_data1.decode()

#                     if data == "HELLO":
#                         global arduino_ip

#                         arduino_ip = addr[0]

#                         print("Arduino登録:", arduino_ip)

#                         return data

#                     data1 = json.loads(data)
#                     print("No0")
#                     print(data1)

#                     #json_data2 = s.recv(1024)
#                     #data2 = json.loads(json_data2.decode())
#                     #print("No1")
#                     #print(data2)

                    
#                     sensor = data1["data"]

#                     print("No2")
#                     print(sensor)


#                     #members = data2["data"]

#                     #print("No3")
#                     #print(members)



#                     #tempC = sensor["tempC"]#温度
#                     #hum = json_data["hum"]#湿度
#                     soil = sensor["soil"]#土壌
#                     #HIC = json_data["HIC"]#体感温度
#                     #light = json_data["light"]#光
#                     #judgement = sensor["judgement"]#int型
#                     #print("judgement:" + str(judgement))



#                     #timestamp = sensor["timestamp"]
#                     #dt = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")



#                     print(dt)
#                     #name = members["name"]
#                     #status = members["status"]

#                     if not json_data1:
#                         print("サーバとの接続が切れました")
#                         break

#                     #print(json_data)

#                     return soil

#         except (ConnectionRefusedError, ConnectionResetError, OSError):
#             print("接続されません")
#             time.sleep(1)






def AboutCooperation(name, accept, reject) -> None:

    senddata = None


     #接続先のサーバ
    HOST = HOST_NUMBER
    PORT = 6000     #ポート番号（数字）


    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                while True:#この無限ループは意味がない


                    if accept == 1:

                        senddata = name + " is accept"

                        s.send(senddata.encode("utf-8"))#ソケット通信で送信できるのはbyte列のみなので、data.encode("utf-8")によって文字列をバイト列に変換

                    if reject == 1:

                        senddata = name + " is reject"

                        s.send(senddata.encode("utf-8"))#ソケット通信で送信できるのはbyte列のみなので、data.encode("utf-8")によって文字列をバイト列に変換







        except (ConnectionRefusedError, ConnectionResetError):
            print("接続されません")
            time.sleep(1)


def NotFind():

    #接続先のサーバ
    HOST = HOST_NUMBER
    PORT = 5002     #ポート番号（数字）


    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))

                json_data = s.recv(1024)
                data = json_data.decode()

                print("sent_data:",data)

                return data

                
                #while True:#この無限ループは意味がない


                    # senddata = "not find people"

                    # s.send(senddata.encode("utf-8"))#ソケット通信で送信できるのはbyte列のみなので、data.encode("utf-8")によって文字列をバイト列に変換



        except (ConnectionRefusedError, ConnectionResetError):
            print("接続されません")
            time.sleep(1)


def AboutKachaka(go) -> None:

    #接続先のサーバ
    HOST = HOST_NUMBER
    PORT = 8001     #ポート番号（数字）

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))


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
            print("接続されません")
            time.sleep(1)





