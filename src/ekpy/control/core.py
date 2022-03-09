import pandas as pd
import numpy as np
import time
import itertools
import warnings
import pyvisa
import os
from IPython import display

from .misc import get_save_name
from ..utils import write_ekpy_data

__all__ = ('trial','experiment')

class experiment():
	
	def __init__(self, run_function):
		"""
		Experiment class. Used to run experiments (see n_param_scan), generate data files, and generate meta data. One must specify a run function that returns `((str) base_name, (dict) meta_data, (pandas.dataframe) data)`. One must also supply a terminate function. It is suggested that one overwrites the checks() method as well.

		args:
			run_function (callable): A function that returns ((str) base_name, (dict) meta_data, (pandas.dataframe) data)

		examples:

			Create an experiment that uses a lockin (SRS830) to measure X and Y.

			.. code-block:: python

				from ekpy.control.instruments import srs830
				from ekpy.control import experiment

				# allow for arbitrary meta data to be passed directly into run_function as kwargs
				def run_function(lockin:'pyvisa.resources.gpib.GPIBInstrument', **meta_data):
				    base_name = 'trial'# a base name that will be saved. File names will be saved according to base_name_TRIALCOUNT, where TRIALCOUNT counts from 0 automatically
				    X, Y = srs830.get_X_Y(lockin) # get the data
				    data = pd.DataFrame({'X':[X],'Y':[Y]}) # put data in dataframe
				    return base_name, meta_data, data

				# subclass experiment for our use case
				class EXP(experiment):
				    
				    def __init__(self, run_function=run_function):
				        super().__init__(run_function)
				        
				    def terminate(self,):
				        pass
				    
				    
				exp = EXP()
				exp.config_path('./')

				### The following is how we pass arguments to run_function
				# parameters we wish to scan over, in this case, NONE
				scan_params = {}
				fixed_params = {'lockin':lockin, 'param1':1} # need to pass the lockin to run_function and any additional meta data, here I'm making up a parameter 'param1'
				order = [] #if we were scanning over parameters, we would need to specify the order here, which one to scan over first etc.

				# do a scan
				exp.n_param_scan(scan_params, fixed_params, order)

				# this will create a file called trial_0.csv


			Working with checks, and terminate functions. To access instruments in terminate, you will want to pass the instrument to the class (not just the run function):

			.. code-block:: python

				class EXP(experiment):
				    
				    def __init__(self, lockin, run_function=run_function):
				        super().__init__(run_function)
				        self.lockin=lockin # initialize here so we have access to it in terminate and or other internal functions

					def checks(self, params):
						if params['lockin']!=self.lockin:
							# make sure the lockin passed to the run_function (through n_param_scan) is the same as that which is initialized here 
							raise ValueError('lockin specified in run_function argument is not the same as when initializing the experiment')
				        
				    def terminate(self,):
				    	# set the internal amplitude to minimum
				        srs830.set_internal_amplitude(self.lockin, 0.004)

		"""
		self.run_function = run_function
		return

	def __repr__(self):
		out = self.__dict__.copy()
		try:
			out.update({'run_function':self.run_function.__name__})
		except:
			pass

		for key in out:
			#print out the actual instruments if we can
			obj = out[key]
			if type(obj) == pyvisa.resources.gpib.GPIBInstrument:
				try:
					out.update({key:obj.query("*idn?")})
				except:
					pass
		return out.__repr__()

	def __str__(self):
		return self.__repr__()

	def show_run_function_help(self):
		"""Return help (used to view docstring/call args etc.) for `self.run_function`.

		returns:
			(help): Help on `self.run_function`

		"""
		return help(self.run_function)

	def config_path(self, path, directory_delimiter='/'):
		"""Config the path to save data. If path does not exist, user will be prompted to create. 

		args:
			path (str): Path
			directory_delimiter (str): Delimiter between directories in path. Sometimes it may be '\\' for Windows OS, for example.

		"""
		if path[-1] != directory_delimiter:
			raise ValueError('must specify a directory. "{}" does not specify a directory'.format(path))

		success = False
		original_path = path

		try:
			os.listdir(path)
			yn = 'n'
		except FileNotFoundError:
			yn = input("Path '{}' does not exist. Do you wish to create it? (y/n)".format(path))
			yn = yn.lower()

		if yn == 'y':
			to_create = []

			while success == False:
				try:
					os.listdir(path)
					success = True
				except FileNotFoundError:
					path_spl = path.split(directory_delimiter)
					to_create.append(path_spl[-2])
					path = ''
					for spl in path_spl[:-2]:
						path+=spl + '/'

			to_create = to_create[::-1]
			for directory in to_create:
				os.mkdir(path + directory + directory_delimiter)
				path += directory + directory_delimiter
				print('creating dir "{}"'.format(path))
				
		else:
			pass
		self.path = path

	def checks(self, params):
		"""Method to perform a set of checks on params before starting a scan. Default is simple pass."""
		pass

	def terminate(self):
		"""Placeholder method for termination. This method should be overriden. 

		example:
			Example of overriding the terminate method to perform a set of actions upon erroring/completion of `n_param_scan`.

			.. code-block:: python

				def terminate(self):
					# set the internal amplitude of the lockin to its lowest value
					srs.set_internal_amplitude(self.lockin, 0.0004)

		"""
		raise NotImplementedError('terminate() should be overridden in experiment subclass. It is not.')


	def _plot(self, data, scan_params):
		"""Method for plotting. This Method should be overwritten with details of how to create a plot if one wishes to plot the data as it is collected.

		args:
			data (pandas.DataFrame): Data from trial.
			scan_params (dict): Parameters of current scan

		example:
			Example of overriding the _plot method to plot a simple scatter plot each time

			.. code-block:: python

				from ekpmeasure.control import plotting
				import matplotlib.pyplot as plt

				def _plot(self, data, scan_params):
					if hasattr(self, 'fig') and hasattr(self, 'ax'):
						pass
					else:
						fig, ax = plt.subplots()
						self.fig = fig
						self.ax = ax
						
					self.ax.scatter(scan_params['frequency'], np.mean(data['R']), color = 'blue')
					plt.show(self.fig)
					plotting.update_plot(self.fig)

		"""
		raise NotImplementedError('_plot() should be overridden in experiment subclass. It is not.')


	def n_param_scan(self, kw_scan_params, fixed_params, scan_param_order, ntrials=1, print_progress=True, plot=False):
		"""Perform a measurement over a set of params and save the data/meta data. 

		args:
			kw_scan_params (dict): Parameters to scan.
			fixed_params (dict): Parameters to keep fixed.
			scan_param_order (array-like): Order of scan parameters. 
			ntrials (int): Number of trials to perform.
			plot (bool): Plot as data is collected.


		Examples:
			
			>>> exp = experiment()
			>>>	kw_scan_params = {
					'frequency':['147hz', '47hz'],
					'amplitude':['50ua','100ua', '250ua', '500ua', '750ua', '850ua','1000ua',],
					'harmonic':[1,2]
				}

			>>>	fixed_params = {
					'lockin':lockin,
					'current_source':current_source,
					'identifier':'D0',
					'angle':20,
					'channel_width':2,
					'channel_length':20,
					'bar_width':1.5,
					'nave':5,
					'delay':'default', 
					'time_constant':'3s',
					'sensitivity':'10uv/pa',
				}

			>>> order = ['harmonic', 'frequency', 'amplitude']
			#Perform scan
			>>> exp.n_param_scan(kw_scan_params, fixed_params, order)
			


		"""
		#check to make sure no errors
		params = kw_scan_params.copy()
		params.update(fixed_params)
		self.checks(params)

		if not hasattr(self, 'terminate'):
			raise NotImplementedError('no terminate function specified')
		if not hasattr(self, 'run_function'):
			raise AttributeError('run_function not yet defined.')
		if not hasattr(self, 'path'):
			raise AttributeError('no save path defined.')
			
		if set(scan_param_order) != set(kw_scan_params.keys()):
			raise KeyError('kw_scan_params do not have the same keys as scan_param_order')
		try:
			total_scans = int(np.prod([len(kw_scan_params[x]) for x in kw_scan_params])*ntrials)
			iteration = 0
			for key in kw_scan_params:
				params = kw_scan_params[key]
				if hasattr(params, '__getitem__') and type(params) != str:
					pass
				else:
					raise TypeError('kw_scan_param: {} must be array-like of params. it is not.'.format(key))
					
			iterable_param_list = list(
				itertools.product(
					*(kw_scan_params[key] for key in scan_param_order[::-1])
				)
			)
			
			for params in iterable_param_list:
				kwargs = fixed_params
				current_scan_params = {} # just the scanning params
				for i, key in enumerate(scan_param_order[::-1]):
					kwargs.update({key:params[i]})
					current_scan_params.update({key:params[i]})
				for count in range(ntrials):
					iteration += 1
					print('Scan {} of {}. {}'.format(iteration, total_scans, current_scan_params))
					
					trial_df = trial(self.run_function, kwargs, self.path, return_df = True)
					if plot:
						self._plot(trial_df, kwargs)
					else:
						display.clear_output(wait = True)
					time.sleep(1)

			return 

		except Exception as e:
			print('terminating.')
			raise e
		finally:
			self.terminate()
			print('done.')
		

def trial(run_function, run_function_args, path, return_df=False, save_meta_data_pickle=True):
	"""
	A trial for an experiment. This will save each trial (as csv) to path with a unique name (indexed by trial if an identical basename already exists). Also creates and saves meta data to path. The specified run_function must return ((str) base_name, (dict) meta_data, (pandas.dataframe) data).

	args:
		run_function (function): A run_function that returns:
			```
			((str) base_name, (dict) meta_data, (pandas.dataframe) data)
			```
		run_function_args (dict): Dict of arguments for the specified run_function
		path (str): Save location.
		return_df (bool): Return the resulting data (pandas.DataFrame)
		save_meta_data_csv (bool): Save the meta_data as a pickle file in addition to .csv. This is carry over from a legacy version.
	


	"""
	base_name, meta_data, df = run_function(**run_function_args)
	try:
		save_name = get_save_name(base_name, path)
		trial = int(save_name.split('_')[-1].replace('.csv',''))
	except Exception as e:
		save_name = input('there was an error generating a save name: {}\n please enter a unique name'.format(e))
		trial = np.nan


	meta_data.update({'trial':trial, 'filename':save_name})

	assert type(df) == type(pd.DataFrame()), 'run_function {} does not return a pandas.DataFrame as its third return argument, it must'.format(run_function.__name__)

	try:
		write_ekpy_data(path+save_name, df, meta_data)
	except:
		# fall back to to_csv
		df.to_csv(path+save_name, index=False)

	#update the meta_data file in this directory
	meta_data = pd.DataFrame(meta_data, index = [0])
	try:
		existing_meta_data = pd.read_csv(path+'meta_data.csv')
		if set(meta_data.columns) != set(existing_meta_data.columns):
			raise ValueError('the columns of meta_data do not match the existing columns of the data in this path ({}). Please ensure you are producing data of the same type, or move to a new path. Please note, your data was saved with file complete filename: {}, but it was not added to meta_data'.format(path, path+save_name))
		out = pd.concat([existing_meta_data, meta_data], ignore_index = True)
	except FileNotFoundError:
		out = meta_data.copy()

	out.to_csv(path + 'meta_data.csv', index = False)
	if save_meta_data_pickle:
		out.to_pickle(path + 'meta_data')
	if return_df:
		return df