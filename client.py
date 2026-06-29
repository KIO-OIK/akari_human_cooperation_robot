#client.py
#ソケット通信でRaspberry Piからのじょうほうを受け取る

import socket
import time
import json

import datetime



def RasPiClient() -> None:

    #接続先のサーバ
    HOST = "172.31.14.22"
    PORT = 6000     #ポート番号（数字）


    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                while True:


                    json_data1 = s.recv(1024)
                    data1 = json.loads(json_data1.decode())
                    print("No0")
                    print(data1)

                    #json_data2 = s.recv(1024)
                    #data2 = json.loads(json_data2.decode())
                    #print("No1")
                    #print(data2)

                    
                    sensor = data1["data"]

                    print("No2")
                    print(sensor)


                    #members = data2["data"]

                    #print("No3")
                    #print(members)



                    tempC = sensor["tempC"]#温度
                    #hum = json_data["hum"]#湿度
                    soil = sensor["soil"]#土壌
                    #HIC = json_data["HIC"]#体感温度
                    #light = json_data["light"]#光
                    judgement = sensor["judgement"]#int型
                    #print("judgement:" + str(judgement))



                    timestamp = sensor["timestamp"]
                    dt = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")



                    print(dt)
                    #name = members["name"]
                    #status = members["status"]

                    if not json_data1:
                        print("サーバとの接続が切れました")
                        break

                    #print(json_data)

                    return judgement, soil, tempC , dt

        except (ConnectionRefusedError, ConnectionResetError, OSError):
            print("接続されません")
            time.sleep(1)


#soildata = RasPiClient()
#print(soildata)
#RasPiClient()


def AboutCooperation(name, accept, reject) -> None:

    senddata = None


     #接続先のサーバ
    HOST = "172.31.14.14"
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


def NotFind() -> None:

    #接続先のサーバ
    HOST = "172.31.14.7"
    PORT = 6000     #ポート番号（数字）


    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                while True:#この無限ループは意味がない


                    senddata = "not find people"

                    s.send(senddata.encode("utf-8"))#ソケット通信で送信できるのはbyte列のみなので、data.encode("utf-8")によって文字列をバイト列に変換



        except (ConnectionRefusedError, ConnectionResetError):
            print("接続されません")
            time.sleep(1)