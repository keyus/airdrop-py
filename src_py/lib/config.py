import json
from .path import config_path,webshare_path

class Config:
    def get_config(self):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return {
                    "status": True,
                    "data": json.load(f),
                }
        except FileNotFoundError:
            return {
                "status": False,
                "message": FileNotFoundError
            }
        
    def set_config(self, config ):
        try:
            with open(config_path, "w") as f:
                f.write(json.dumps(config))
                return {
                    "status": True,
                }
        except FileNotFoundError:
            return {
                "status": False,
                "message": FileNotFoundError
            }
    def get_proxy(self):
        try:
             with open(webshare_path, "r", encoding="utf-8") as f:
                proxy_list = f.readlines()
                proxy_list = [x.strip() for x in proxy_list]
                return {
                    "status": True,
                    "data": proxy_list
                }
        except FileNotFoundError:
            return {
                "status": False,
                "message": FileNotFoundError
            }
        
    def set_proxy(self, proxy):
        try:
            with open(webshare_path, "w") as f:
                for p in proxy:
                    f.write(p + '\n')
                return {
                    "status": True,
                }
        except FileNotFoundError:
            return {
                "status": False,
                "message": FileNotFoundError
            }
    
   