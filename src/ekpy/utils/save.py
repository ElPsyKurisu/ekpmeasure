import os
import pandas as pd

__all__ = ('write_ekpy_data', 'read_ekpy_data')


def write_ekpy_data(fname:str, data:'pandas.DataFrame', meta_data:dict):
	"""Write and ekpy data file. This will have the meta data as a header at the top.

	args:
		fname (str): File name
		data (pandas.DataFrame): Data
		meta_data (dict): Meta data

	"""
	header = 'ekpy_heading{}'.format(os.linesep)
	for key in meta_data:
		header+='{}:::{}{}'.format(key, meta_data[key], os.linesep)
	header+='ekpy_heading_complete{}'.format(os.linesep)    

	data_to_write=data.to_csv(index=False)
	to_write=(header+data_to_write).replace('\r\n', '\n')
	with open(fname, 'w', newline=os.linesep) as f:
		f.write(to_write)
	return

def read_ekpy_data(file:str, return_meta_data=False):
	"""Read ekpy data file. If no ekpy heading exists ('ekpy_heading') defaults to `pandas.read_csv'

	args:
		file (str): File name
		return_meta_data (bool): Whether to return the associated meta data (heading) or just return the data

	returns:
		(pandas.DataFrame) : Data
		(pandas.DataFrame, dict): (Data, Meta Data)
	"""
	with open(file, 'r') as f:
		lines = f.readlines()
	index=len(lines)+1
	for i, line in enumerate(lines):
		if i == 0 and 'ekpy_heading' not in line:
			break
		if 'ekpy_heading_complete' not in line:
			continue
		else:
			index=i

	if index>len(lines):
		if return_meta_data:
			raise ValueError('Failed to find end of ekpy heading. Considering trying again with return_meta_data set to False?')
		else:
			return pd.read_csv(file)
		
	if not return_meta_data:
		return pd.read_csv(file, skip_blank_lines=True, skiprows=index+1)
	
	else:
		return pd.read_csv(file, skip_blank_lines=True, skiprows=index+1), _parse_ekpy_meta_data(lines)

def _parse_ekpy_meta_data(lines:list):
	"""Parse ekpy_heading."""
	meta_data = {}
	for line in lines:
		if 'ekpy_heading_complete' in line:
			break
		if 'ekpy_heading' in line:
			continue
		if line == '\n' or line == '\r' or line == '\r\n':
			continue
		spl=line.replace('\n', '').replace('\r', '').split(':::')
		meta_data.update({spl[0]:spl[1]})
	return meta_data