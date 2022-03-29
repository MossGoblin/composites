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
    def __init__(self, logger, options) -> None:
        self.logger = logger
        self.opt = options


    def generate_number_list(self):
        self.logger.info('Generating numbers')
        if self.opt.set_mode == 'family':
            self.logger.debug('Processing families')
            self.generate_number_families()
        elif self.opt.set_mode == 'range':
            self.logger.debug('Processing range')
        else:
            self.logger.debug('Processing file')
        print('NYI')


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

    def generate_number_families(self):
        processed_numbers = []
        for family in self.opt.set_families:
            family_product = np.prod(family)
            identity_factors = []
            # HERE
            if self.opt.set_identity_factor_mode == 'count':
                if self.opt.set_identity_factor_minimum_mode == 'family':
                    largest_family_factor = family[-1]
                    larger_primes = pp.primes_above(largest_family_factor)
                    first_identity_factor = next(larger_primes)
                elif self.opt.set_identity_factor_minimum_mode == 'origin':
                    first_identity_factor = 2
                else:
                    first_identity_factor = self.opt.set_identity_factor_minimum_value
                number_of_families = self.opt.set_identity_factor_count
            else:
                first_identity_factor = self.opt.set_identity_factor_range_min
                number_of_families = pp.prime_count(self.opt.set_identity_factor_range_max) - pp.prime_count(self.opt.set_identity_factor_range_min)

            # if include_all_identities:
            #     identity_factors_lower_bound = family[-1]
            # else:
            #     identity_factors_lower_bound = 2
            # identity_factors.extend(self.get_primes_between(
            #     identity_factors_lower_bound, family_count-1))
            # for identity_factor in identity_factors:
            #     number_value = int(family_product) * identity_factor
            #     try:
            #         number = Number(number_value)
            #     except Exception as e:
            #         print(number_value)
            #         raise e
            #     processed_numbers.append(number)
        return processed_numbers

    def get_primes_between(self, previous: int, total_count: int):
        primes = []
        prime_generator = pp.primes_above(previous)
        for count in range(total_count):
            primes.append(next(prime_generator))
        return primes

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
