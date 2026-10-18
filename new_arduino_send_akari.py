import json
import socket
import threading
import time
from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

from akari_client import AkariClient
from akari_client.position import Positions
from akari_client.color import Colors


# =====================================
# 通信設定
# =====================================
HOST = "0.0.0.0"
PORT = 6001

BUFFER_SIZE = 4096
ENCODING = "utf-8"

BUTTON_CHECK_INTERVAL = 0.1

JST = ZoneInfo("Asia/Tokyo")


# =====================================
# Arduino接続管理
# =====================================
arduino_socket: Optional[socket.socket] = None
arduino_address = None

arduino_lock = threading.Lock()

stop_event = threading.Event()


# =====================================
# M5Stack管理
# =====================================
m5_instance = None
m5_lock = threading.Lock()


# =====================================
# ボタン処理状態
# =====================================
request_in_progress = False
request_lock = threading.Lock()


# =====================================
# 現在時刻
# =====================================
def current_time() -> str:
    return datetime.now(JST).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# =====================================
# M5Stackへ表示
# =====================================
def show_m5_message(
    text: str,
    text_color=Colors.WHITE,
    back_color=Colors.BLACK,
    size: int = 4
) -> None:
    global m5_instance

    with m5_lock:
        if m5_instance is None:
            return

        try:
            m5_instance.set_display_text(
                text=text,
                pos_x=Positions.CENTER,
                pos_y=Positions.CENTER,
                size=size,
                text_color=text_color,
                back_color=back_color,
                refresh=True,
                sync=True
            )

        except Exception as error:
            print(
                f"[{current_time()}] "
                f"M5Stack表示エラー: {error}"
            )


# =====================================
# Arduino接続確認
# =====================================
def is_arduino_connected() -> bool:
    with arduino_lock:
        return arduino_socket is not None


# =====================================
# Arduino登録
# =====================================
def register_arduino(
    client_socket: socket.socket,
    client_address
) -> None:
    global arduino_socket
    global arduino_address

    with arduino_lock:
        if (
            arduino_socket is not None
            and arduino_socket is not client_socket
        ):
            try:
                arduino_socket.close()
            except OSError:
                pass

        arduino_socket = client_socket
        arduino_address = client_address

    print()
    print("====================================")
    print(f"[{current_time()}] Arduino接続")
    print(
        f"接続元: "
        f"{client_address[0]}:{client_address[1]}"
    )
    print("====================================")

    show_m5_message(
        text=(
            "Arduino Connected\n"
            "Press Button A"
        ),
        text_color=Colors.WHITE,
        back_color=Colors.GREEN,
        size=4
    )


# =====================================
# Arduino登録解除
# =====================================
def unregister_arduino(
    client_socket: socket.socket
) -> None:
    global arduino_socket
    global arduino_address

    with arduino_lock:
        if arduino_socket is client_socket:
            arduino_socket = None
            arduino_address = None

    print(
        f"[{current_time()}] "
        "Arduinoが切断されました"
    )

    show_m5_message(
        text=(
            "Arduino\n"
            "Disconnected"
        ),
        text_color=Colors.WHITE,
        back_color=Colors.RED,
        size=5
    )


# =====================================
# Arduinoへ命令送信
# =====================================
def send_command_to_arduino(
    command: str
) -> bool:
    global arduino_socket
    global arduino_address

    with arduino_lock:
        if arduino_socket is None:
            print(
                f"[{current_time()}] "
                "Arduinoが接続されていません"
            )

            return False

        try:
            message = command.strip() + "\n"

            arduino_socket.sendall(
                message.encode(ENCODING)
            )

            print(
                f"[{current_time()}] "
                f"Arduinoへ送信: {command}"
            )

            return True

        except OSError as error:
            print(
                f"[{current_time()}] "
                f"Arduinoへの送信エラー: {error}"
            )

            try:
                arduino_socket.close()
            except OSError:
                pass

            arduino_socket = None
            arduino_address = None

            return False


# =====================================
# センサー値の状態文字列
# =====================================
# def temperature_status(
#     judgement: int
# ) -> str:
#     if judgement == 1:
#         return "HIGH"

#     return "OK"


# def soil_status(
#     judgement: int
# ) -> str:
#     if judgement == 1:
#         return "DRY"

#     return "OK"


# =====================================
# センサーデータをコマンドライン表示
# =====================================
def print_sensor_data(
    sensor_data: dict[str, Any]
) -> None:
    temp_c = sensor_data.get("tempC")
    #temp_f = sensor_data.get("tempF")
    #humidity = sensor_data.get("hum")
    #heat_index_c = sensor_data.get("HIC")
    #heat_index_f = sensor_data.get("HIF")
    soil = sensor_data.get("soil")
    #light = sensor_data.get("light")

    temp_judgement = int(
        sensor_data.get(
            "tempC_judgement",
            0
        )
    )

    soil_judgement = int(
        sensor_data.get(
            "soil_judgement",
            0
        )
    )

    print()
    print("====================================")
    print("AKARIがセンサーデータを受信しました")
    print(f"受信時刻       : {current_time()}")
    print("------------------------------------")
    print(f"温度           : {temp_c} ℃")
    #print(f"温度（華氏）   : {temp_f} °F")
    #print(f"湿度           : {humidity} %")
    #print(f"体感温度       : {heat_index_c} ℃")
    #print(f"体感温度（華氏）: {heat_index_f} °F")
    print(f"土壌センサー   : {soil}")
    #print(f"明るさ         : {light} %")
    # print(
    #     f"温度判定       : "
    #     f"{temperature_status(temp_judgement)}"
    # )
    # print(
    #     f"土壌判定       : "
    #     f"{soil_status(soil_judgement)}"
    # )
    print(
        f"温度判定       : "
        f"{temp_judgement}"
    )
    print(
        f"土壌判定       : "
        f"{soil_judgement}"
    )
    print("====================================")
    print()




# =====================================
# Arduinoからのメッセージ処理
# =====================================
def process_arduino_message(
    message: str,
    client_socket: socket.socket,
    client_address
) -> None:
    global request_in_progress

    message = message.strip()

    if not message:
        return

    # Arduino接続通知
    if message == "ARDUINO_ACTION_READY":
        register_arduino(
            client_socket,
            client_address
        )

        return

    # 接続確認
    if message == "PONG":
        print(
            f"[{current_time()}] "
            "ArduinoからPONGを受信"
        )

        return

    # JSONデータか確認
    try:
        received_data = json.loads(
            message
        )

    except json.JSONDecodeError:
        print(
            f"[{current_time()}] "
            f"不明なデータを受信: {message}"
        )

        return

    # Arduino側エラー
    if "error" in received_data:
        error_message = received_data["error"]

        print(
            f"[{current_time()}] "
            f"Arduinoエラー: {error_message}"
        )

        show_m5_message(
            text=(
                "Sensor Error\n"
                f"{error_message}"
            ),
            text_color=Colors.WHITE,
            back_color=Colors.RED,
            size=3
        )

        with request_lock:
            request_in_progress = False

        return

    # センサーデータ表示
    print_sensor_data(
        received_data
    )

    # display_sensor_data(
    #     received_data
    # )

    with request_lock:
        request_in_progress = False


# =====================================
# Arduino接続処理
# =====================================
def handle_arduino_client(
    client_socket: socket.socket,
    client_address
) -> None:
    receive_buffer = ""

    print(
        f"[{current_time()}] "
        f"6001番ポートへ接続されました: "
        f"{client_address[0]}:"
        f"{client_address[1]}"
    )

    try:
        while not stop_event.is_set():
            data = client_socket.recv(
                BUFFER_SIZE
            )

            if not data:
                break

            receive_buffer += data.decode(
                ENCODING,
                errors="replace"
            )

            while "\n" in receive_buffer:
                message, receive_buffer = (
                    receive_buffer.split(
                        "\n",
                        1
                    )
                )

                process_arduino_message(
                    message,
                    client_socket,
                    client_address
                )

    except (
        ConnectionResetError,
        BrokenPipeError,
        OSError
    ) as error:
        if not stop_event.is_set():
            print(
                f"[{current_time()}] "
                f"Arduino通信エラー: {error}"
            )

    finally:
        unregister_arduino(
            client_socket
        )

        try:
            client_socket.close()
        except OSError:
            pass


# =====================================
# 6001番ポートサーバー
# =====================================
def start_server() -> None:
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        (HOST, PORT)
    )

    server_socket.listen(5)
    server_socket.settimeout(1.0)

    print("====================================")
    print("AKARIセンサーサーバー起動")
    print(f"待受アドレス: {HOST}")
    print(f"待受ポート  : {PORT}")
    print("Arduinoの接続を待っています")
    print("====================================")

    try:
        while not stop_event.is_set():
            try:
                client_socket, client_address = (
                    server_socket.accept()
                )

            except socket.timeout:
                continue

            thread = threading.Thread(
                target=handle_arduino_client,
                args=(
                    client_socket,
                    client_address
                ),
                daemon=True
            )

            thread.start()

    finally:
        server_socket.close()


# =====================================
# ボタンA処理
# =====================================
def request_sensor_data() -> None:
    global request_in_progress

    with request_lock:
        if request_in_progress:
            print(
                f"[{current_time()}] "
                "現在センサーデータを取得中です"
            )

            return

        request_in_progress = True

    show_m5_message(
        text=(
            "Reading\n"
            "Sensor Data..."
        ),
        text_color=Colors.BLACK,
        back_color=Colors.YELLOW,
        size=5
    )

    result = send_command_to_arduino(
        "GET_SENSOR_DATA"
    )

    if not result:
        with request_lock:
            request_in_progress = False

        show_m5_message(
            text=(
                "Arduino\n"
                "Not Connected"
            ),
            text_color=Colors.WHITE,
            back_color=Colors.RED,
            size=5
        )


# =====================================
# M5Stackボタン監視
# =====================================
def monitor_buttons(
    m5
) -> None:

    last_sent = None

    while not stop_event.is_set():
        try:


            now = datetime.now()

            if now.second == 0:

                key = (now.hour, now.minute)

                if key != last_sent:#同じ時刻に何回も送られないように
                    request_sensor_data()
                    last_sent = key

        except Exception as error:
            print(
                f"[{current_time()}] "
                f"M5Stack取得エラー: {error}"
            )

            time.sleep(1)

        time.sleep(
            BUTTON_CHECK_INTERVAL
        )


# =====================================
# メイン処理
# =====================================
def main() -> None:
    global m5_instance
    global arduino_socket

    server_thread = threading.Thread(target=start_server,daemon=True)

    server_thread.start()

    try:
        with AkariClient() as akari:
            m5 = akari.m5stack
            m5_instance = m5

            print("AKARIへ接続しました")

            show_m5_message(
                text=(
                    "Waiting for\n"
                    "Arduino..."
                ),
                text_color=Colors.WHITE,
                back_color=Colors.BLACK,
                size=5
            )

            monitor_buttons(m5)

    except KeyboardInterrupt:
        print()
        print("キーボード操作で終了します")

    except Exception as error:
        print(
            f"AKARI接続エラー: {error}"
        )

    finally:
        stop_event.set()

        with arduino_lock:
            if arduino_socket is not None:
                try:
                    arduino_socket.close()
                except OSError:
                    pass

                arduino_socket = None

        print("プログラムを終了しました")


if __name__ == "__main__":
    main()