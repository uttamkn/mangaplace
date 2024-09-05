import subprocess


def build():
    subprocess.run(["pyinstaller", "--onefile", "src/main.py"])


if __name__ == "__main__":
    build()
