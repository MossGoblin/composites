from utils import ToolBox

class Processor():

    def __init__(self, config_file) -> None:
        self.tb = ToolBox()
        if config_file == None:
            config_file = 'config.ini'
        pass

    def run(self):
        pass
