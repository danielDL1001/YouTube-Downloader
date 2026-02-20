import platform

if platform.system() == "Windows":
    from windows_version import run
else:
    from linux_version import run

run()