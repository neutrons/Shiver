import pyoncat
import getpass as gp
import numpy as np
import json


def oncat_login():
    """
    Login to ONCat database. It asks for the password of the current user.
    It returns an instance of pyoncat.ONCat object, to be used in queries.

    Parameters
    ----------
    None
    
    Returns
    -------
    oncat : pyoncat.ONCat
        An object that contains login information to oncat database.
    """
    ONCAT_URL = "https://oncat.ornl.gov"
    CLIENT_ID = "99025bb3-ce06-4f4b-bcf2-36ebf925cd1d"

    oncat = pyoncat.ONCat(ONCAT_URL, client_id=CLIENT_ID, flow=pyoncat.RESOURCE_OWNER_CREDENTIALS_FLOW)
    username = gp.getuser()
    oncat.login(username, gp.getpass('Enter password for "' + username + '":'))
    return oncat


def get_data_from_oncat(login, projection, ipts_number, instrument, facility="SNS", tags="type/raw"):
    """
    Get data according to a projection from oncat
    
    Parameters:
    -----------
    login : pyoncat.ONCat
        An object that contains login information to oncat database.
    projection : list
        A list of paths in the oncat datafile to extract the relevant information.
    ipts_number : int,str
        The experiment identifier number (IPTS)
    instrument : str
        The instrument associated with the datafiles
    facility : str, optional
        The facility associated with the datafiles (Default = 'SNS')
    tags : str, optional
        The type of files to look for in the OnCat database (Default = 'type/raw')
    
    Returns:
    --------
    datafiles: dict
        A dictionary containing information requested from the OnCat database
    """
    datafiles = login.Datafile.list(
        facility=facility,
        instrument=instrument,
        experiment="IPTS-{}".format(ipts_number),
        projection=projection,
        tags=tags,
    )
    return datafiles


def get_dataset_names(login, ipts_number, instrument, use_notes=False, facility="SNS"):
    """
    A function to return the names of the datasets, either from sequence names or from comments
    
    Parameters:
    -----------
    login : pyoncat.ONCat
        An object that contains login information to oncat database. 
    ipts_number : int,str
        The experiment identifier number (IPTS)
    instrument : str
        The instrument associated with the datafiles
    use_notes : bool, optional
        A flag to indicate that the names of the datasets are stored in the 
        Notes/Comments (as opposed to sequence name)
    facility : str, optional
        The facility associated with the datafiles (Default = 'SNS')  
    
    Returns:
    --------
    dsn: set of strings
        A set containing strings with the dataset names, as tored in the OnCat database
    """
    projection = ["metadata.entry.daslogs.sequencename", "metadata.entry.notes"]
    ds = get_data_from_oncat(login, projection, ipts_number, instrument, facility)

    if use_notes:
        dsn = [ds[i]["metadata"]["entry"]["notes"] for i in range(len(ds))]
    else:
        dsn = [ds[i]["metadata"]["entry"]["daslogs"]["sequencename"]["value"] for i in range(len(ds))]

    dsn = set(dsn)
    return dsn


def get_dataset_info(
    *,
    login,
    ipts_number,
    instrument,
    dataset_name=None,
    use_notes=False,
    facility="SNS",
    group_by_angle=False,
    angle_pv="omega",
    angle_bin=0.5,
    include_runs=None,
    exclude_runs=None,
):
    """
    A function to return a list of runs in a dataset, optionally grouped by angle.
    Grouping by angle is from the lowest value, within angle_bin.  
    
    Parameters:
    -----------
    login : pyoncat.ONCat
        An object that contains login information to oncat database. 
    ipts_number : int,str
        The experiment identifier number (IPTS)
    instrument : str
        The instrument associated with the datafiles
    dataset_name : str, optional
        The name of a dataset to look for in the database. It can be None.
    use_notes : bool, optional
        A flag to indicate that the names of the datasets are stored in the 
        Notes/Comments (as opposed to sequence name)
    facility : str, optional
        The facility associated with the datafiles (Default = 'SNS')  
    group_by_angle : bool, optional
        A flag to indicate if the runs should be grouped by angle
    angle_pv : str, optional
        The name of the angle process variable. The value read from this variable 
        will be used for grouping files together.Default is 'omega'
    angle_bin : float, optional
        The maximum difference (in degrees) between angles in the same group. Default is 0.5
    include_runs : array_like, optional
        A list or array of additional runs to be added to the same dataset. The default is None
    exclude_runs : array_like, optional
        A list or array of runs to be excluded from the dataset. The default is None
    
    Returns:
    --------
    good_runs : list
        List of runs in the dataset, or list of list of runs at the same angle
     
    Raises:
    -------
    ValueError
        If any of the include_runs is not in the OnCat database for this IPTS
        If any of the include_runs is already in the dataset
        If any of the exclude_runs is not already accounted for
        If no runs were found to match the criteria (for example, 
            dataset_name=None and include_runs=None) 
    """
    # get run number, angle, and sequence names from oncat
    projection = ["indexed.run_number", f"metadata.entry.daslogs.{angle_pv}"]
    if use_notes:
        projection.append("metadata.entry.notes")
    else:
        projection.append("metadata.entry.daslogs.sequencename")
    datafiles = get_data_from_oncat(login, projection, ipts_number, instrument, facility)

    run_number = np.empty(len(datafiles), dtype="int")
    angle = {}
    sequence = np.empty(len(datafiles), dtype="U50")
    for idx, df in enumerate(datafiles):
        run_number[idx] = df["indexed"]["run_number"]
        angle[str(run_number[idx])] = df["metadata"]["entry"]["daslogs"][angle_pv]["average_value"]
        if use_notes:
            sequence[idx] = df["metadata"]["entry"]["notes"]
        else:
            sequence[idx] = df["metadata"]["entry"]["daslogs"]["sequencename"]["value"]

    if dataset_name:
        good_runs = run_number[sequence == dataset_name]
    else:
        good_runs = np.array([], dtype="int")

    # include runs
    if include_runs:
        include_runs = np.array(include_runs)
        # check if all include_runs are part of this IPTS
        condition = np.in1d(include_runs, run_number)
        if not np.all(condition):
            not_found = include_runs[np.logical_not(condition)]
            bad_str = ", ".join([str(nf) for nf in not_found])
            raise ValueError(f"Could not find the following 'include_runs' in this IPTS: {bad_str}")
        # check if runs already in the good_runs
        condition = np.in1d(include_runs, good_runs)
        if np.any(condition):
            already_there = include_runs[condition]
            bad_str = ", ".join([str(at) for at in already_there])
            raise ValueError(f"The following 'include_runs' are already part of the dataset: {bad_str}")
        good_runs = np.append(good_runs, include_runs)

    # exclude runs
    if exclude_runs:
        exclude_runs = np.array(exclude_runs)
        # check if all the exclude_runs are already selected
        condition = np.in1d(exclude_runs, good_runs)
        if not np.all(condition):
            not_found = exclude_runs[np.logical_not(condition)]
            bad_str = ", ".join([str(nf) for nf in not_found])
            raise ValueError(f"The following 'exclude_runs' are not in this dataset: {bad_str}")
        good_runs = good_runs[np.in1d(good_runs, exclude_runs, invert=True)]

    # no runs found
    if len(good_runs) == 0:
        raise ValueError("Could not find any runs matching your criteria")

    # group by angle if desired
    if group_by_angle:
        angle_list = [angle[str(r)] for r in good_runs]
        # sort runs by angle
        z = [(x, y) for x, y in sorted(zip(angle_list, good_runs))]
        angle_list, good_runs = zip(*z)
        angle_list = np.array(angle_list)
        good_runs = np.array(good_runs)
        grouped_runs = []
        while len(good_runs) > 0:
            inds = angle_list - angle_list[0] < angle_bin
            grouped_runs.append(good_runs[inds].tolist())
            good_runs = good_runs[np.logical_not(inds)]
            angle_list = angle_list[np.logical_not(inds)]
        good_runs = grouped_runs
    else:
        good_runs = good_runs.tolist()
    return good_runs


def write_json_from_oncat(
    *,
    filename,
    login,
    ipts_number,
    instrument,
    dataset_name=None,
    use_notes=False,
    facility="SNS",
    group_by_angle=False,
    angle_pv="omega",
    angle_bin=0.5,
    include_runs=None,
    exclude_runs=None,
    append=False,
):
    """
    A function to write runs belonging to datasets into a json file, 
    optionally grouped by angle. Grouping by angle is from the lowest value, within angle_bin.  
    
    Parameters:
    -----------
    filename : str
        The name of the json file to be written
    login : pyoncat.ONCat
        An object that contains login information to oncat database. 
    ipts_number : int,str
        The experiment identifier number (IPTS)
    instrument : str
        The instrument associated with the datafiles
    dataset_name : str, optional
        The name of a dataset to look for in the database. It can be None.
    use_notes : bool, optional
        A flag to indicate that the names of the datasets are stored in the 
        Notes/Comments (as opposed to sequence name)
    facility : str, optional
        The facility associated with the datafiles (Default = 'SNS')  
    group_by_angle : bool, optional
        A flag to indicate if the runs should be grouped by angle
    angle_pv : str, optional
        The name of the angle process variable. The value read from this variable 
        will be used for grouping files together.Default is 'omega'
    angle_bin : float, optional
        The maximum difference (in degrees) between angles in the same group. Default is 0.5
    include_runs : array_like, optional
        A list or array of additional runs to be added to the same dataset. The default is None
    exclude_runs : array_like, optional
        A list or array of runs to be excluded from the dataset. The default is None
    append : bool, optional
        A flag wether to append (overwrite datasets) in an existing json file
    
    Returns:
    --------
    data.keys : list
        List of dataset names
    
    Notes:
    ------
    1. The json file contains a structure like:
       {"data_set1":[run1, run2, run3],
        "data_set2":[[run11, run 12], [run13, run14]]}
    2. If no name is specified, and include_runs is None, the json file
       will contain all the datasets in the OnCat database for the given ipts_number
    3. include_runs and exclude_runs will be used for a single dataset only. 
    4. If dataset_name is None and include_runs is not, the corresponding entry
       in the json file will be called "custom".
    5. If the dataset_name is not found in the database but include_runs were provided,
       the corresponding entry in the json file will be labelled by the dataset_name
    6. If append is True, and an entry is found with the same name as dataset_name,
       it will be overwritten. All other entries will be unchanged.
    """
    # create the dictionary
    data = {}
    # single entry
    if dataset_name or include_runs:
        value = get_dataset_info(
            login=login,
            ipts_number=ipts_number,
            instrument=instrument,
            dataset_name=dataset_name,
            use_notes=use_notes,
            facility=facility,
            group_by_angle=group_by_angle,
            angle_pv=angle_pv,
            angle_bin=angle_bin,
            include_runs=include_runs,
            exclude_runs=exclude_runs,
        )
        if dataset_name:
            key = dataset_name
        else:
            key = "custom"
        data[key] = value
    # all entries
    else:
        names = get_dataset_names(
            login=login, ipts_number=ipts_number, instrument=instrument, use_notes=use_notes, facility=facility
        )
        for key in names:
            data[key] = get_dataset_info(
                login=login,
                ipts_number=ipts_number,
                instrument=instrument,
                use_notes=use_notes,
                facility=facility,
                dataset_name=key,
                group_by_angle=group_by_angle,
                angle_pv=angle_pv,
                angle_bin=angle_bin,
            )
    # write to file
    if append:
        # first read the file
        with open(filename, "rt") as f:
            d = json.load(f)
        d.update(data)
        with open(filename, "wt+") as f:
            json.dump(d, f)
        return d.keys()
    else:
        with open(filename, "wt+") as f:
            json.dump(data, f)
        return data.keys()
