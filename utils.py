from configparser import ConfigParser
import json
import math
from typing import List
import pyprimes as pp
import numpy as np
import re
import pandas as pd


class Number():

    def __init__(self, value):
        self.value = value
        self.is_prime = pp.isprime(self.value)
        if self.value == 1:
            self.ideal_factor = 0
            self.prime_factors = []
            self.mean_deviation = 0
            self.anti_slope = 0
        else:
            self.prime_factors = []
            if self.is_prime:
                self.prime_factors.append(self.value)
            else:
                self.prime_factors = pp.factors(self.value)
            self.ideal_factor = self.get_ideal_factor(
                self.value, self.prime_factors)
            self.mean_deviation = self.get_mean_deviation(
                self.prime_factors, self.ideal_factor)
            if self.mean_deviation > 0:
                self.anti_slope = self.value / self.mean_deviation
            else:
                self.anti_slope = 0

    def __str__(self):
        str = f'value: {self.value} :: '
        str = str + \
            f':: factors: [{self.prime_factors[:-1]}] {self.prime_factors[-1]}'
        str = str + f' > ideal factor: {self.ideal_factor}'
        str = str + f' > mean deviation: {self.mean_deviation}'
        str = str + f' > antislope: {self.anti_slope}'
        return str

    def __repr__(self):
        repr = f'{self.value} ({self.prime_factors[:-1]} {self.prime_factors[-1]})'
        return repr

    def get_ideal_factor(self, value: int, prime_factors: List[int]) -> float:
        return math.pow(value, 1/len(prime_factors))

    def get_mean_deviation(self, prime_factors: List[int], ideal_factor: float) -> float:
        deviations_sum = 0
        for prime_factor in prime_factors:
            deviations_sum += abs(prime_factor - ideal_factor)
        mean_deviation = deviations_sum / len(prime_factors)

        return mean_deviation


class ToolBox():
    def __init__(self, logger, options) -> None:
        self.logger = logger
        self.opt = options


    def generate_number_list(self):
        self.logger.info('Generating numbers')
        number_list = []
        if self.opt.set_mode == 'family':
            self.logger.debug('Processing families')
            number_list = self.generate_number_families()
        elif self.opt.set_mode == 'range':
            self.logger.debug('Processing range')
            number_list = self.generate_continuous_number_list()
        else:
            self.logger.debug('Processing file - NOT IMPLEMENTED YET')
        self.logger.debug(f'Numbers generated ({len(number_list)})')

        return number_list


    def generate_continuous_number_list(self):
        '''
        Generate a number of Number objects with values in a range, specified in config
        '''
        lowerbound = self.opt.set_range_min
        upperbound = self.opt.set_range_max
        if lowerbound < 2:
            lowerbound = 2
        number_list = []
        for value in range(lowerbound, upperbound + 1):
            if pp.isprime(value) and not self.opt.set_include_primes:
                continue
            number = Number(value)
            number_list.append(number)
        return number_list

    def generate_number_families(self):
        '''
        Generate a list of Number objects
        from the family definitions specified in config
        '''
        number_list = []
        for family in self.opt.set_families:
            family_product = int(np.prod(family))
            if self.opt.set_identity_factor_mode == 'count':
                if self.opt.set_identity_factor_minimum_mode == 'family':
                    largest_family_factor = family[-1]
                    identity_prime_generator = pp.primes_above(largest_family_factor)
                    first_identity_factor = next(identity_prime_generator)
                elif self.opt.set_identity_factor_minimum_mode == 'origin':
                    first_identity_factor = 2
                    identity_prime_generator = pp.primes_above(first_identity_factor)
                else:
                    first_identity_factor = self.opt.set_identity_factor_minimum_value
                    identity_prime_generator = pp.primes_above(first_identity_factor)
                number_of_families = self.opt.set_identity_factor_count
            else:
                first_identity_factor = self.opt.set_identity_factor_range_min
                number_of_families = pp.prime_count(self.opt.set_identity_factor_range_max) - pp.prime_count(self.opt.set_identity_factor_range_min)
                identity_prime_generator = pp.primes_above(first_identity_factor)

            number_list.append(Number(family_product * first_identity_factor))
            for count in range(number_of_families):
                next_identity_factor = next(identity_prime_generator)
                number_list.append(Number(family_product * next_identity_factor))
            
        return number_list

    def read_data_from_file(self):
        file_name = self.opt.set_csv_file_name
        try:
            with open(file_name, mode='w') as file:
                df = pd.read_csv(file)
        except Exception as e:
            self.logger.error(f'Could not read csv input file: {e}')
            raise e
        pass
        return df

    def create_dataframe(self, number_list: List[Number]):
        # prep dictionary
        data_dict = {}
        data_dict['number'] = []
        if self.opt.set_include_primes:
            data_dict['is_prime'] = []
        data_dict['prime_factors'] = []
        data_dict['ideal'] = []
        data_dict['deviation'] = []
        data_dict['anti_slope'] = []
        data_dict['family_factors'] = []
        data_dict['identity_factor'] = []
        data_dict['family'] = []

        # fill in dictionary
        for number in number_list:
            data_dict['number'].append(number.value)
            if self.opt.set_include_primes:
                data_dict['is_prime'].append(
                    'true' if number.is_prime else 'false')
            data_dict['prime_factors'].append(
                self.int_list_to_str(number.prime_factors))
            data_dict['ideal'].append(number.ideal_factor)
            data_dict['deviation'].append(number.mean_deviation)
            data_dict['anti_slope'].append(number.anti_slope)
            if number.value == 1:
                data_dict['family_factors'].append(0)
                data_dict['identity_factor'].append(0)
                data_dict['factor_family'].append(1)
            else:
                data_dict['family_factors'].append(number.prime_factors[:-1])
                data_dict['identity_factor'].append(number.prime_factors[-1])
                data_dict['family'].append(int(np.prod(number.prime_factors[:-1])))

        df = pd.DataFrame(data_dict)
        df.reset_index()
        self.logger.debug(f'Data collated')

        return df


    def create_graph(self, df):
        print('NYI')


    def get_primes_between(self, previous: int, total_count: int):
        primes = []
        prime_generator = pp.primes_above(previous)
        for count in range(total_count):
            primes.append(next(prime_generator))
        return primes

    def int_list_to_str(self, number_list: List[int], separator=', ', use_bookends=True, bookends=['[ ', ' ]']):
        '''
        Generate a string from a list of integers
        '''

        stringified_list = []
        for number in number_list:
            stringified_list.append(str(number))
        list_string = separator.join(stringified_list)
        if use_bookends:
            return bookends[0] + list_string + bookends[1]
        else:
            return list_string

class Options(object):
    def __init__(self):
        pass

    def __setattr__(self, key, value):
        self.__dict__[key] = value
    
    def set(self, key, value):
        self.__dict__[key] = value

class SettingsParser():
    def __init__(self, config_file='config.ini') -> None:
        self.config_file = config_file
        self.config = ConfigParser()
        # DBG START
        self.logger_mode = None
        self.logger_file_name_string = None
        self.logger_base_folder = None
        self.logger_reset_files = None
        self.logger_format = None
        self.logger_level = None
        self.set_mode = None
        self.set_families = None
        self.set_identity_factor_mode = None
        self.set_identity_factor_range_min = None
        self.set_identity_factor_range_max = None
        self.set_identity_factor_minimum_mode = None
        self.set_identity_factor_minimum_value = None
        self.set_identity_factor_count = None
        self.set_include_primes = None
        self.set_range_min = None
        self.set_range_max = None
        self.set_csv_file_name = None
        self.graph_width = None
        self.graph_height = None
        self.graph_point_size = None
        self.graph_mode = None
        self.graph_use_color_buckets = None
        self.graph_palette = None
        self.run_create_csv = None
        self.run_hard_copy_timestamp_granularity = None
        self.run_reset_output_data = None
        # DBG END
        self._read_settings(self.config_file)

    def _set(self, key, value):
        self.__dict__[key] = value

    def _read_settings(self, config_file='config.ini'):
        if not config_file:
            config_file = self.config_file
        self.config.read(self.config_file)
        for section in self.config.sections():
            section_name = f'{section}_'
            for option in self.config.options(section):
                option_name = section_name + option
                self._set(option_name, self.parse(section, option))

    def get_settings(self):
        return self

    def parse(self, section: str, parameter: str):
        # parse the settings according to their type
        string_value = self.config.get(section, parameter)

        # try float
        float_string = re.search('^[0-9]+\.[0-9]+$', string_value)
        if float_string:
            return float(float_string[0])

        # try int
        int_string = re.search('^[0-9]+$', string_value)
        if int_string:
            return int(int_string[0])

        # try bool
        bool_string = re.search('^(true|false)$', string_value)
        if bool_string:
            return True if bool_string[0] == 'true' else False

        # try int array
        array_string = re.search('^(\[|\]|\d|,|\s)+$', string_value)
        if array_string:
            return json.loads(array_string[0])

        # return string for all other cases
        return string_value
