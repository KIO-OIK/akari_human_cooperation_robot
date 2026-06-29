#answer_yes.py

from gtts import gTTS 
import os

from akari_client import AkariClient
from akari_client.position import Positions
from akari_client.color import Colors, Color

import time


import face_tracking_auth

#import main


class AnswerYes:

    def __init__(self,name,m5,joints,judgement, soil, tempC, dt, tempC_threshold_min, tempC_threshold_max) -> None:
        self.name = name
        self.m5 = m5
        self.joints = joints
        self.judgement = judgement
        self.soil = soil
        self.tempC = tempC
        self.dt = dt
        self.tempC_threshold_min = tempC_threshold_min
        self.tempC_threshold_max = tempC_threshold_max



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

                text="忙しいのにごめんねー？"

                tts = gTTS(text, lang="ja", slow=False)

                #ファイルへ出力
                tts.save('yomiage_yes.mp3')


                # サーボの速度を5rad/sに変更
                self.joints.set_joint_velocities(pan=5,tilt=5)

                self.joints.move_joint_positions(pan=0, tilt=-0.5)


                #音声ファイルの読み込み
                os.system("mpg123 yomiage_yes.mp3")

                time.sleep(2)

                self.joints.set_joint_velocities(pan=10,tilt=10)


                time.sleep(20)

                face_tracking_auth.tracking_enabled = True

                break


            if data["button_c"] == True:


                face_tracking_auth.tracking_enabled = False

                self.m5.set_display_text("(^_^)",pos_x=Positions.CENTER,pos_y=Positions.CENTER, refresh=True, size=10)

                #time.sleep(5)

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

                 #音声ファイルの読み込み
                os.system("mpg123 yomiage_yes.mp3")

                face_tracking_auth.tracking_enabled = True

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

                #time.sleep(2)


                self.joints.set_joint_velocities(pan=10,tilt=10)

                time.sleep(20)


                face_tracking_auth.tracking_enabled = True

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

                time.sleep(2)

                break

            
            countM5 += 1

            time.sleep(3)

            

        countM5 = 0





    
    def request_temp(self) -> None:

        if self.tempC < tempC_threshold_min:
            text= self.name + "さん！植物が寒そうにしてるよ！部屋の温度をあげてほしいな！"

        if self.tempC > tempC_threshold_max:
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

                time.sleep(20)

                self.joints.set_joint_velocities(pan=10,tilt=10)


                face_tracking_auth.tracking_enabled = True

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

                time.sleep(2)

                break

            
            countM5 += 1

            time.sleep(3)

            

        countM5 = 0





    

    #def which_request(self) -> None:

        #while True:

            #if self.soil > しきい値:

                #self.request_water()

            #if 時間になったら(サーバー側から時間としきい値を取得)

                #self.request_sun()

            #if tempC > 最高温度 or 最低温度しきい値 > self.tempC

                #self.request_temp()

                
            #else break





