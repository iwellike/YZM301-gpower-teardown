"""Records a short (~15s) screen video of the CLI running the ratio!=1
a-priori fix (the apriori_ratio_3 case: n1=43, n2=127, matching real
G*Power exactly). The command is typed as real OS-level keystrokes
(pywinauto.keyboard.send_keys) at a human-like pace, not pasted/echoed,
so the recording shows actual typing. Scratch script, not a deliverable.
"""
import os
import random
import subprocess
import time

from pywinauto.keyboard import send_keys

PROJECT_DIR = r"C:\Users\MELIKE TIKIR\Desktop\YZM301-gpower-teardown"
VIDEO_PATH = os.path.join(PROJECT_DIR, "docs", "demo_ratio3_fix.mp4")
CMD = (
    "python -m src.cli --test t2-indep --mode a-priori --tails 2 "
    "--d 0.5 --alpha 0.05 --power 0.8 --ratio 3"
)


def type_like_human(text, lo=0.035, hi=0.09):
    for ch in text:
        send_keys("{SPACE}" if ch == " " else ch)
        time.sleep(random.uniform(lo, hi))


def main():
    subprocess.Popen(["wt.exe", "-d", PROJECT_DIR])
    time.sleep(2.5)
    send_keys("{F11}")
    time.sleep(1.0)

    type_like_human("clear")
    send_keys("{ENTER}")
    time.sleep(1.0)

    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-y", "-f", "gdigrab", "-framerate", "30", "-i", "desktop", VIDEO_PATH],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)

    time.sleep(0.8)
    type_like_human(CMD)
    time.sleep(0.7)
    send_keys("{ENTER}")
    time.sleep(5.0)

    ffmpeg.stdin.write(b"q")
    ffmpeg.stdin.flush()
    ffmpeg.wait(timeout=10)
    print("RECORDING_DONE", VIDEO_PATH)


if __name__ == "__main__":
    main()
