from uuid import getnode as get_mac
import requests
import json

def checkLicense():
    f = open('settings.json') 
    data = json.load(f)
    f.close()

    mac = str(get_mac())
    licencia = data['license']

    data = {
        'clave': licencia,
        'mac': mac
    }

    licenciaValida = 'ez'
    try:
        r = requests.post('http://py.juaristech.com/pythonapps/authenticate', json=data, timeout=7)
        licenciaValida = str(r.content, encoding='utf8')
    except Exception as e:
        print(e)
        return False

    if(licenciaValida == 'ez'):
        return False
    else:
        return True