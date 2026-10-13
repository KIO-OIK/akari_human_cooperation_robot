"""
AKARIへKachaka一周完了通知を送信するTCPサーバー。

このファイルでは、主に次の処理を行う。

1. AKARIからのTCP接続を待ち受ける
2. 接続されたAKARIのソケット情報を保存する
3. Kachakaの巡回完了時に、保存されている接続を使って通知する
4. 接続切断や通信エラーが発生した場合にソケットを安全に閉じる
5. 空文字列や改行のみのデータがAKARIへ送られることを防ぐ

重要:
AKARIがサーバーへ接続しただけでは、データは送信しない。
明示的に通知関数が呼ばれた場合のみ、AKARIへ文字列を送信する。
"""


# TCP/IP通信を行うためのPython標準ライブラリ。
# サーバーソケットの作成、接続受付、データ送信、
# ソケットの切断などに使用する。
import socket

# 型ヒントで使用する型を読み込む。
#
# Optional:
#   値が指定された型、またはNoneになることを表す。
#
# Tuple:
#   複数の値を組み合わせたタプル型を表す。
#   このコードでは接続元アドレスの
#   「IPアドレス」と「ポート番号」を表すために使用する。
from typing import Optional, Tuple


# プログラム全体で共有する実行状態を管理するモジュール。
#
# このモジュールには、主に次の情報が保存されている。
#
# ・現在接続中のAKARIのソケット
# ・AKARIの接続元アドレス
# ・ソケット情報を安全に操作するためのロック
# ・プログラム終了を通知するイベント
#
# 複数のスレッドから同じ情報を扱う可能性があるため、
# runtime_stateを通して共有状態を管理している。
import runtime_state as state


# 設定ファイルから、AKARI通知サーバーの
# 待受IPアドレスとポート番号を読み込む。
from config import (
    # サーバーが待ち受けるIPアドレス。
    # 例:
    # "0.0.0.0"の場合は、すべてのネットワークインターフェースで
    # 接続を受け付ける。
    AKARI_COMPLETION_SERVER_HOST,

    # AKARI一周完了通知用TCPサーバーのポート番号。
    AKARI_COMPLETION_SERVER_PORT,
)


# ==================================================
# AKARIへ送信する完了通知
# ==================================================

# Kachakaが一周を完了したことをAKARIへ伝えるための文字列。
#
# この文字列はAKARI側で受信され、
# 「Kachakaの巡回が完了した」というイベントを
# 判定するために使用される。
#
# 接続時には送信されず、
# send_kachaka_round_completed_to_akari()が
# 呼び出された場合だけ送信される。
KACHAKA_ROUND_COMPLETED_MESSAGE = (
    "kachaka_round_completed"
)


# ==================================================
# ソケットを安全に閉じる
# ==================================================

def close_socket_safely(
    target_socket: Optional[socket.socket],
) -> None:
    """
    指定されたソケットを安全に閉じる。

    target_socketには、閉じたいソケット、
    またはNoneを受け取る。

    ソケットを閉じる際は、最初にshutdown()を使って
    送受信を停止し、その後close()でソケット自体を閉じる。

    shutdown()に失敗した場合でも、
    close()は必ず試行する。

    すでに切断されているソケットや、
    すでに閉じられたソケットに対してshutdown()や
    close()を実行するとOSErrorが発生する場合がある。

    そのため、OSErrorは無視し、
    プログラム全体が停止しないようにしている。
    """

    # ソケットが渡されていない場合は、
    # 閉じる対象が存在しないため何もせず終了する。
    if target_socket is None:
        return

    try:
        # ソケットの読み込み方向と書き込み方向の
        # 両方の通信を停止する。
        #
        # SHUT_RDWRを指定することで、
        # 受信と送信の両方を停止する。
        target_socket.shutdown(
            socket.SHUT_RDWR
        )

    except OSError:
        # すでに接続が切れている場合や、
        # ソケットが閉じられている場合などは
        # shutdown()でOSErrorが発生することがある。
        #
        # その場合でも、後続のclose()は実行するため、
        # ここでは例外を無視する。
        pass

    try:
        # OSが管理しているソケット資源を解放する。
        target_socket.close()

    except OSError:
        # すでにソケットが閉じられている場合などに
        # OSErrorが発生する可能性がある。
        #
        # 終了処理中のエラーによってプログラム全体が
        # 停止しないよう、ここでは例外を無視する。
        pass


# ==================================================
# 現在のAKARI接続を閉じる
# ==================================================

def close_akari_completion_connection() -> None:
    """
    現在保存されているAKARIとの
    一周完了通知用接続を閉じる。

    runtime_stateに保存されている
    AKARIのソケットと接続元アドレスを取得し、
    共有状態から削除した後でソケットを閉じる。

    共有状態を操作するときはロックを使用し、
    他のスレッドによる送信処理や接続登録処理と
    同時に変更されないようにする。
    """

    # AKARI接続情報は複数のスレッドから
    # 読み書きされる可能性がある。
    #
    # ロックを取得した状態で、
    # 現在のソケットとアドレスを取り出し、
    # 共有状態をNoneに変更する。
    with state.akari_completion_socket_lock:
        # 現在保存されているAKARI接続ソケットを
        # ローカル変数へ一時保存する。
        current_socket = (
            state.akari_completion_socket
        )

        # 現在接続中のAKARIの
        # IPアドレスとポート番号を取得する。
        current_address = (
            state.akari_completion_address
        )

        # 共有状態上では、AKARIが接続していない状態にする。
        #
        # ソケットを実際に閉じる前にNoneへ変更することで、
        # 他のスレッドが古いソケットを使用しにくくする。
        state.akari_completion_socket = None
        state.akari_completion_address = None

    # 接続元アドレスが保存されている場合は、
    # どのAKARI接続を終了するのかコンソールへ表示する。
    if current_address is not None:
        print(
            "AKARI一周完了通知用接続を"
            "終了します:",
            f"{current_address[0]}:"
            f"{current_address[1]}",
        )

    # ロックの外側でソケットを閉じる。
    #
    # ソケットのshutdown()やclose()に時間がかかった場合でも、
    # ロックを長時間保持しないようにしている。
    close_socket_safely(
        current_socket
    )


# ==================================================
# AKARI接続登録
# ==================================================

def register_akari_completion_connection(
    client_socket: socket.socket,
    address: Tuple[str, int],
) -> None:
    """
    AKARIから接続されたソケットを保存する。

    client_socket:
        accept()によって取得した、
        AKARIとの通信に使用するソケット。

    address:
        接続元AKARIのアドレス情報。
        address[0]にIPアドレス、
        address[1]にポート番号が保存されている。

    すでにAKARIが接続している状態で新しい接続が来た場合は、
    新しい接続を登録した後、以前の接続を閉じる。

    重要:
    この関数ではsend()やsendall()を実行しない。

    そのため、AKARIが接続しただけでは
    文字列、空文字列、改行などを一切送信しない。
    """

    # 以前接続していたAKARIのソケットを
    # 一時保存するための変数。
    old_socket = None

    # 以前接続していたAKARIの
    # IPアドレスとポート番号を保存する変数。
    old_address = None

    # AKARI接続情報は送信処理など、
    # 他のスレッドからも参照される可能性がある。
    #
    # ロック中に現在の接続を取得し、
    # 新しい接続へ置き換える。
    with state.akari_completion_socket_lock:
        # 現在保存されている古いソケットを取得する。
        old_socket = (
            state.akari_completion_socket
        )

        # 現在保存されている古い接続元アドレスを取得する。
        old_address = (
            state.akari_completion_address
        )

        # 今回accept()した新しいAKARIソケットを
        # 共有状態へ保存する。
        state.akari_completion_socket = (
            client_socket
        )

        # 新しく接続したAKARIの
        # IPアドレスとポート番号を保存する。
        state.akari_completion_address = (
            address
        )

    # 接続受付ログを見やすくするための区切り線。
    print("----------------------------------------")

    # AKARIからの一周完了通知用接続を
    # 正常に受け付けたことを表示する。
    print(
        "AKARI一周完了通知用接続を"
        "受け付けました。"
    )

    # 接続してきたAKARIの
    # IPアドレスとポート番号を表示する。
    print(
        "接続元:",
        f"{address[0]}:{address[1]}",
    )

    # 接続しただけではデータを送信しないことを
    # コンソール上で明示する。
    print(
        "接続時にはデータを送信しません。"
    )

    # 接続受付ログの終了を示す区切り線。
    print("----------------------------------------")

    # 新しい接続が来た場合、
    # 以前のソケットは新しい接続の登録後に閉じる。
    #
    # old_socketが存在し、
    # かつ新しく登録したclient_socketとは
    # 別のソケットである場合のみ閉じる。
    if (
        old_socket is not None
        and old_socket is not client_socket
    ):
        # 古い接続元アドレスが分かる場合は、
        # 終了対象をコンソールへ表示する。
        if old_address is not None:
            print(
                "以前のAKARI接続を終了します:",
                f"{old_address[0]}:"
                f"{old_address[1]}",
            )

        # 古いソケットを安全に閉じる。
        close_socket_safely(
            old_socket
        )


# ==================================================
# 送信文字列の検証
# ==================================================

def normalize_completion_message(
    message,
) -> Optional[str]:
    """
    AKARIへ送信する文字列を検証し、
    送信可能な形式に整えて返す。

    messageが次のいずれかに該当する場合は、
    送信対象外としてNoneを返す。

    ・None
    ・空文字列
    ・半角スペースだけの文字列
    ・改行だけの文字列
    ・タブだけの文字列
    ・空白文字だけの文字列

    有効なデータの場合は、前後の空白や改行を
    strip()で取り除いた文字列を返す。
    """

    # message自体がNoneの場合は、
    # 文字列として送信できないためNoneを返す。
    if message is None:
        return None

    # messageを文字列型へ変換する。
    #
    # その後strip()を使い、
    # 文字列の先頭と末尾にある以下の文字を削除する。
    #
    # ・半角スペース
    # ・改行
    # ・タブ
    # ・その他の空白文字
    normalized_message = str(
        message
    ).strip()

    # strip()した結果が空文字列の場合、
    # 実際に送る内容が存在しないためNoneを返す。
    if not normalized_message:
        return None

    # 有効な文字列が残っている場合は、
    # 整形後の文字列を返す。
    return normalized_message


# ==================================================
# AKARIへメッセージ送信
# ==================================================

def send_completion_message(
    message,
) -> bool:
    """
    現在接続中のAKARIへ、有効な文字列だけを送信する。

    送信前にnormalize_completion_message()を使用して、
    送信内容を検証する。

    次の内容は送信しない。

    ・None
    ・空文字列
    ・半角スペースだけ
    ・改行だけ
    ・タブだけ
    ・その他の空白だけ

    送信に成功した場合はTrueを返す。

    次のような場合はFalseを返す。

    ・送信内容が空だった場合
    ・AKARIが接続していない場合
    ・送信中に通信エラーが発生した場合
    """

    # 引数で受け取ったmessageを検証し、
    # 前後の空白を除去した有効な文字列、
    # またはNoneを取得する。
    normalized_message = (
        normalize_completion_message(
            message
        )
    )

    # 検証結果がNoneの場合は、
    # 送信可能なデータが存在しない。
    if normalized_message is None:
        # 空のデータを送ろうとしたことを
        # コンソールへ表示する。
        print(
            "AKARIへの送信内容が空のため、"
            "送信を中止しました。"
        )

        # 送信していないためFalseを返す。
        return False

    # 有効なメッセージの末尾にだけ、
    # データの区切りを示す改行を追加する。
    #
    # その後、TCP通信で送信できるように、
    # UTF-8形式のバイト列へ変換する。
    #
    # 例:
    # "kachaka_round_completed"
    #
    # 送信データ:
    # b"kachaka_round_completed\n"
    send_data = (
        normalized_message + "\n"
    ).encode("utf-8")

    # 通信エラーが発生したソケットを
    # ロックの外側で閉じるために使用する変数。
    disconnected_socket = None

    # AKARIのソケット情報は、
    # 接続受付処理や切断処理からも変更される可能性がある。
    #
    # そのため、ロック中にソケットを取得して送信を行う。
    with state.akari_completion_socket_lock:
        # 現在接続中のAKARIソケットを取得する。
        client_socket = (
            state.akari_completion_socket
        )

        # 現在接続中のAKARIの
        # IPアドレスとポート番号を取得する。
        client_address = (
            state.akari_completion_address
        )

        # AKARIのソケットが保存されていない場合は、
        # AKARIが通知用サーバーへ接続していない。
        if client_socket is None:
            print(
                "AKARIが一周完了通知用ポートへ"
                "接続していないため、"
                "通知を送信できません。"
            )

            # 送信できなかったためFalseを返す。
            return False

        try:
            # 送信開始ログを見やすくするための区切り線。
            print("----------------------------------------")

            # AKARIへ通知を送信することを表示する。
            print(
                "AKARIへ一周完了通知を"
                "送信します。"
            )

            # 接続先アドレスが保存されている場合は、
            # 送信先のIPアドレスとポート番号を表示する。
            if client_address is not None:
                print(
                    "送信先:",
                    f"{client_address[0]}:"
                    f"{client_address[1]}",
                )

            # 実際にAKARIへ送信する文字列を表示する。
            #
            # ここでは改行を追加する前の文字列を表示する。
            print(
                "送信内容:",
                normalized_message,
            )

            # AKARIへバイト列を送信する。
            #
            # sendall()は、指定したデータ全体が送信されるまで
            # 送信処理を継続する。
            #
            # send()とは異なり、一部のデータだけが送信されて
            # 処理が終了する可能性を抑えられる。
            client_socket.sendall(
                send_data
            )

            # sendall()が例外なく完了した場合、
            # 通知が正常に送信できたことを表示する。
            print(
                "AKARIへの一周完了通知が"
                "完了しました。"
            )

            # 送信ログの終了を示す区切り線。
            print("----------------------------------------")

            # 正常に送信できたためTrueを返す。
            return True

        # TCP接続の切断や通信異常によって
        # 発生する可能性がある例外をまとめて処理する。
        except (
            # 接続先がソケットを閉じた状態で
            # データを送信した場合などに発生する。
            BrokenPipeError,

            # 接続先から接続が強制的にリセットされた場合に
            # 発生する。
            ConnectionResetError,

            # 接続が途中で中止された場合に発生する。
            ConnectionAbortedError,

            # その他のソケット通信やOS関連の
            # エラーが発生した場合に使用される。
            OSError,
        ) as error:
            # エラーの種類と内容をコンソールへ表示する。
            print(
                "AKARIへの一周完了通知に"
                "失敗しました:",
                type(error).__name__,
                error,
            )

            # エラーが発生したソケットを保存する。
            #
            # withブロックを抜けた後で、
            # close_socket_safely()を使用して閉じる。
            disconnected_socket = (
                client_socket
            )

            # エラーが発生したclient_socketが、
            # 現在共有状態に保存されているソケットと
            # 同じものであるか確認する。
            #
            # 送信中に別の接続が登録されている可能性があるため、
            # 同じソケットの場合だけ共有状態を削除する。
            if (
                state.akari_completion_socket
                is client_socket
            ):
                # 接続が切れたソケットを共有状態から削除する。
                state.akari_completion_socket = None
                state.akari_completion_address = None

    # 通信エラーが発生したソケットを安全に閉じる。
    #
    # エラーが発生していない場合はNoneのため、
    # close_socket_safely()内ですぐに処理が終了する。
    close_socket_safely(
        disconnected_socket
    )

    # AKARIへの送信に失敗したためFalseを返す。
    return False


# ==================================================
# Kachaka一周完了通知
# ==================================================

def send_kachaka_round_completed_to_akari() -> bool:
    """
    Kachakaの一周完了をAKARIへ通知する。

    Kachakaが巡回を完了し、
    AKARIを載せたシェルフを元の場所へ戻した後に
    呼び出すことを想定している。

    この関数は、固定の通知文字列である
    KACHAKA_ROUND_COMPLETED_MESSAGEを
    send_completion_message()へ渡す。

    kachaka go、kachaka start、
    kachaka resumeなどの巡回再開処理からは
    呼び出さない。

    これにより、巡回を再開しただけで
    一周完了通知が誤送信されることを防ぐ。

    送信成功時はTrue、
    送信失敗時はFalseを返す。
    """

    # Kachakaの一周完了を示す固定文字列を、
    # AKARIへの共通送信関数へ渡す。
    return send_completion_message(
        KACHAKA_ROUND_COMPLETED_MESSAGE
    )


# ==================================================
# AKARI接続確認
# ==================================================

def is_akari_completion_connected() -> bool:
    """
    AKARIが一周完了通知用ポートへ
    接続しているか確認する。

    runtime_stateにAKARIソケットが
    保存されている場合はTrueを返す。

    ソケットが保存されていない場合は
    Falseを返す。

    注意:
    この関数は、共有状態にソケットが存在するかだけを確認する。
    実際に通信可能かどうかは、送信時に確定する。
    """

    # 他のスレッドがAKARIの接続情報を
    # 更新している途中に読み取らないよう、
    # ロックを取得して確認する。
    with state.akari_completion_socket_lock:
        # ソケットがNoneでなければ接続ありと判断し、
        # Trueを返す。
        #
        # NoneであればFalseを返す。
        return (
            state.akari_completion_socket
            is not None
        )


# ==================================================
# 一周完了通知サーバー
# ==================================================

def akari_completion_server_worker() -> None:
    """
    AKARI一周完了通知用TCPサーバーを起動する。

    このサーバーは、AKARIからのTCP接続を待ち受ける。

    AKARIから接続された場合は、
    通信用ソケットと接続元アドレスを
    runtime_stateへ保存する。

    接続された時点ではデータを送信しない。

    send_kachaka_round_completed_to_akari()、
    またはsend_completion_message()が
    明示的に呼ばれた場合だけAKARIへ通知を送信する。

    shutdown_eventがセットされるまで、
    接続受付処理を繰り返す。
    """

    # IPv4のTCP通信用サーバーソケットを作成する。
    #
    # AF_INET:
    #   IPv4アドレスを使用する。
    #
    # SOCK_STREAM:
    #   TCP通信を使用する。
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )


    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1,
    )

    server_socket.settimeout(1.0)

    try:

        server_socket.bind(
            (
                AKARI_COMPLETION_SERVER_HOST,
                AKARI_COMPLETION_SERVER_PORT,
            )
        )


        server_socket.listen(5)

        # サーバーが正常に起動したことを表示する。
        print(
            "AKARI一周完了通知サーバーを"
            "起動しました。"
        )


        print(
            "待受アドレス:",
            f"{AKARI_COMPLETION_SERVER_HOST}:"
            f"{AKARI_COMPLETION_SERVER_PORT}",
        )


        print(
            "AKARI接続時には"
            "文字列を送信しません。"
        )

        while not state.shutdown_event.is_set():
            try:

                client_socket, address = (
                    server_socket.accept()
                )

            except socket.timeout:

                continue

            except OSError as error:

                if state.shutdown_event.is_set():
                    break

                print(
                    "AKARI一周完了通知サーバーの"
                    "接続受付エラー:",
                    type(error).__name__,
                    error,
                )

                continue
            register_akari_completion_connection(
                client_socket,
                address,
            )

    except OSError as error:
        # bind()やlisten()など、
        # サーバー起動処理でOSErrorが発生した場合に実行される。

        # プログラム終了処理中ではない場合だけ、
        # エラー内容をコンソールへ表示する。
        if not state.shutdown_event.is_set():
            print(
                "AKARI一周完了通知サーバーエラー:",
                type(error).__name__,
                error,
            )

    finally:
        # 正常終了、エラー終了のどちらの場合でも、
        # 現在接続中のAKARIソケットを閉じる。
        close_akari_completion_connection()

        try:
            # 接続受付に使用していた
            # サーバーソケットを閉じる。
            server_socket.close()

        except OSError:
            pass
        print(
            "AKARI一周完了通知サーバーを"
            "終了しました。"
        )


# ==================================================
# 互換用起動関数
# ==================================================

def start_akari_completion_server() -> None:
    """
    AKARI一周完了通知サーバーを起動するための
    互換用関数。

    main.pyや他のファイルが、
    start_akari_completion_server()という関数名を
    使用している場合に対応する。

    実際のサーバー処理は、
    akari_completion_server_worker()で行われる。

    この関数を用意することで、
    呼び出し側の関数名を変更せずに
    サーバーを起動できる。
    """

    # 実際のAKARI一周完了通知サーバー処理を開始する。
    akari_completion_server_worker()