from configparser import ConfigParser
import json
import math
from typing import List
import pyprimes as pp
import numpy as np
import re


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
    def __init__(self) -> None:
        pass

    def generate_continuous_number_list(self, lowerbound: int, upperbound: int, include_primes: bool):
        lowerbound = lowerbound
        upperbound = upperbound
        if lowerbound < 2:
            lowerbound = 2
        number_list = []
        for value in range(lowerbound, upperbound + 1):
            if pp.isprime(value) and not include_primes:
                continue
            number = Number(value=value)
            number_list.append(number)
        return number_list

    def generate_number_families(self, families: List, include_all_identities: bool, family_count):
        processed_numbers = []
        for family in families:
            family_product = np.prod(family)
            identity_factors = []
            if include_all_identities:
                identity_factors_lower_bound = family[-1]
            else:
                identity_factors_lower_bound = 2
            identity_factors.extend(self.get_primes_between(
                identity_factors_lower_bound, family_count-1))
            for identity_factor in identity_factors:
                number_value = int(family_product) * identity_factor
                try:
                    number = Number(number_value)
                except Exception as e:
                    print(number_value)
                    raise e
                processed_numbers.append(number)
        return processed_numbers

    def get_primes_between(self, previous: int, total_count: int):
        primes = []
        prime_generator = pp.primes_above(previous)
        for count in range(total_count):
            primes.append(next(prime_generator))
        return primes


class SettingsParser():
    def __init__(self, config_file='config.ini') -> None:
        self.config_file = config_file
        self.config = ConfigParser()
        self.settings = self.read_settings(self.config_file)

    def read_settings(self, config_file='config.ini'):
        settings = {}
        if not config_file:
            config_file = self.config_file
        self.config.read(self.config_file)

        # Logger settings
        settings['log_mode'] = self.parse('logger', 'log_mode')
        settings['log_file_name_string'] = self.parse(
            'logger', 'log_file_name_string')
        settings['reset_log_files'] = self.parse('logger', 'reset_log_files')
        settings['logger_format'] = self.parse('logger', 'logger_format')
        settings['logger_level'] = self.parse('logger', 'logger_level')
        settings['logging_base_folder'] = self.parse('logger', 'logging_base_folder')

        # Number set settings
        settings['number_input_mode'] = self.parse(
            'numbers', 'number_input_mode')
        settings['mode'] = self.parse('numbers', 'mode')
        settings['families'] = self.parse('numbers', 'families')
        settings['identity_factor_range_min'] = self.parse(
            'numbers', 'identity_factor_range_min')
        settings['identity_factor_range_max'] = self.parse(
            'numbers', 'identity_factor_range_max')
        settings['identity_factor_mode'] = self.parse(
            'numbers', 'identity_factor_mode')
        settings['identity_factor_maximum'] = self.parse(
            'numbers', 'identity_factor_maximum')
        settings['identity_factor_minimum_mode'] = self.parse(
            'numbers', 'identity_factor_minimum_mode')
        settings['include_primes'] = self.parse('numbers', 'include_primes')
        settings['range_min'] = self.parse('numbers', 'range_min')
        settings['range_max'] = self.parse('numbers', 'range_max')

        # Run parameters
        settings['create_csv'] = self.parse('run', 'create_csv')
        settings['hard_copy_timestamp_granularity'] = self.parse(
            'run', 'hard_copy_timestamp_granularity')
        settings['reset_output_data'] = self.parse('run', 'reset_output_data')

        # graph parameters
        settings['width'] = self.parse('graph', 'width')
        settings['height'] = self.parse('graph', 'height')
        settings['point_size'] = self.parse('graph', 'point_size')
        settings['mode'] = self.parse('graph', 'mode')
        settings['use_color_buckets'] = self.parse(
            'graph', 'use_color_buckets')
        settings['palette'] = self.parse('graph', 'palette')
        
        return settings

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

    def get_settings(self):
        return self.settings
