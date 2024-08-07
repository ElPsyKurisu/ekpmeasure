'''
Not sure if I should add this to the core class or leave it here for now. Since I am modifiying erics code directly, would rather have it in a seperate file to differentiate it before i merge it

ACTS ON EKPY.DATA NOT DSET 
'''
from inspect import getmembers, isfunction, getdoc
from importlib import import_module
from ekpy.analysis.core import Data, Dataset
import os
import pandas as pd
from ekpy.analysis.plotting import lane_martin
import matplotlib.pyplot as plt
import numpy as np

def use_analysis_file(module, data, saveall=False, path=None, skip_func=None, verbose=False, dont_pass_defn=False):
    """
    Reads correctly formatted analysis file and performs all functions in sequential order and returns the final mutated Data. Only want it to return the final
    mutated data alongside the original unless saveall=True

    So because of overriding cases where a func overrides something by say data_dict['voltage'] = new_voltage but data_dict['voltage'] already existed we
    have data saver to save the day!

    Adding functionality to accept data or dataset (so can do multiple runs)

    Args:
        module (str): the name of the analysis file which must be in the same directory.
        data (ekpy.data or ekpy.dataset): The data to use the analysis file on. if dataset then it modifies all of them
        saveall (Boolean): If set to true it saves each intermediate step to a file
        path (str): if savell is true you must set a path where to save the intermediate steps. Usually the path where you pulled the dset from.
        skip_func (str or list of str): The name of the functions to list, if skip_func is not defined in the analysis file it is simply not skipped and
        a warning appears
        verbose (Boolean): If set to true attempts to plot each step of the data analysis pathway
        dont_pass_defn (Boolean): Functions that do not use kwargs or defintion can pass this so you dont need to add kwargs (for legacy reasons)

    Returns:
        data (ekpy.data or ekpy.dataset): The modified data or dataset.
        data_saver (dict): A Dictionary containing all the intermediate steps of the data. (optional)
    """
    module = import_module(module)
    functions_list = list(module.__all__)
    if skip_func is not None:
        if skip_func is not list:
            t = []
            t.append(skip_func)
            skip_func = t
        for func in skip_func:
            try:
                functions_list.remove(func)
            except ValueError:
                print(f'Did not skip as skip_func: {func} does not exist, perhaps the spelling is wrong')
    #add functionaility to allow for datasets
    if type(data) is Dataset:
        data = data.get_data()
    data_saver = {'data0': data,}
    funcs_modified = ['original',]
    plotted_against_list = [None, ]
    skip_plot_list = [False, ]
    for i, name in enumerate(functions_list):
        func = getattr(module, name)
        if dont_pass_defn:
            check_if_func_nonetype = data.apply(func, pass_defn=False)
        else:
            check_if_func_nonetype = data.apply(func, pass_defn=True)
        if check_if_func_nonetype is None:
            continue
        func_doc_str = getdoc(func)
        func_appended, plotted_against, skip_plot = get_function_doc_append(func_doc_str)
        funcs_modified.append(func_appended)
        skip_plot_list.append(skip_plot)
        plotted_against_list.append(plotted_against)
        key_name = f"data{i + 1}"
        data_saver[key_name] = check_if_func_nonetype
        data = data_saver[key_name]
    original_data = data_saver['data0'].to_dict()
    last_data_added = data[data.data_keys[-1]]
    if type(last_data_added) is dict:
        for key in original_data.keys():
            original_data[key]['data'][data.data_keys[-1]] = last_data_added[key]
    else:
        original_data[0]['data'][data.data_keys[-1]] = last_data_added 
    data_out = Data(original_data)

    if verbose:
        functions_list.insert(0, "Unmodified")
        verbose_helper(data_saver, funcs_modified, plotted_against_list, functions_list, skip_plot_list)

    if saveall:
        if path is None:
            print("Warning creating a directory since a path was not given")
            path = './'
        path = path + '/data_saver0'
        iterator = 1
        while os.path.exists(path):
            if iterator > 1000:
                raise ValueError("Dog make a new directory. you have over 1000 folders here or something messed up")
            path = list(path)
            path[-1] = str(iterator)
            path = "".join(path)
            iterator += 1
        os.mkdir(path)
        print("Folder %s created!" % path)
        meta_data_saver = Data({0: {'definition':0, 'data': {'funcs_modified': np.array(funcs_modified, dtype=str), 'plotted_against': np.array(plotted_against_list)}}})
        meta_data_saver.to_ekpdat(path + '/saver.ekpdat')
        for keys in data_saver:
            data_saver[keys].to_ekpdat(path +f'\\{keys}'+'.ekpdat')
    return data_out, data_saver

    




def get_function_doc_append(doc_string):
    """
    Helper function which takes in an appropiately formatted string and scans it for the appended value. See use_analysis_file for more
    information. Note will error if it doesnt end with MODIFIES: func_name'' ' 

    Args:
        doc_string (str): The given doc_string to scan
    Returns:
        func_name_appended (str): The name of the function that was modified by the function
        plotted_against (str): The key that should be plotted against whatever was modified here, Returns None if not found
        skip_plot (boolean): Optional Flag that will suppress warnings if you have a function that doesn't need to show a plotting step
    """
    if doc_string.find("MODIFIES:") != -1:
        func_name_start = doc_string.find("MODIFIES:") + len("MODIFIES:")
        func_name_appended = doc_string[func_name_start:].strip() 
    else:
        func_name_appended = None
    if doc_string.find("PLOT_AGAINST:") != -1:
        plotted_against_start = doc_string.find("PLOT_AGAINST:") + len("PLOT_AGAINST:")
        plotted_against_end = doc_string[plotted_against_start:].find("\n")
        plotted_against = doc_string[plotted_against_start:plotted_against_start+plotted_against_end].strip()
    else:
        plotted_against = None
    if doc_string.find("SKIP_PLOT") != -1:
        skip_plot = True
    else:
        skip_plot = False

    return func_name_appended, plotted_against, skip_plot
    

def verbose_helper(data_saver, funcs_modified, plotted_against, functions_list, skip_plot_list):
    """
    Helper Function that takes in a dictionary of ekpds.Data and a list of functions that were modified and plots each one in accordance to
    specificaions

    Args:
        data_saver (dict): A dictionary of each intermediate step in the process
        funcs_modified (list): A list of what was modified each time in the process
        plotted_against (str): The key of what we want to plot everything against (the x axis)
        functions_list (list): List of the names of the functions applied to be used in the titles
    Returns:
        None
    """
    data_saver_list = list(data_saver.keys())
    for i, name in enumerate(data_saver_list):
        scatter = False
        data = data_saver[name] #we get the data starting with data0 the original data
        func_modified = funcs_modified[i]
        if func_modified == 'original':
            func_modified = data.data_keys[1]
        plot_against = plotted_against[i]
        if plot_against is None:
            plot_against = data.data_keys[0] #plots first element 

        if skip_plot_list[i]:
            continue

        if plot_against is None and func_modified is None:
            #this represents a function that doesnt change any data like a plotting function perhaps
            print(f'Skipped {name} since either the doc_string is incomplete or it returns nothing')
            continue #go past this one in the list changed from pass
        
        #check to make sure that the plot_against is the same length as func_modifed
        if type(data[plot_against]) is dict:
            if len(data[func_modified][0]) != len(data[plot_against][0]): #check if first element of dictionary (which refers to each trial?) doesnt work note type should be array
                indices = data[func_modified] #I need 2d array here
                plot_against = data.data_keys[0]
                func_modified = data.data_keys[1]
                scatter = True
        else:
            if len(data[func_modified]) != len(data[plot_against]):
                indices = np.array([data[func_modified]]) #this is numpy array for 1d case need to make 2d?
                plot_against = data.data_keys[0]
                func_modified = data.data_keys[1]
                scatter = True

        #Setup plt ax and style
        plt.style.use(lane_martin)
        fig, ax = plt.subplots()
        ax.set_title(f'Function Applied: {functions_list[i]}')
        ax.set_xlabel(plot_against)
        ax.set_ylabel(func_modified)
        try:
            data.plot(x=plot_against, y=func_modified, ax=ax, labelby='trial')
            if scatter:
                data.scatter(x=plot_against, y=func_modified, subset=indices, ax=ax)
        except ValueError:
            print("{} has a different len than {}. Please ensure this is intended behavior}".format(func_modified, plot_against))
        except IndexError:
            print("{} was skipped. Ensure this was not meant to be plotted".format(func_modified))


    
        





