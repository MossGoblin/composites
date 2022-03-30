from datetime import datetime
import logging
from utils import SettingsParser, ToolBox


class Processor():

    def __init__(self, config_file='config.ini') -> None:
        self.opt = SettingsParser(config_file=config_file).get_settings()
        self.tb = ToolBox(self.opt)
        self.logger = self.set_up_logger()
        self.tb.set_logger(self.logger)

    def set_up_logger(self):
        # create logger
        logger = logging.getLogger(__name__)
        log_level = self.opt.logger_level
        logger.setLevel(log_level)
        # create formatter and set level
        formatter = logging.Formatter(self.opt.logger_format)

        reset_log_folder = self.opt.logger_reset_files
        log_folder = self.opt.logger_base_folder
        self.tb.prep_folder(log_folder, reset_log_folder)

        logger_mode = self.opt.logger_mode
        if logger_mode == 'console' or logger_mode == 'full':
            # create console handler
            handler = logging.StreamHandler()
            # add formatter to handler
            handler.setFormatter(formatter)
            # add handler to logger
            logger.addHandler(handler)

        if logger_mode == 'file' or logger_mode == 'full':
            # create file handler
            log_file_name = self.opt.logger_file_name_string
            if not log_folder == 'none':
                log_file_name = log_folder + "/" + log_file_name
            handler = logging.FileHandler(
                log_file_name, mode='w', encoding='utf-8')
            # add formatter to handler
            handler.setFormatter(formatter)
            # add handler to logger
            logger.addHandler(handler)

        return logger

    def log_settings(self):
        '''
        Log settings pertinent to the current run
        '''
        self.logger.info('== SETTINGS ==')
        self.logger.info('NUMBER SET')
        self.logger.info(f'number generation mode: {self.opt.set_mode}')
        if self.opt.set_mode == 'family':
            self.logger.debug(f'families: {self.opt.set_families}')
            self.logger.debug(
                f'identity factor mode: {self.opt.set_identity_factor_mode}')
            if self.opt.set_identity_factor_mode == 'range':
                self.logger.debug(
                    f'identity factor range: {self.opt.set_identity_factor_range_min}..{self.opt.set_identity_factor_range_max}')
            else:
                if self.opt.set_identity_factor_minimum_mode == 'value':
                    ifm = f'value ({self.opt.set_identity_factor_minimum_value})'
                else:
                    ifm = self.opt.set_identity_factor_minimum_mode

                self.logger.debug(f'identity factor minimum: {ifm}')

        elif self.opt.set_mode == 'range':
            self.logger.debug(
                f'range [{self.opt.set_range_min}..{self.opt.set_range_max}]')
            self.logger.debug(
                f'primes: {"included" if self.opt.set_include_primes else "excluded"}]')

        self.logger.info('GRAPH')
        self.logger.info(
            f'graph size: {self.opt.graph_width}/{self.opt.graph_height} x {self.opt.graph_point_size}pt')
        self.logger.info(f'Y-axis: {self.opt.graph_mode}')
        self.logger.debug(f'Colorization: {self.opt.graph_use_color_buckets}')

        self.logger.info('RUN')
        self.logger.info(f'csv output: {self.opt.run_create_csv}')
        if self.opt.run_hard_copy_timestamp_granularity == 0:
            timestamp_format = 'days'
        elif self.opt.run_hard_copy_timestamp_granularity == 1:
            timestamp_format = 'hours'
        elif self.opt.run_hard_copy_timestamp_granularity == 2:
            timestamp_format = 'minutes'
        else:
            timestamp_format = 'full'
        self.logger.debug(f'timestamp granularity: {timestamp_format}')
        self.logger.debug(
            f'output folder reset: {self.opt.run_reset_output_data}')

        self.logger.info('==============')

    def run(self):
        start = datetime.utcnow()
        self.logger.info(f'Start at {start}')
        self.log_settings()
        if self.opt.set_mode == 'file':
            df = self.tb.read_data_from_file()
        else:
            numbers = self.tb.generate_number_list()
            df = self.tb.create_dataframe(numbers)
            self.tb.plot_data(df)
        end = datetime.utcnow()
        self.logger.info(f'End at {end}')
        self.logger.info(f'Total time: {end-start}')
