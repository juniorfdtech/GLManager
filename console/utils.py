import os


def pause(text='\nEnter para continuar'):
    input('\033[1;32m' + text + '\033[0m')


def get_ip_address():
    import urllib.request as request

    path = os.path.join(os.path.expanduser('~'), '.ip')

    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read().strip()

    try:
        url = 'https://api.ipify.org'
        response = request.urlopen(url)
        ip = response.read().decode('utf-8')

        with open(path, 'w') as f:
            f.write(ip.strip())

        return ip.strip()

    except Exception as e:
        return '0.0.0.0'
