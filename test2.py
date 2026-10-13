"""Kachakaのドッキング・巡回・一時停止・再開処理。"""

import json
import os
import random
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from kachaka_api import KachakaApiClient

import runtime_state as state

from akari_completion_server import (
    send_kachaka_round_completed_to_akari,
)

from akari_server import (
    send_sensor_data_to_akari,
)

from config import (
    DOCK_WAIT_SECONDS,
    KACHAKA_TARGET,
    LOCATION_WAIT_SECONDS,
    MOVE_WAIT_SECONDS,
    RANDOM_LOCATIONS,
    SHELF_DOCK_POSE_FILE,
    UNDOCK_WAIT_SECONDS,
)


# ==================================================
# Kachakaクライアント
# ==================================================
kachaka_client = KachakaApiClient(
    target=KACHAKA_TARGET
)


# ==================================================
# Kachaka API結果確認
# ==================================================
def is_kachaka_success(result):
    """
    Kachaka APIの実行結果が成功か確認する。
    """
    if result is None:
        return False

    if isinstance(result, bool):
        return result

    success = getattr(
        result,
        "success",
        None,
    )

    if success is not None:
        return bool(success)

    # kachaka_apiのバージョンによって、
    # 戻り値にsuccessがない場合がある。
    return True


def print_kachaka_error(
    action_name,
    result,
):
    """
    Kachaka APIのエラーを表示する。
    """
    print(
        f"{action_name}に失敗しました。"
    )

    if result is None:
        print(
            "Kachaka APIから結果を"
            "取得できませんでした。"
        )

        return

    error_code = getattr(
        result,
        "error_code",
        None,
    )

    if error_code is not None:
        print(
            "エラーコード:",
            error_code,
        )


# ==================================================
# Kachaka現在位置
# ==================================================
def get_current_robot_pose():
    """
    Kachakaの現在位置を辞書形式で取得する。
    """
    pose = kachaka_client.get_robot_pose()

    return {
        "x": float(pose.x),
        "y": float(pose.y),
        "theta": float(pose.theta),
    }


def print_pose(
    pose,
    title="Kachaka位置",
):
    """
    Kachakaの位置を表示する。
    """
    print(title)
    print(f"x     : {pose['x']}")
    print(f"y     : {pose['y']}")
    print(f"theta : {pose['theta']}")


# ==================================================
# シェルフ位置保存
# ==================================================
def save_shelf_dock_pose(
    pose=None,
):
    """
    次回シェルフへドッキングするときに使用する
    Kachaka位置をJSONファイルへ保存する。
    """
    try:
        if pose is None:
            pose = get_current_robot_pose()

        pose_data = {
            "x": float(pose["x"]),
            "y": float(pose["y"]),
            "theta": float(pose["theta"]),
            "saved_at": datetime.now(
                ZoneInfo("Asia/Tokyo")
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

        temporary_file = (
            SHELF_DOCK_POSE_FILE + ".tmp"
        )

        with open(
            temporary_file,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                pose_data,
                file,
                ensure_ascii=False,
                indent=4,
            )

        os.replace(
            temporary_file,
            SHELF_DOCK_POSE_FILE,
        )

        print(
            "次回用のシェルフ"
            "ドッキング位置を保存しました。"
        )

        print_pose(
            pose_data,
            "保存した位置",
        )

        return True

    except Exception as error:
        print(
            "ドッキング位置の保存エラー:",
            type(error).__name__,
            error,
        )

        return False


def load_shelf_dock_pose():
    """
    保存済みのシェルフドッキング位置を読み込む。
    """
    if not os.path.exists(
        SHELF_DOCK_POSE_FILE
    ):
        print(
            f"{SHELF_DOCK_POSE_FILE}が"
            "存在しません。"
        )

        return None

    try:
        with open(
            SHELF_DOCK_POSE_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            pose_data = json.load(file)

        required_keys = (
            "x",
            "y",
            "theta",
        )

        for key in required_keys:
            if key not in pose_data:
                print(
                    "ドッキング位置ファイルに"
                    f"{key}がありません。"
                )

                return None

        pose = {
            "x": float(pose_data["x"]),
            "y": float(pose_data["y"]),
            "theta": float(pose_data["theta"]),
        }

        print_pose(
            pose,
            "読み込んだシェルフ位置",
        )

        return pose

    except (
        OSError,
        ValueError,
        TypeError,
        json.JSONDecodeError,
    ) as error:
        print(
            "ドッキング位置の読み込みエラー:",
            type(error).__name__,
            error,
        )

        return None


def calibrate_shelf_dock_pose():
    """
    現在のKachaka位置を
    シェルフドッキング位置として保存する。
    """
    print(
        "現在のKachaka位置を"
        "シェルフドッキング位置として登録します。"
    )

    try:
        current_pose = get_current_robot_pose()

        print_pose(
            current_pose,
            "登録する位置",
        )

        return save_shelf_dock_pose(
            current_pose
        )

    except Exception as error:
        print(
            "シェルフ位置登録エラー:",
            type(error).__name__,
            error,
        )

        return False


# ==================================================
# 一時停止処理
# ==================================================
def cancel_current_kachaka_command():
    """
    現在実行中のKachaka命令をキャンセルする。
    """
    try:
        result = kachaka_client.cancel_command()

        if result is None:
            print(
                "Kachakaへ現在命令の"
                "キャンセル要求を送信しました。"
            )

            return True

        if isinstance(result, bool):
            if result:
                print(
                    "Kachakaの現在命令を"
                    "キャンセルしました。"
                )

            else:
                print(
                    "Kachaka命令のキャンセル結果が"
                    "Falseでした。"
                )

            return result

        success = getattr(
            result,
            "success",
            None,
        )

        if success is None:
            print(
                "Kachakaへ現在命令の"
                "キャンセル要求を送信しました。"
            )

            return True

        if success:
            print(
                "Kachakaの現在命令を"
                "キャンセルしました。"
            )

            return True

        print_kachaka_error(
            "Kachaka命令のキャンセル",
            result,
        )

        return False

    except Exception as error:
        print(
            "Kachaka命令キャンセルエラー:",
            type(error).__name__,
            error,
        )

        return False


def pause_kachaka():
    """
    Kachakaをその場で一時停止する。

    この処理では以下を実行しない。
    ・シェルフ返却
    ・シェルフ解除
    ・充電ドック帰還
    """
    print("----------------------------------------")
    print("Kachakaの一時停止要求を受信しました。")

    # 先に一時停止状態へ変更する。
    state.kachaka_stop_event.set()

    success = cancel_current_kachaka_command()

    if success:
        print(
            "Kachakaをその場で停止しました。"
        )

    else:
        print(
            "現在命令のキャンセル確認には"
            "失敗しましたが、"
            "一時停止状態は維持します。"
        )

    print(
        "kachaka go、kachaka start、"
        "またはkachaka resumeを"
        "受信するまで待機します。"
    )

    print("----------------------------------------")

    return success


def resume_kachaka():
    """
    Kachakaの一時停止状態を解除する。

    この関数はAKARIへの通知を行わない。
    """
    if not state.kachaka_stop_event.is_set():
        print(
            "Kachakaは一時停止していません。"
        )

        return False

    state.kachaka_stop_event.clear()

    print("----------------------------------------")
    print("Kachakaの再開命令を受信しました。")
    print("停止前の巡回処理を再開します。")
    print(
        "再開時点ではAKARIへ"
        "一周完了通知を送信しません。"
    )
    print("----------------------------------------")

    return True


def wait_while_kachaka_paused():
    """
    一時停止中の場合、
    再開命令を受信するまで待機する。
    """
    waiting_message_printed = False

    while state.kachaka_stop_event.is_set():
        if not waiting_message_printed:
            print("----------------------------------------")
            print(
                "Kachakaは現在位置で一時停止中です。"
            )
            print(
                "シェルフ返却は行いません。"
            )
            print(
                "充電ドックへも戻りません。"
            )
            print(
                "kachaka go、kachaka start、"
                "またはkachaka resumeを"
                "待っています。"
            )
            print("----------------------------------------")

            waiting_message_printed = True

        if state.shutdown_event.wait(
            timeout=0.5
        ):
            return False

    if waiting_message_printed:
        print(
            "Kachakaの一時停止が解除されました。"
        )
        print(
            "中断していた処理を続けます。"
        )

    return not state.shutdown_event.is_set()


def wait_with_pause(seconds):
    """
    指定時間待機する。

    待機中にstopを受信した場合は、
    再開されるまで残り時間の計測を止める。
    """
    remaining = float(seconds)

    while remaining > 0:
        if state.shutdown_event.is_set():
            return False

        if not wait_while_kachaka_paused():
            return False

        wait_seconds = min(
            0.2,
            remaining,
        )

        start_time = time.monotonic()

        if state.shutdown_event.wait(
            timeout=wait_seconds
        ):
            return False

        elapsed = (
            time.monotonic() - start_time
        )

        remaining -= elapsed

    return True


# ==================================================
# 一時停止対応移動
# ==================================================
def move_to_location_with_pause(
    location_name,
    action_name,
):
    """
    登録地点へ移動する。

    移動中にstopを受信した場合は、
    再開後に同じ移動先への命令を再実行する。

    通常の移動失敗の場合はFalseを返す。
    呼び出し側でその地点をスキップする。
    """
    while not state.shutdown_event.is_set():
        if not wait_while_kachaka_paused():
            return False

        print(
            f"{action_name}を開始します。"
        )

        print(
            "移動先:",
            location_name,
        )

        try:
            result = (
                kachaka_client.move_to_location(
                    location_name
                )
            )

        except Exception as error:
            if state.kachaka_stop_event.is_set():
                print(
                    f"{action_name}中に"
                    "一時停止しました。"
                )

                if not wait_while_kachaka_paused():
                    return False

                print(
                    f"{location_name}への移動を"
                    "再実行します。"
                )

                continue

            print(
                f"{action_name}中にエラーが"
                "発生しました:",
                type(error).__name__,
                error,
            )

            return False

        # stopによるキャンセルの場合
        if state.kachaka_stop_event.is_set():
            print(
                f"{action_name}中に"
                "一時停止しました。"
            )

            if not wait_while_kachaka_paused():
                return False

            print(
                f"{location_name}への移動を"
                "再実行します。"
            )

            continue

        # 通常の移動失敗
        if not is_kachaka_success(result):
            print_kachaka_error(
                action_name,
                result,
            )

            return False

        print(
            f"{action_name}が完了しました。"
        )

        return True

    return False


def move_to_pose_with_pause(
    pose,
    action_name,
):
    """
    指定座標へ移動する。

    移動中にstopを受信した場合は、
    再開後に同じ座標への移動を再実行する。
    """
    while not state.shutdown_event.is_set():
        if not wait_while_kachaka_paused():
            return False

        print(
            f"{action_name}を開始します。"
        )

        print_pose(
            pose,
            "移動先座標",
        )

        try:
            result = kachaka_client.move_to_pose(
                pose["x"],
                pose["y"],
                pose["theta"],
            )

        except Exception as error:
            if state.kachaka_stop_event.is_set():
                print(
                    f"{action_name}中に"
                    "一時停止しました。"
                )

                if not wait_while_kachaka_paused():
                    return False

                print(
                    f"{action_name}を再実行します。"
                )

                continue

            print(
                f"{action_name}中にエラーが"
                "発生しました:",
                type(error).__name__,
                error,
            )

            return False

        if state.kachaka_stop_event.is_set():
            print(
                f"{action_name}中に"
                "一時停止しました。"
            )

            if not wait_while_kachaka_paused():
                return False

            print(
                f"{action_name}を再実行します。"
            )

            continue

        if not is_kachaka_success(result):
            print_kachaka_error(
                action_name,
                result,
            )

            return False

        print(
            f"{action_name}が完了しました。"
        )

        return True

    return False


def execute_action_with_pause(
    action,
    action_name,
):
    """
    ドッキングやシェルフ解除などの命令を
    一時停止対応で実行する。
    """
    while not state.shutdown_event.is_set():
        if not wait_while_kachaka_paused():
            return False

        print(
            f"{action_name}を開始します。"
        )

        try:
            result = action()

        except Exception as error:
            if state.kachaka_stop_event.is_set():
                print(
                    f"{action_name}中に"
                    "一時停止しました。"
                )

                if not wait_while_kachaka_paused():
                    return False

                print(
                    f"{action_name}を再実行します。"
                )

                continue

            print(
                f"{action_name}中にエラーが"
                "発生しました:",
                type(error).__name__,
                error,
            )

            return False

        if state.kachaka_stop_event.is_set():
            print(
                f"{action_name}中に"
                "一時停止しました。"
            )

            if not wait_while_kachaka_paused():
                return False

            print(
                f"{action_name}を再実行します。"
            )

            continue

        if not is_kachaka_success(result):
            print_kachaka_error(
                action_name,
                result,
            )

            return False

        print(
            f"{action_name}が完了しました。"
        )

        return True

    return False


# ==================================================
# Kachaka巡回
# ==================================================
def run_kachaka_route(sensor=None):
    """
    Kachakaの巡回処理を実行する。

    処理順:
    1. 保存済みシェルフ位置へ移動
    2. シェルフへドッキング
    3. ランダム順で巡回
    4. 最初に実際に到着できた巡回地点で
       AKARIへセンサーデータ送信
    5. 巡回地点への移動失敗時は
       その地点だけスキップ
    6. シェルフの元位置へ戻る
    7. シェルフを解除
    8. 次回用位置を保存
    9. 条件を満たした場合のみ一周完了通知
    10. Kachakaだけ充電ドックへ戻る

    巡回地点への移動失敗:
    ・次の地点がある場合は次へ進む
    ・最後の地点だった場合は最後の処理へ進む
    ・シェルフ返却や充電ドック帰還は実行する
    ・一周完了通知は送信しない

    一周完了通知の条件:
    ・今回の巡回でstopを一度も受信していない
    ・巡回地点への移動失敗が一度もない
    ・シェルフ返却が完了している
    ・シェルフ解除が完了している
    """
    acquired = (
        state.kachaka_route_lock.acquire(
            blocking=False
        )
    )

    if not acquired:
        print(
            "Kachakaはすでに巡回処理を"
            "実行しています。"
        )

        return False

    # 新しい巡回開始時のみ
    # stop履歴をリセットする。
    with state.kachaka_route_state_lock:
        state.kachaka_route_running = True
        state.kachaka_stop_received_during_route = False

    try:
        print(
            "===== Kachakaランダム巡回開始 ====="
        )

        if not wait_while_kachaka_paused():
            return False

        original_dock_pose = (
            load_shelf_dock_pose()
        )

        if original_dock_pose is None:
            print(
                "シェルフのドッキング位置を"
                "読み込めないため、"
                "巡回を開始できません。"
            )

            return False

        # ------------------------------------------------
        # シェルフ位置へ移動
        # ------------------------------------------------
        move_success = move_to_pose_with_pause(
            pose=original_dock_pose,
            action_name="シェルフ位置への移動",
        )

        if not move_success:
            return False

        if not wait_with_pause(
            MOVE_WAIT_SECONDS
        ):
            return False

        # ------------------------------------------------
        # シェルフへドッキング
        # ------------------------------------------------
        dock_success = execute_action_with_pause(
            action=kachaka_client.dock_shelf,
            action_name="あかりシェルフへのドッキング",
        )

        if not dock_success:
            return False

        if not wait_with_pause(
            DOCK_WAIT_SECONDS
        ):
            return False

        print(
            "あかりシェルフへの"
            "ドッキングが完了しました。"
        )

        # ------------------------------------------------
        # 巡回順をランダム化
        # ------------------------------------------------
        patrol_locations = list(
            RANDOM_LOCATIONS
        )

        random.shuffle(
            patrol_locations
        )

        print(
            "今回の巡回順:",
            " → ".join(patrol_locations),
        )

        # ------------------------------------------------
        # ランダム巡回
        # ------------------------------------------------
        # 最初に実際に到着した地点で
        # センサーデータを一度だけ送る。
        akari_sensor_sent = False

        # 巡回地点への移動失敗が
        # 一度でもあったか。
        route_move_failed = False

        # 実際に到着できた地点数。
        reached_location_count = 0

        for index, location_name in enumerate(
            patrol_locations
        ):
            if not wait_while_kachaka_paused():
                return False

            move_success = (
                move_to_location_with_pause(
                    location_name=location_name,
                    action_name=(
                        f"巡回地点"
                        f"{location_name}への移動"
                    ),
                )
            )

            # ============================================
            # 巡回地点への移動失敗
            # ============================================
            if not move_success:
                route_move_failed = True

                print(
                    f"巡回地点{location_name}への"
                    "移動に失敗しました。"
                )

                is_last_location = (
                    index
                    == len(patrol_locations) - 1
                )

                if is_last_location:
                    print(
                        "この地点が最後の巡回地点のため、"
                        "シェルフ返却などの"
                        "最後の処理へ進みます。"
                    )

                else:
                    print(
                        "この地点をスキップして、"
                        "次の巡回地点へ進みます。"
                    )

                # return Falseにはしない。
                # 次の巡回地点へ進む。
                continue

            # ============================================
            # 巡回地点への移動成功
            # ============================================
            reached_location_count += 1

            print(
                f"巡回地点{location_name}へ"
                "到着しました。"
            )

            # ------------------------------------------------
            # 最初に「実際に到着できた地点」で
            # AKARIへセンサーデータ送信
            # ------------------------------------------------
            #
            # 最初の予定地点に失敗しても、
            # 次に成功した地点で送信する。
            if (
                sensor is not None
                and not akari_sensor_sent
            ):
                if not wait_while_kachaka_paused():
                    return False

                send_success = (
                    send_sensor_data_to_akari(
                        sensor
                    )
                )

                # 送信を試みたのでTrueにする。
                # この巡回中に何度も送信しない。
                akari_sensor_sent = True

                if send_success:
                    print(
                        "最初に到着した巡回地点で"
                        "AKARIへセンサーデータを"
                        "送信しました。"
                    )

                else:
                    print(
                        "AKARIへのセンサーデータ送信に"
                        "失敗しました。"
                    )

            # 到着後の待機
            if not wait_with_pause(
                LOCATION_WAIT_SECONDS
            ):
                return False

        # ------------------------------------------------
        # 巡回結果表示
        # ------------------------------------------------
        print(
            "----------------------------------------"
        )

        print(
            "ランダム巡回処理が終了しました。"
        )

        print(
            "巡回予定地点数:",
            len(patrol_locations),
        )

        print(
            "到着成功地点数:",
            reached_location_count,
        )

        if route_move_failed:
            print(
                "一部の巡回地点への移動に"
                "失敗しました。"
            )

            print(
                "シェルフ返却などの"
                "最後の処理は継続します。"
            )

        else:
            print(
                "すべての巡回地点への"
                "移動が完了しました。"
            )

        if reached_location_count == 0:
            print(
                "巡回地点には1か所も"
                "到着できませんでしたが、"
                "シェルフ返却処理へ進みます。"
            )

        print(
            "----------------------------------------"
        )

        # ------------------------------------------------
        # 元のシェルフ位置へ戻る
        # ------------------------------------------------
        if not wait_while_kachaka_paused():
            return False

        return_success = move_to_pose_with_pause(
            pose=original_dock_pose,
            action_name="元のシェルフ位置への帰還",
        )

        if not return_success:
            print(
                "シェルフを載せた状態のため、"
                "現在位置ではシェルフを解除しません。"
            )

            return False

        print(
            "最初にシェルフが"
            "置いてあった位置へ戻りました。"
        )

        if not wait_with_pause(
            MOVE_WAIT_SECONDS
        ):
            return False

        # ------------------------------------------------
        # シェルフを元の場所へ置く
        # ------------------------------------------------
        undock_success = execute_action_with_pause(
            action=kachaka_client.undock_shelf,
            action_name="あかりシェルフの解除",
        )

        if not undock_success:
            return False

        print(
            "あかりシェルフを"
            "元の場所へ置きました。"
        )

        if not wait_with_pause(
            UNDOCK_WAIT_SECONDS
        ):
            return False

        # ------------------------------------------------
        # 次回用ドッキング位置保存
        # ------------------------------------------------
        current_dock_pose = (
            get_current_robot_pose()
        )

        print_pose(
            current_dock_pose,
            "シェルフ解除後のKachaka位置",
        )

        if not save_shelf_dock_pose(
            current_dock_pose
        ):
            print(
                "シェルフは元の場所へ置きましたが、"
                "次回用位置を保存できませんでした。"
            )

            return False

        # ------------------------------------------------
        # AKARI一周完了通知
        # ------------------------------------------------
        with state.kachaka_route_state_lock:
            stop_received_during_route = (
                state.kachaka_stop_received_during_route
            )

        if stop_received_during_route:
            print(
                "----------------------------------------"
            )

            print(
                "今回の巡回中にkachaka stopを"
                "受信しているため、"
            )

            print(
                "AKARIへの一周完了通知は"
                "送信しません。"
            )

            print(
                "----------------------------------------"
            )

        elif route_move_failed:
            print(
                "----------------------------------------"
            )

            print(
                "今回の巡回では"
                "移動に失敗した地点があるため、"
            )

            print(
                "AKARIへの一周完了通知は"
                "送信しません。"
            )

            print(
                "----------------------------------------"
            )

        else:
            completion_sent = (
                send_kachaka_round_completed_to_akari()
            )

            if completion_sent:
                print(
                    "AKARIへKachaka一周完了通知を"
                    "送信しました。"
                )

            else:
                print(
                    "Kachakaの一周は完了しましたが、"
                    "AKARIへの一周完了通知を"
                    "送信できませんでした。"
                )

        # ------------------------------------------------
        # Kachakaだけ充電ドックへ戻る
        # ------------------------------------------------
        if not wait_while_kachaka_paused():
            return False

        charger_success = execute_action_with_pause(
            action=kachaka_client.return_home,
            action_name="充電ドックへの帰還",
        )

        if not charger_success:
            return False

        print(
            "Kachakaが充電ドックへ"
            "戻りました。"
        )

        # ------------------------------------------------
        # 最終結果
        # ------------------------------------------------
        if route_move_failed:
            print(
                "===== Kachaka巡回終了 "
                "（一部地点スキップ）====="
            )

        else:
            print(
                "===== Kachakaランダム巡回完了 ====="
            )

        # 巡回地点の一部に失敗していても、
        # シェルフ返却と充電ドック帰還まで
        # 正常に完了したためTrueを返す。
        #
        # これによりsensor_service側では
        # 通常どおりクールダウンへ入る。
        return True

    except Exception as error:
        print(
            "Kachaka巡回エラー:",
            type(error).__name__,
            error,
        )

        return False

    finally:
        with state.kachaka_route_state_lock:
            state.kachaka_route_running = False

        state.kachaka_route_lock.release()