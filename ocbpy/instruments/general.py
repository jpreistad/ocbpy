#!/usr/bin/env python
""" General loading routines for data files

Functions
-------------------------------------------------------------------------------
test_file(filename)
    Test to see whether file exists and is small enough to load
load_ascii_data(filename, hlines, kwargs)
    Load time-sorted ascii data file

"""
from __future__ import absolute_import, unicode_literals

import datetime as dt
import numpy as np
from os import path

import ocbpy
import ocbpy.ocb_time as ocbt

def test_file(filename):
    """Test to ensure the file is small enough to read in.  Python can only
    allocate 2GB of data without crashing

    Parameters
    ------------
    filename : (str)
        Filename to test

    Returns
    ---------
    good_flag : (bool)
        True if good, bad if false

    """

    if not path.isfile(filename):
        ocbpy.logger.warning("name provided is not a file")
        return False
    
    fsize = path.getsize(filename)

    if(fsize > 2.0e9):
        ocbpy.logger.warning("File size [{:.2f} GB > 2 GB]".format(fsize*1e-9))
        return False
    elif(fsize == 0):
        ocbpy.logger.warning("empty file [{:s}]".format(filename))
        return False

    return True

def load_ascii_data(filename, hlines, gft_kwargs=dict(), hsplit=None,
                    datetime_cols=list(), datetime_fmt=None, int_cols=list(),
                    str_cols=list(), max_str_length=50, header=list()):
    """ Load an ascii data file into a dict of numpy array. 

    Parameters
    ------------
    filename : (str)
        data file name
    hlines : (int)
        number of lines in header.  If zero, must include header.
    gft_kwargs : (dict)
        Dictionary holding optional keyword arguments for the numpy genfromtxt
        routine (default=dict())
    hsplit : (str, NoneType)
        character seperating data labels in header.  None splits on all
        whitespace characters. (default=None)
    datetime_cols : (list of ints)
        If there are date strings or values that should be converted to a
        datetime object, list them in order here. Not processed as floats.
        (default=[])
    datetime_fmt : (str or NoneType)
        Format needed to convert the datetime_cols entries into a datetime
        object.  Special formats permitted are: 'YEAR SOY', 'YYDDD', 'SOD'.
        'YEAR SOY' must be used together; 'YYDDD' indicates years since 1900 and
        day of year, and may be used with any time format; 'SOD' indicates
        seconds of day, and may be used with any date format (default=None)
    int_cols : (list of ints)
        Data that should be processed as integers, not floats. (default=[])
    str_cols : (list of ints)
        Data that should be processed as strings, not floats. (default=[])
    max_str_length : (int)
        Maximum allowed string length. (default=50)
    header : (list of str)
        Header string(s) where the last line contains whitespace separated data
        names (default=list())

    Returns
    ----------
    header : (list of strings)
        Contains all specified header lines
    out : (dict of numpy.arrays)
        The dict keys are specified by the header data line, the data
        for each key are stored in the numpy array

    Notes
    -------
    Data is assumed to be float unless otherwise stated.

    """

    #-----------------------------------------------------------------------
    # Test to ensure the file is small enough to read in.  Python can only
    # allocate 2GB of data.  If you load something larger, python will crash
    if not test_file(filename):
        return header, dict()

    #--------------------------------------------------
    # Initialize the convert_time input dictionary
    dfmt_parts = list() if datetime_fmt is None else datetime_fmt.split(" ")
    convert_time_input = {"year": None, "soy": None, "yyddd": None,
                          "date": None, "tod": None,
                          "datetime_fmt": datetime_fmt}
    time_formats = ["H", "I", "p", "M", "S", "f", "z", "Z"]

    #----------------------------------------------------------------------
    # Make sure the max_str_length is long enough to read datetime and that
    # the time data will be cast in the correct format
    if datetime_fmt is not None:
        if max_str_length < len(datetime_fmt):
            max_str_length = len(datetime_fmt)
            if datetime_fmt.find("%y") >= 0 or datetime_fmt.find("%j") >= 0:
                max_str_length += 2
            if(datetime_fmt.find("%a") >= 0 or datetime_fmt.find("%b") >= 0 or
            datetime_fmt.find("%Z") >= 0):
                max_str_length += 1
            if(datetime_fmt.find("%B") >= 0 or datetime_fmt.find("%X") >= 0 or
            datetime_fmt.find("%x") >= 0):
                max_str_length += 10
            if datetime_fmt.find("%f") >= 0 or datetime_fmt.find("%Y") >= 0:
                max_str_length += 4
            if datetime_fmt.find("%z") >= 0:
                max_str_length += 3
            if datetime_fmt.find("%c") >= 0:
                max_str_length += 20
            if datetime_fmt.upper().find("YYDDD"):
                max_str_length += 8

        if datetime_fmt.upper().find("YEAR") >= 0:
            ipart = datetime_fmt.upper().find("YEAR")
            case_part = datetime_fmt[ipart:ipart+4]
            int_cols.append(dfmt_parts.index(case_part))
        if datetime_fmt.upper().find("SOY") >= 0:
            ipart = datetime_fmt.upper().find("SOY")
            case_part = datetime_fmt[ipart:ipart+3]
            int_cols.append(dfmt_parts.index(case_part))

    #----------------------------------------------
    # Open the data file and read the header rows
    with open(filename, "r") as fin:
        in_header = str(header[-1]) if len(header) > 0 else None

        for hind in range(hlines):
            header.append(fin.readline().strip())

    #---------------------------------------------------------------------
    # Create the output dictionary keylist
    if len(header) == 0:
        estr = "unable to find header of [{:d}] lines".format(hlines)
        ocbpy.logger.error(estr)
        return header, dict()

    keyheader = in_header if in_header is not None else header[-1]

    if 'comment' in gft_kwargs.keys() and gft_kwargs['comment'] is not None:
        keyheader = keyheader.split(gft_kwargs['comment'])[0]

    keyheader = keyheader.replace("#", "").strip()
    keylist = keyheader.split(hsplit)
    nhead = len(keylist)
    out = {okey: list() for okey in keylist}

    #---------------------------------------------------------------------
    # Build the dtype list
    ldtype = [float for i in range(nhead)]

    for icol in int_cols:
        ldtype[icol] = int

    for icol in str_cols:
        ldtype[icol] = '|U{:d}'.format(max_str_length)
    
    #---------------------------------------------------------------------
    # Build and add the datetime objects to the output dictionary
    dt_keys = ['datetime', 'DATETIME', 'DT', 'dt']
    if len(datetime_cols) > 0 and datetime_fmt is not None:
        idt = 0
        while dt_keys[idt] in out.keys(): idt += 1

        if idt < len(dt_keys):
            keylist.append(dt_keys[idt])
            out[dt_keys[idt]] = list()

        # Change the datetime column input from float to string, if it is not
        # supposed to be an integer
        for i, icol in enumerate(datetime_cols):
            if(not icol in int_cols and
               dfmt_parts[i].upper().find("SOD") < 0):
                ldtype[icol] = '|U{:d}'.format(max_str_length)
    else:
        idt = len(dt_keys)

    #-------------------------------------------
    # Open the datafile and read the data rows
    temp = np.genfromtxt(filename, skip_header=hlines, dtype=ldtype,
                         **gft_kwargs)

    if len(temp) > 0:
        noff = 0
        # When dtype is specified, output comes as a np.array of np.void objects
        for line in temp:
            if len(line) == nhead:
                for num,name in enumerate(keylist):
                    if len(name) > 0:
                        if idt < len(dt_keys) and name == dt_keys[idt]:
                            # Build the convert_time input
                            for icol, dcol in enumerate(datetime_cols):
                                if dfmt_parts[icol].find("%") == 0:
                                    if dfmt_parts[icol][1] in time_formats:
                                        ckey = "tod"
                                    else:
                                        ckey = "date"
                                else:
                                    ckey = dfmt_parts[icol].lower()
                                    if ckey in ['year', 'soy']:
                                        line[dcol] = int(line[dcol])
                                    elif ckey == 'sod':
                                        line[dcol] = float(line[dcol])
                                        
                                convert_time_input[ckey] = line[dcol]
                                
                            # Convert the string into a datetime object
                            try:
                                ftime = ocbt.convert_time(**convert_time_input)
                            except ValueError as verr:
                                raise verr

                            # Save the output data
                            out[dt_keys[idt]].append(ftime)
                        else:
                            out[name].append(line[num-noff])
                    else:
                        noff += 1
            else:
                estr = "unknown genfromtxt output for [{:s}]".format(filename)
                ocbpy.logger.error(estr)
                return header, dict()

    del temp

    # Cast all lists as numpy arrays, if possible
    for k in out.keys():
        try:
            out[k] = np.array(out[k], dtype=type(out[k][0]))
        except TypeError:
            pass

    return header, out
