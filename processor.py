from datetime import datetime
import logging
import os
from utils import SettingsParser, ToolBox

class Processor():

    def __init__(self, config_file='config.ini') -> None:
        self.sp = SettingsParser(config_file=config_file)
        self.logger = self.set_up_logger()

    def set_up_logger(self):
        # create logger
        logger = logging.getLogger(__name__)
        log_level = self.sp.logger_level
        logger.setLevel(log_level)
        # create formatter and set level
        formatter = logging.Formatter(self.sp.logger_format)

        reset_log_folder = self.sp.reset_log_files
        log_folder = self.sp.logging_base_folder
        self.prep_folder(log_folder, reset_log_folder)

        logger_mode = self.sp.log_mode
        if logger_mode == 'console' or logger_mode == 'full':
            # create console handler
            handler = logging.StreamHandler()
            # add formatter to handler
            handler.setFormatter(formatter)
            # add handler to logger
            logger.addHandler(handler)

        if logger_mode == 'file' or logger_mode == 'full':
            # create file handler
            log_file_name = self.sp.log_file_name_string
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
        start = datetime.utcnow()
        self.logger.info(f'Start at {start}')
        # Log settings
        self.logger.info('== SETTINGS ==')
        self.logger.info('NUMBER SET')
        self.logger.info(f'number generation mode: {self.sp.number_mode}')
        if self.sp.number_mode == 'family':
            self.logger.debug(f'namilies: {self.sp.families}')
            self.logger.debug(f'identity factor mode: {self.sp.identity_factor_mode}')
            if self.sp.identity_factor_mode == 'range':
                self.logger.debug(f'identity factor range: {self.sp.identity_factor_range_min}..{self.sp.identity_factor_range_max}')
            else:
                if self.sp.identity_factor_minimum_mode == 'value':
                    ifm = f'value ({self.sp.identity_factor_minimum_value})'
                else: ifm = self.sp.identity_factor_minimum_mode

                self.logger.debug(f'identity factor minimum: {ifm}')

        elif self.sp.number_mode == 'continuous':
            self.logger.debug(f'range [{self.sp.range_min}..{self.sp.range_max}]')
            self.logger.debug(f'primes: {"included" if self.sp.include_primes else "excluded"}]')
        
        self.logger.info('GRAPH')
        self.logger.info(f'graph size: {self.sp.width}/{self.sp.height} x {self.sp.point_size}pt')
        self.logger.info(f'Y-axis: {self.sp.graph_mode}')
        self.logger.debug(f'Colorization: {self.sp.use_color_buckets}')

        self.logger.info('RUN')
        self.logger.info(f'csv output: {self.sp.create_csv}')
        if self.sp.hard_copy_timestamp_granularity==0:
            timestamp_format = 'days'
        elif self.sp.hard_copy_timestamp_granularity==1:
            timestamp_format = 'hours'
        elif self.sp.hard_copy_timestamp_granularity==2:
            timestamp_format = 'minutes'
        else:
            timestamp_format = 'full'
        self.logger.debug(f'timestamp granularity: {timestamp_format}')
        self.logger.debug(f'output folder reset: {self.sp.reset_output_data}')

        self.logger.info('==============')
        end = datetime.utcnow()
        self.logger.info(f'End at {end}')
        self.logger.info(f'Total time: {end-start}')
