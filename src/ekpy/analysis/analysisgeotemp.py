'''
Not sure if I should add this to the core class or leave it here for now. Since I am modifiying erics code directly, would rather have it in a seperate file to differentiate it before i merge it

ACTS ON EKPY.DATA NOT DSET 
'''
from inspect import getmembers, isfunction
from importlib import import_module
def use_analysis_file(module, data, saveall=False, path=None):
    """
    Reads correctly formatted analysis file and performs all functions in sequential order and returns the final mutated Data.

    Args:
        module (str): the name of the analysis file which must be in the same directory.
        data (ekpy.data): The data to use the analysis file on.
        saveall (Boolean): If set to true it saves each intermediate step to a file
        path (str): if savell is true you must set a path where to save the intermediate steps. Usually the path where you pulled the dset from.

    Returns:
        data (ekpy.data): The modified data.
        data_saver (dict): A Dictionary containing all the intermediate steps of the data. (optional)
    """
    module = import_module(module)
    functions_list = module.__all__
    data_saver = {'data0': data,}
    for i, name in enumerate(functions_list):
        func = getattr(module, name)
        key_name = f"data{i + 1}"
        data_saver[key_name] = data.apply(func)
        data = data_saver[key_name]
    if saveall:
        for keys in data_saver:
            data_saver[keys].to_ekpdat(path + f"/data_saver/{keys}.ekpds")
        return data, data_saver
    else:
        return data

    
        





