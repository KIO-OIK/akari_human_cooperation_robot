#answer_yes.py

from gtts import gTTS 
import os

from akari_client import AkariClient
from akari_client.position import Positions
from akari_client.color import Colors, Color

import time

import threading

import face_tracking_auth

import client
import human_detection
import face_distance
# from client import scheduler
# from client import SensorClient
import arduino_send_akari

import main


#import main

setting_time = 15
soil_threshold = 700
tempC_threshold_min = 20
tempC_threshold_max = 32


class AnswerYes:

    def __init__(self,name,m5,joints,reject_name,judgement_soil,judgement_temp,judgement_suntime) -> None:
        self.name = name
        self.m5 = m5
        self.joints = joints
        self.reject_name = reject_name
        self.judgement_soil = judgement_soil
        self.judgement_temp = judgement_temp
        self.judgement_suntime = judgement_suntime
        # self.judgement = judgement
        # self.soil = soil
        # self.tempC = tempC
        # self.dt = dt
        # self.tempC_threshold_min = tempC_threshold_min
        # self.tempC_threshold_max = tempC_threshold_max
        # self.soil_threshold = soil_threshold
        # self.setting_time = setting_time

        # self.judgement, self.soil, self.tempC, self.dt= client.JudgementClient()
        #self.judgement_soil, self.judgement_temp, self.judgement_suntime = client.JudgementClient()#これじゃもう一回受け取らなきゃだめになっちゃう



    def request_water(self) -> None:



        text= self.name + "さん！植物の土がカラカラになっちゃった！水やりをお願いできないかな!"

        tts = gTTS(text, lang="ja", slow=False)

        #ファイルへ出力
        tts.save('yomiage_yes.mp3')


        #音声ファイルの読み込み
        os.system("mpg123 yomiage_yes.mp3")

        #soil_data = main.soil

        #print("soil_data:"+str(soil_data))


        countM5 = 0


        while True:

            data = self.m5.get()

            if countM5 == 0:

                self.m5.set_display_text("いいえ",pos_x=Positions.LEFT,pos_y=Positions.BOTTOM, refresh=True, size=4)
                self.m5.set_display_text("はい",pos_x=Positions.RIGHT,pos_y=Positions.BOTTOM, refresh=False, size=4)

            

            if data["button_a"] == True:

                face_tracking_auth.tracking_enabled = False

                self.m5.set_display_text("(T_T)",pos_x=Positions.CENTER,pos_y=Positions.CENTER, refresh=True, size=10)

                text="忙しいのにごめんね"

                tts = gTTS(text, lang="ja", slow=False)

                #ファイルへ出力
                tts.save('yomiage_yes.mp3')


                # サーボの速度を5rad/sに変更
                self.joints.set_joint_velocities(pan=5,tilt=5)

                self.joints.move_joint_positions(pan=0, tilt=-0.5)


                #音声ファイルの読み込み
                os.system("mpg123 yomiage_yes.mp3")



                client.AboutCooperation(self.name, 0, 1)

                face_tracking_auth.stop_face_tracking = True

                self.reject_name.append(self.name)

                client.AboutKachaka(1)



                #time.sleep(2)

                self.joints.set_joint_velocities(pan=10,tilt=10)


                time.sleep(20)

                human_detection.detect_human(self.m5,self.joints,self.reject_name,self.judgement_soil,self.judgement_temp,self.judgement_suntime)#人検知機能

                print("def request_water(self)完了、returnします。")

                return
                #face_distance.face_distance()#人の距離検知

                #face_tracking_auth.tracking_enabled = True


            if data["button_c"] == True:


                face_tracking_auth.tracking_enabled = False

                self.m5.set_display_text("(^_^)",pos_x=Positions.CENTER,pos_y=Positions.CENTER, refresh=True, size=10)

                #time.sleep(5)

                text="ありがとう！植物も喜んでるよ！今から植物を近くに持ってくるね！"

                tts = gTTS(text, lang="ja", slow=False)

                #ファイルへ出力
                tts.save('yomiage_yes.mp3')

                # サーボの速度を5rad/sに変更
                self.joints.set_joint_velocities(pan=10,tilt=10)

                self.joints.move_joint_positions(pan=0, tilt=0.1)
                time.sleep(0.3)

                self.joints.move_joint_positions(pan=0, tilt=-0.5)
                time.sleep(0.3)

                self.joints.move_joint_positions(pan=0, tilt=0.1)
                time.sleep(0.3)

                self.joints.move_joint_positions(pan=0, tilt=-0.5)
                time.sleep(0.3)

                self.joints.move_joint_positions(pan=0, tilt=0.1)
                time.sleep(0.3)

                #time.sleep(5)

                #音声ファイルの読み込み
                os.system("mpg123 yomiage_yes.mp3")


                face_tracking_auth.tracking_enabled = True

                client.PlantKachaka(1)#植物を近くに運ぶ

                PlantArrive = client.PlantArrive(1)

                text="かちゃかが運んできたら、シェルフにあるじょうろの１目盛分のお水を上げてほしいな！"


                tts = gTTS(text, lang="ja", slow=False)

                #ファイルへ出力
                tts.save('yomiage_yes.mp3')

                        #音声ファイルの読み込み
                os.system("mpg123 yomiage_yes.mp3")

                time.sleep(60)

                while True:
                    latest_temp_c, latest_soil1, latest_soil2, latest_soil3, latest_light = arduino_send_akari.main()

                    if latest_soil1 < 409 and latest_soil2 < 409 and latest_soil3 < 429:
                        self.m5.set_display_text("(^_^)",pos_x=Positions.CENTER,pos_y=Positions.CENTER, refresh=True, size=10)

                        text="お水が満たされたよ。協力してくれてありがとう"

                        tts = gTTS(text, lang="ja", slow=False)

                        #ファイルへ出力
                        tts.save('yomiage_yes.mp3')

                                #音声ファイルの読み込み
                        os.system("mpg123 yomiage_yes.mp3")

                        self.judgement_soil = 0

                        break

                    text="もう１目盛分のお水をあげてほしいな。"

                    tts = gTTS(text, lang="ja", slow=False)

                    #ファイルへ出力
                    tts.save('yomiage_yes.mp3')

                            #音声ファイルの読み込み
                    os.system("mpg123 yomiage_yes.mp3")



                # client.AboutKachaka(2)

                # print("kachaka back 実行しました。")

                client.AboutCooperation(self.name, 1, 0)

                #time.sleep(2)

                break

            
            countM5 += 1

            time.sleep(3)

            

        countM5 = 0


    def request_sun(self) -> None:


        text= self.name + "さん！植物が光合成する時間になったんだ！植物を日当たりのいい場所に運んでくれないかな！"

        tts = gTTS(text, lang="ja", slow=False)

        #ファイルへ出力
        tts.save('yomiage_yes.mp3')


        #音声ファイルの読み込み
        os.system("mpg123 yomiage_yes.mp3")


        countM5 = 0


        while True:

            data = self.m5.get()

            if countM5 == 0:

                self.m5.set_display_text("いいえ",pos_x=Positions.LEFT,pos_y=Positions.BOTTOM, refresh=True, size=4)
                self.m5.set_display_text("はい",pos_x=Positions.RIGHT,pos_y=Positions.BOTTOM, refresh=False, size=4)

            

            if data["button_a"] == True:

                face_tracking_auth.tracking_enabled = False

                self.m5.set_display_text("(T_T)",pos_x=Positions.CENTER,pos_y=Positions.CENTER, refresh=True, size=10)

                text="忙しいのにごめんねー？"

                tts = gTTS(text, lang="ja", slow=False)

                #ファイルへ出力
                tts.save('yomiage_yes.mp3')


                # サーボの速度を5rad/sに変更
                self.joints.set_joint_velocities(pan=5,tilt=5)

                self.joints.move_joint_positions(pan=0, tilt=-0.5)


                #音声ファイルの読み込み
                os.system("mpg123 yomiage_yes.mp3")

                client.AboutCooperation(self.name, 0, 1)

                self.reject_name.append(self.name)

                face_tracking_auth.stop_face_tracking = True

                client.AboutKachaka(1)

                #time.sleep(2)


                self.joints.set_joint_velocities(pan=10,tilt=10)


                time.sleep(20)

                human_detection.detect_human(self.m5,self.joints,self.reject_name,self.judgement_soil,self.judgement_temp,self.judgement_suntime)#人検知機能

                print("def request_sun(self)完了、returnします。")

                return

                #face_tracking_auth.tracking_enabled = True

                break


            if data["button_c"] == True:

                face_tracking_auth.tracking_enabled = False

                self.m5.set_display_text("(^_^)",pos_x=Positions.CENTER,pos_y=Positions.CENTER, refresh=True, size=10)

                text="ありがとう！植物も喜んでるよ！"

                tts = gTTS(text, lang="ja", slow=False)

                #ファイルへ出力
                tts.save('yomiage_yes.mp3')

                # サーボの速度を5rad/sに変更
                self.joints.set_joint_velocities(pan=10,tilt=10)

                self.joints.move_joint_positions(pan=0, tilt=0.1)
                time.sleep(0.3)

                self.joints.move_joint_positions(pan=0, tilt=-0.5)
                time.sleep(0.3)

                self.joints.move_joint_positions(pan=0, tilt=0.1)
                time.sleep(0.3)

                self.joints.move_joint_positions(pan=0, tilt=-0.5)
                time.sleep(0.3)

                self.joints.move_joint_positions(pan=0, tilt=0.1)
                time.sleep(0.3)

                #time.sleep(5)

                #face_tracking_auth.tracking_enabled = True

                #time.sleep(2)

                #音声ファイルの読み込み
                os.system("mpg123 yomiage_yes.mp3")

                face_tracking_auth.tracking_enabled = True

                client.PlantKachaka(1)#植物を近くに運ぶ

                text="今からかちゃかが植物を運んでくるね。"


                tts = gTTS(text, lang="ja", slow=False)

                #ファイルへ出力
                tts.save('yomiage_yes.mp3')

                        #音声ファイルの読み込み
                os.system("mpg123 yomiage_yes.mp3")

                latest_temp_c, latest_soil1, latest_soil2, latest_soil3, latest_light = arduino_send_akari.main()

                old_light = latest_light

                PlantArrive = client.PlantArrive(1)

                text = "植物がついたら、植木鉢についているライトのコードを繋いでから電源をいれて、タイマーを３時間設定にしてくれるかな。時計マークのボタンを３回押して、スイッチがオレンジに点灯したら大丈夫だよ。"

                tts = gTTS(text, lang="ja", slow=False)

                #ファイルへ出力
                tts.save('yomiage_yes.mp3')

                        #音声ファイルの読み込み
                os.system("mpg123 yomiage_yes.mp3")

                time.sleep(60)

                while True:
                    latest_temp_c, latest_soil1, latest_soil2, latest_soil3, latest_light = arduino_send_akari.main()

                    light_difference = latest_light - old_light

                    if light_difference > 10:
                        self.m5.set_display_text("(^_^)",pos_x=Positions.CENTER,pos_y=Positions.CENTER, refresh=True, size=10)

                        text="ライトが起動したよ。協力してくれてありがとう。"

                        tts = gTTS(text, lang="ja", slow=False)

                        #ファイルへ出力
                        tts.save('yomiage_yes.mp3')

                                #音声ファイルの読み込み
                        os.system("mpg123 yomiage_yes.mp3")

                        self.judgement_suntime = 0

                        break

                time.sleep(2)

                break

            
            countM5 += 1

            time.sleep(3)

            

        countM5 = 0





    
    def request_temp(self) -> None:

        if self.judgement_temp == 1:
            text= self.name + "さん！植物が寒そうにしてるよ！部屋の温度をあげてほしいな！"

        if self.judgement_temp == 2:
            text= self.name + "さん！植物が暑そうにしてるよ！部屋の温度をあげてほしいな！"


        #text= self.name + "さん！"

        tts = gTTS(text, lang="ja", slow=False)

        #ファイルへ出力
        tts.save('yomiage_yes.mp3')


        #音声ファイルの読み込み
        os.system("mpg123 yomiage_yes.mp3")


        countM5 = 0


        while True:

            data = self.m5.get()

            if countM5 == 0:

                self.m5.set_display_text("いいえ",pos_x=Positions.LEFT,pos_y=Positions.BOTTOM, refresh=True, size=4)
                self.m5.set_display_text("はい",pos_x=Positions.RIGHT,pos_y=Positions.BOTTOM, refresh=False, size=4)

            

            if data["button_a"] == True:

                face_tracking_auth.tracking_enabled = False

                self.m5.set_display_text("(T_T)",pos_x=Positions.CENTER,pos_y=Positions.CENTER, refresh=True, size=10)

                text="忙しいのにごめんねー？"

                tts = gTTS(text, lang="ja", slow=False)

                #ファイルへ出力
                tts.save('yomiage_yes.mp3')


                # サーボの速度を5rad/sに変更
                self.joints.set_joint_velocities(pan=5,tilt=5)

                self.joints.move_joint_positions(pan=0, tilt=-0.5)


                #音声ファイルの読み込み
                os.system("mpg123 yomiage_yes.mp3")

                # threadCoop = threading.Thread(target=client.AboutCooperation, args=(self.name, 0, 1,))
                # threadCoop.start()

                client.AboutCooperation(self.name, 0, 1)

                self.reject_name.append(self.name)

                face_tracking_auth.stop_face_tracking = True

                client.AboutKachaka(1)

                self.joints.set_joint_velocities(pan=10,tilt=10)

                time.sleep(20)

                human_detection.detect_human(self.m5,self.joints,self.reject_name,self.judgement_soil,self.judgement_temp,self.judgement_suntime)#人検知機能

                print("def request_temp(self)完了、returnします。")

                return
                #face_tracking_auth.tracking_enabled = True

                break


            if data["button_c"] == True:

                face_tracking_auth.tracking_enabled = False

                self.m5.set_display_text("(^_^)",pos_x=Positions.CENTER,pos_y=Positions.CENTER, refresh=True, size=10)

                text="ありがとう！植物も喜んでるよ！"

                tts = gTTS(text, lang="ja", slow=False)

                #ファイルへ出力
                tts.save('yomiage_yes.mp3')
                
                # サーボの速度を5rad/sに変更
                self.joints.set_joint_velocities(pan=10,tilt=10)

                self.joints.move_joint_positions(pan=0, tilt=0.1)
                time.sleep(0.3)

                self.joints.move_joint_positions(pan=0, tilt=-0.5)
                time.sleep(0.3)

                self.joints.move_joint_positions(pan=0, tilt=0.1)
                time.sleep(0.3)

                self.joints.move_joint_positions(pan=0, tilt=-0.5)
                time.sleep(0.3)

                self.joints.move_joint_positions(pan=0, tilt=0.1)
                time.sleep(0.3)

                #time.sleep(5)

                

                #time.sleep(2)
                #音声ファイルの読み込み
                os.system("mpg123 yomiage_yes.mp3")

                face_tracking_auth.tracking_enabled = True







                # client.PlantKachaka(1)#植物を近くに運ぶ

                # time.sleep(120)

                # text="かちゃかが運んできたこの植物にお水をおねがい！"


                # tts = gTTS(text, lang="ja", slow=False)

                # #ファイルへ出力
                # tts.save('yomiage_yes.mp3')

                #         #音声ファイルの読み込み
                # os.system("mpg123 yomiage_yes.mp3")

                # time.sleep(60)

                if self.judgement_temp == 1:#寒いとき

                    old_temp_c = 0
                    temp_raise = 0

                    #while True:

                    latest_temp_c, latest_soil1, latest_soil2, latest_soil3, latest_light = arduino_send_akari.main()

                    old_temp_c = latest_temp_c

                    time.sleep(300)

                    while True:
                        latest_temp_c, latest_soil1, latest_soil2, latest_soil3, latest_light = arduino_send_akari.main()

                        if latest_temp_c - old_temp_c > 0:

                            self.m5.set_display_text("(^_^)",pos_x=Positions.CENTER,pos_y=Positions.CENTER, refresh=True, size=10)

                            text="部屋が暖かくなったよ。協力してくれてありがとう"

                            tts = gTTS(text, lang="ja", slow=False)

                            #ファイルへ出力
                            tts.save('yomiage_yes.mp3')

                                    #音声ファイルの読み込み
                            os.system("mpg123 yomiage_yes.mp3")

                            self.judgement_temp = 0

                            break

                        text="もう少し温度を上げてほしいな"

                        tts = gTTS(text, lang="ja", slow=False)

                        #ファイルへ出力
                        tts.save('yomiage_yes.mp3')

                                #音声ファイルの読み込み
                        os.system("mpg123 yomiage_yes.mp3")

                    client.AboutCooperation(self.name, 1, 0)

                    time.sleep(2)

                    break



                if self.judgement_temp == 2:#暑いとき

                    old_temp_c = 0
                    temp_raise = 0

                    #while True:

                    latest_temp_c, latest_soil1, latest_soil2, latest_soil3, latest_light = arduino_send_akari.main()

                    old_temp_c = latest_temp_c

                    time.sleep(300)

                    while True:
                        latest_temp_c, latest_soil1, latest_soil2, latest_soil3, latest_light = arduino_send_akari.main()

                        if latest_temp_c - old_temp_c < 0:

                            self.m5.set_display_text("(^_^)",pos_x=Positions.CENTER,pos_y=Positions.CENTER, refresh=True, size=10)

                            text="部屋が涼しくなったよ。協力してくれてありがとう"

                            tts = gTTS(text, lang="ja", slow=False)

                            #ファイルへ出力
                            tts.save('yomiage_yes.mp3')

                                    #音声ファイルの読み込み
                            os.system("mpg123 yomiage_yes.mp3")

                            self.judgement_temp = 0

                            break

                        text="もう少し温度を下げてほしいな"

                        tts = gTTS(text, lang="ja", slow=False)

                        #ファイルへ出力
                        tts.save('yomiage_yes.mp3')

                                #音声ファイルの読み込み
                        os.system("mpg123 yomiage_yes.mp3")

                    client.AboutCooperation(self.name, 1, 0)

                    time.sleep(2)

                    break

            
            countM5 += 1

            time.sleep(3)

            

        countM5 = 0





    

    def which_request(self) -> None:



        #judgement_soil, judgement_temp, judgement_suntime = client.JudgementClient()

        # print("judgement:"+ str(self.judgement))
        # print("soil:" + str(self.soil))
        # print("tempC:"+str(self.tempC))
        # print("dt:"+str(self.dt))

        # hour = self.dt.hour
        first_soil_data = self.judgement_soil
        first_suntime_data = self.judgement_suntime

        while True:

            if self.name in self.reject_name:
                return

            elif self.judgement_soil == 1:

                self.request_water()

            elif self.judgement_suntime == 1:#時間になったら(サーバー側から時間としきい値を取得)

                self.request_sun()

            elif self.judgement_temp == 1 or self.judgement_temp == 2:

                self.request_temp()

                
            else:
                break



        face_tracking_auth.stop_face_tracking = True


        self.m5.set_display_text("(^_^)",pos_x=Positions.CENTER,pos_y=Positions.CENTER, refresh=True, size=10)

        print("------------------------------------")

        print("Akari:「必要なお世話が全部できたよ！助けてくれてありがとう！元気に育つと嬉しいな！」")
        print("------------------------------------")

        text="必要なお世話が全部できたよ！助けてくれてありがとう！元気に育つと嬉しいな！"

        tts = gTTS(text, lang="ja", slow=False)

        #ファイルへ出力
        tts.save('yomiage_yes.mp3')

                        # サーボの速度を5rad/sに変更
        self.joints.set_joint_velocities(pan=10,tilt=10)

        self.joints.move_joint_positions(pan=0, tilt=0.1)
        time.sleep(0.3)

        self.joints.move_joint_positions(pan=0, tilt=-0.5)
        time.sleep(0.3)

        self.joints.move_joint_positions(pan=0, tilt=0.1)
        time.sleep(0.3)

        self.joints.move_joint_positions(pan=0, tilt=-0.5)
        time.sleep(0.3)

        self.joints.move_joint_positions(pan=0, tilt=0.1)
        time.sleep(0.3)

        os.system("mpg123 yomiage_yes.mp3")
        print("リクエスト完了")
        print("first_soil_data:",first_soil_data)
        print("first_suntime_data:",first_suntime_data)

        if first_soil_data == 1 or first_suntime_data == 1:

            client.PlantKachaka(2)#植物をもとに戻す

            PlantBackOK = client.ReDocking(1)

        else:

            PlantBackOK = "redocking"

        print("PlantBackOK:", PlantBackOK)

        if PlantBackOK == "redocking":
            print("kachaka back 実行します。")
            time.sleep(3)

            client.AboutKachaka(2)

        # main.main()

        return





