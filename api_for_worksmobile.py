import json
import requests
import winreg


class api_For_Worksmobile():
    def get_tokens(self):
        key = winreg.HKEY_CURRENT_USER
        key_value = r"SOFTWARE\Tks\Ssks\Keys"
        reg = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
        token, type = winreg.QueryValueEx(reg, "akys")
        return token

    def send_mail(self,mails):
        url = 'https://www.worksapis.com/v1.0/users/me/mail'
        tokens = self.get_tokens()
        headers = {"authorization": "Bearer " + tokens,
                   "Content-Type": "application/json"}
        data = mails
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code = 401:
            self.update_tokens
        return response.status_code

    def update_tokens(self):
        url = 'https://auth.worksmobile.com/oauth2/v2.0/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        refresh_token = 'kr1AAAAhJGVFA2wTRsyV15LOX0O5MgAEPtUe5A8y70R5UYNCEp6szRLrDxtPLrU/Dk54VEhs0frpQNkZBYnkhPU7YZ1QeOJy98t1pZitFQ2xEbxgrr+pFyLYnvokjb6xaR5njYeMQPsNqhLgxKGlXYCHOPOZsIdN97qDwgLSndfp4l3XMUBEy3p4eBkPEHD7f24c0Y/Mw=='
        grant_type = "refresh_token"
        client_id = "NZEIZ_Jx9ie_XLxQ4kE2"
        client_secret = "iM9isoQXQx"

        data = {"refresh_token": refresh_token,
                "grant_type": grant_type,
                "client_id": client_id,
                "client_secret": client_secret}

        resp = requests.post(url, data=data, headers=headers)
        tokens = resp.json()
        tokens = tokens['access_token']




