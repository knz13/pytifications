


class Pytifications:
    def __init__(self,login,password):
        self._logged_in = False

    def send_message(self,message: str):
        if not self._logged_in:
            print('could not send pynotification, make sure you have logged in correctly')
            return    
        pass

    def am_i_logged_in(self):
        return self._logged_in
    