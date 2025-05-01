import subprocess
import sys
import time

scripts = [
    "backend.processors.gfw.vessels_api",
    "backend.processors.gfw.loitering_api"
]

def main():
    while True:
        for script in scripts:
            print(f"\nRunning {script} ...")
            subprocess.run([sys.executable, "-m", script])

        print("\n5 minute waiting period ... ")
        time.sleep(300)

if __name__ == "__main__":
    main()
