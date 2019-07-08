class NotLoginError(Exception):
    def __init__(self,text):
        self.text=text
    def __str__(self):
        return repr('not login error, cookie : \n'+self.text)
class BadRequestError(Exception):
    def __init__(self,text):
        self.text=text
    def __str__(self):
        return repr('bad request: '+self.text)