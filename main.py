from multiprocessing import Process
import subprocess
import os
from Utils.Storage import bootstrap_persistent_storage

def run_script(script_name):
    try:
        subprocess.run(['python3', script_name])
    except Exception as e:
        print(f"Ошибка при запуске {script_name}: {e}")

if __name__ == "__main__":
    bootstrap_persistent_storage()

    # Railway/container friendly: enable/disable optional processes via env flags.
    # Defaults: run core + antibot; skip antiddos (iptables/scapy) unless explicitly enabled.
    enable_botuser = os.getenv("ENABLE_BOTUSER", "1") == "1"
    enable_antibot = os.getenv("ENABLE_ANTIBOT", "1") == "1"
    enable_antiddos = os.getenv("ENABLE_ANTIDDOS", "0") == "1"

    files = ['core.py']
    if enable_antiddos:
        files.append('antiddos.py')
    if enable_botuser:
        files.append('botuser.py')
    if enable_antibot:
        files.append('antibot.py')
    
    processes = []
    for file in files:
        process = Process(target=run_script, args=(file,))
        processes.append(process)
        process.start()
    
    
    # Ожидаем завершения всех процессов (магазин работает в фоне)
    for process in processes:
        process.join()
