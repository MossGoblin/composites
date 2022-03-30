from configparser import ConfigParser
from datetime import datetime
import json
import math
import os
from typing import Dict, List
import pyprimes as pp
import numpy as np
import re
import pandas as pd

from bokeh.models import ColumnDataSource, CategoricalColorMapper
from bokeh.plotting import figure, show
from bokeh import models as models

import labels


class ToolBox():
    def __init__(self, options) -> None:
        self.opt = options

    def set_logger(self, logger):
        self.logger = logger

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
        for number in range(lowerbound, upperbound + 1):
            if pp.isprime(number) and not self.opt.set_include_primes:
                continue
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
                    if not pp.isprime(first_identity_factor):
                        first_identity_factor = next(identity_prime_generator)
                number_of_families = self.opt.set_identity_factor_count
            else:
                first_identity_factor = self.opt.set_identity_factor_range_min
                number_of_families = pp.prime_count(self.opt.set_identity_factor_range_max) - pp.prime_count(self.opt.set_identity_factor_range_min)
                identity_prime_generator = pp.primes_above(first_identity_factor)

            number_list.append(family_product * first_identity_factor)
            for count in range(number_of_families - 1):
                next_identity_factor = next(identity_prime_generator)
                number_list.append(family_product * next_identity_factor)
            
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

        def get_ideal_factor(number: int, factors) -> float:
            return math.pow(number, 1/len(factors))

        def get_mean_deviation(prime_factors: List[int], ideal_factor: float) -> float:
            deviations_sum = 0
            for prime_factor in prime_factors:
                deviations_sum += abs(prime_factor - ideal_factor)
            mean_deviation = deviations_sum / len(prime_factors)
            return mean_deviation

        def get_antisplope(number, mean_deviation):
            if mean_deviation > 0:
                return number / mean_deviation
            else:
                return 0

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
        data_dict['family_product'] = []

        # fill in dictionary
        for number in number_list:
            data_dict['number'].append(number)
            if self.opt.set_include_primes:
                data_dict['is_prime'].append(
                    'true' if pp.isprime(number) else 'false')
            factors = pp.factors(number)
            data_dict['prime_factors'].append(
                self.int_list_to_str(factors))
            ideal_factor = get_ideal_factor(number, factors)
            data_dict['ideal'].append(ideal_factor)
            mean_deviation = get_mean_deviation(factors, ideal_factor)
            data_dict['deviation'].append(mean_deviation)
            anti_slope = get_antisplope(number, mean_deviation)
            data_dict['anti_slope'].append(anti_slope)
            if number == 1:
                data_dict['family_factors'].append(0)
                data_dict['identity_factor'].append(0)
                data_dict['family_product'].append(1)
            else:
                data_dict['family_factors'].append(factors[:-1])
                data_dict['identity_factor'].append(factors[-1])
                data_dict['family_product'].append(int(np.prod(factors[:-1])))

        df = pd.DataFrame(data_dict)
        df.reset_index()
        self.logger.debug(f'Data collated')

        return df


    def plot_data(self, df):
        data = ColumnDataSource(data=df)

        # [x] create plot
        plot_width = self.opt.graph_width
        plot_height = self.opt.graph_height
        primes_included_text = " Primes included" if self.opt.set_include_primes else " Primes excluded"

        graph_params = {}
        graph_params['title'] = 'LOREM IPSUM'
        graph_params['y_axis_label'] = labels.y_axis_label[self.opt.graph_mode]
        graph_params['width'] = plot_width
        graph_params['height'] = plot_height

        graph = self.get_figure(graph_params)

        # [x] add hover tool
        tooltips = [('number', '@number')]
        if self.opt.set_include_primes:
            tooltips.append(('prime', '@is_prime'))
        tooltips.extend([('factors', '@prime_factors'),
                        ('ideal factor value', '@ideal'),
                        ('mean factor deviation', '@deviation'),
                        ('anti-slope', '@anti_slope'),
                        ('family factors', '@family_factors'),
                        ('identity factor', '@identity_factor'),
                        ('family product', '@family_product'),
                         ])

        hover = models.HoverTool(tooltips=tooltips)
        graph.add_tools(hover)

        # [x] add graph
        graph_point_size = int(self.opt.graph_point_size)

        graph_params['type'] = 'scatter'
        graph_params['y_value'] = labels.y_axis_values[self.opt.graph_mode]
        graph_params['graph_point_size'] = graph_point_size
        graph_params['palette'] = self.opt.graph_palette

        graph, coloring = self.create_graph(graph, data, graph_params)

        # [x] 'hard copy'
        graph_mode_chunk = labels.graph_mode_filename_chunk[self.opt.graph_mode]
        timestamp_format = self.generate_timestamp()
        timestamp = datetime.utcnow().strftime(timestamp_format)
        primes_included = 'primes' if self.opt.set_include_primes else 'no_primes'
        # hard_copy_filename = str(self.cfg.lowerbound) + '_' + str(self.cfg.upperbound) + \
        #     '_' + graph_mode_chunk + '_' + primes_included + '_' + coloring + '_' + timestamp
        hard_copy_filename = 'PLACEHOLDER_NAME'
        csv_output_folder = 'output'
        if self.opt.run_create_csv:
            full_hard_copy_filename = hard_copy_filename + '.csv'
            path = csv_output_folder + '\\'
            self.prep_folder(csv_output_folder, self.opt.run_reset_output_data)
            df.to_csv(path + full_hard_copy_filename)
            self.logger.info(f'Data saved as output\{full_hard_copy_filename}')

        # [x] show
        self.logger.info('Graph generated')
        show(graph)

        self.stash_graph_html(csv_output_folder, hard_copy_filename)

    def generate_timestamp(self):
        '''
        Generate timestamp string, depending on the desired granularity, set in the config file
        '''

        timestamp_format = ''
        timestamp_granularity = self.opt.run_hard_copy_timestamp_granularity
        format_chunks = ['%d%m%Y', '_%H', '%M', '%S']
        for chunk_index in range(timestamp_granularity + 1):
            timestamp_format += format_chunks[chunk_index]
        return timestamp_format

    def stash_graph_html(self, csv_output_folder, graph_filename: str):
        full_stashed_filename = csv_output_folder + '\\' + graph_filename + '.html'
        with open('main.html', 'r') as html_output_file:
            content = html_output_file.read()
            with open(full_stashed_filename, 'wt') as stashed_html_output_file:
                stashed_html_output_file.write(content)
        self.logger.info(f'Graph saved as {full_stashed_filename}')

    def create_graph(self, graph: figure, data: ColumnDataSource, graph_params: Dict) -> figure:
        '''
        Creates a scatter plot by given parameters
        '''

        coloring = ''
        y_value = graph_params['y_value']
        graph_point_size = graph_params['graph_point_size']
        palette = graph_params['palette']

        base_color = '#3030ff'
        graph.scatter(source=data, x='number', y=y_value, color=base_color, size=graph_point_size)
        coloring = 'monocolor'

        return graph, coloring


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

    def get_figure(self, params: Dict) -> figure:
        '''
        Returns a figure with the provided parameters
        '''
        title = params['title']
        y_axis_label = params['y_axis_label']
        width = params['width']
        height = params['height']

        return figure(title=title, x_axis_label='number', y_axis_label=y_axis_label, width=width, height=height)

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
