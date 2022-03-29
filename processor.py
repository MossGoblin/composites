import logging
import os
from utils import SettingsParser, ToolBox

class Processor():

    def __init__(self, config_file='config.ini') -> None:
        self.sp = SettingsParser(config_file=config_file)
        self.settings = self.sp.get_settings()
        self.logger = self.set_up_logger()

    def set_up_logger(self):
        # create logger
        logger = logging.getLogger(__name__)
        log_level = self.settings['logger_level']
        logger.setLevel(log_level)
        # create formatter and set level
        formatter = logging.Formatter(self.settings['logger_format'])

        reset_log_folder = self.settings['reset_log_files']
        log_folder = self.settings['logging_base_folder']
        self.prep_folder(log_folder, reset_log_folder)

        logger_mode = self.settings['log_mode']
        if logger_mode == 'console' or logger_mode == 'full':
            # create console handler
            handler = logging.StreamHandler()
            # add formatter to handler
            handler.setFormatter(formatter)
            # add handler to logger
            logger.addHandler(handler)
            
        if logger_mode == 'file' or logger_mode == 'full':
            # create file handler
            log_file_name = self.settings['log_file_name_string']
            if not log_folder == 'none':
                log_file_name = log_folder + "/" + log_file_name
            handler = logging.FileHandler(log_file_name, mode='w', encoding='utf-8')
            # add formatter to handler
            handler.setFormatter(formatter)
            # add handler to logger
            logger.addHandler(handler)
        
        return logger

    def prep_folder(self, folder_name: str, reset_folder: bool):
        '''
        Prepare folder for output csv files
        '''

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
            return
        else:
            if reset_folder:
                for root, directories, files in os.walk(folder_name):
                    for file in files:
                        file_path = root + '/' + file
                        os.remove(file_path)
            return

    def run(self):
        self.logger.info('Start')
        self.logger.debug('Going...')
        self.logger.info('Done')
        pass
