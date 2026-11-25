import os, time, logging
import requests, serial
from dotenv import load_dotenv
load_dotenv()
API_URL=os.getenv('API_URL','').rstrip('/')
TOKEN=os.getenv('AGENT_TOKEN','')
PORT=os.getenv('SERIAL_PORT','COM5')
BAUD=int(os.getenv('BAUD_RATE','9600'))
HEAD={'X-Agent-Token':TOKEN}
logging.basicConfig(level=logging.INFO,format='%(asctime)s | %(levelname)s | %(message)s')
def main():
    if not API_URL.startswith('https://') or not TOKEN: raise SystemExit('Заполните API_URL и AGENT_TOKEN в .env')
    try: board=serial.Serial(PORT,BAUD,timeout=1,write_timeout=2)
    except serial.SerialException as e: raise SystemExit(f'Не удалось открыть {PORT}: {e}')
    time.sleep(2); board.reset_input_buffer(); version=None
    logging.info('Мост запущен: %s → %s',PORT,API_URL)
    try:
        while True:
            try:
                r=requests.get(API_URL+'/api/agent/command',headers=HEAD,timeout=15); r.raise_for_status()
                data=r.json(); desired=bool(data['desired']); new_version=data['version']
                if new_version != version:
                    board.write(('ON\n' if desired else 'OFF\n').encode('ascii')); board.flush()
                    reply=board.readline().decode('ascii',errors='ignore').strip()
                    expected='STATE:ON' if desired else 'STATE:OFF'
                    if reply != expected: logging.warning('Ожидалось %s, получено %r',expected,reply)
                    else: logging.info('Arduino подтвердила %s',reply)
                    version=new_version
                s=requests.post(API_URL+'/api/agent/status',headers=HEAD,json={'on':desired},timeout=15); s.raise_for_status()
                time.sleep(2)
            except (requests.RequestException,serial.SerialException,KeyError,ValueError) as e:
                logging.warning('Ошибка связи: %s',e); time.sleep(5)
    except KeyboardInterrupt: logging.info('Остановка')
    finally: board.close()
if __name__=='__main__': main()
