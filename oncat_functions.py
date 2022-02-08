from oncat_util import get_fromoncat, oncat_login
import numpy as np
import json


def get_dataset_names(login, IPTSnum="27032", instrument="ARCS", use_notes=False, facility="SNS"):
    projection = ["metadata.entry.daslogs.sequencename", "metadata.entry.notes"]
    ds = get_fromoncat(login, projection, IPTSnum, instrument, facility)

    if use_notes:
        v = [ds[i]["metadata"]["entry"]["notes"] for i in range(len(ds))]
    else:
        v = [ds[i]["metadata"]["entry"]["daslogs"]["sequencename"]["value"] for i in range(len(ds))]

    return set(v)


def get_dataset_info(
    *,
    login,
    IPTSnum,
    instrument,
    dataset_name=None,
    use_notes=False,
    facility="SNS",
    group_by_angle=False,
    anglePV="omega",
    angle_bin=0.5,
    include_runs=None,
    exclude_runs=None,
):

    # get run number, angle, and sequence names from oncat
    projection = ["indexed.run_number", f"metadata.entry.daslogs.{anglePV}"]
    if use_notes:
        projection.append("metadata.entry.notes")
    else:
        projection.append("metadata.entry.daslogs.sequencename")
    datafiles = get_fromoncat(login, projection, IPTSnum, instrument, facility)

    run_number = np.empty(len(datafiles), dtype="int")
    angle = {}
    sequence = np.empty(len(datafiles), dtype="U50")
    for idx, df in enumerate(datafiles):
        run_number[idx] = df["indexed"]["run_number"]
        angle[str(run_number[idx])] = df["metadata"]["entry"]["daslogs"][anglePV]["average_value"]
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
        good_runs = good_runs[np.isin(good_runs, exclude_runs, invert=True)]

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


def write_json(
    *,
    filename,
    login,
    IPTSnum,
    instrument,
    dataset_name=None,
    use_notes=False,
    facility="SNS",
    group_by_angle=False,
    anglePV="omega",
    angle_bin=0.5,
    include_runs=None,
    exclude_runs=None,
    append=False,
):

    # create the dictionary
    data = {}
    # single entry
    if dataset_name or include_runs:
        value = get_dataset_info(
            login=login,
            IPTSnum=IPTSnum,
            instrument=instrument,
            dataset_name=dataset_name,
            use_notes=use_notes,
            facility=facility,
            group_by_angle=group_by_angle,
            anglePV=anglePV,
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
            login=login, IPTSnum=IPTSnum, instrument=instrument, use_notes=use_notes, facility=facility
        )
        for key in names:
            data[key] = get_dataset_info(
                login=login,
                IPTSnum=IPTSnum,
                instrument=instrument,
                use_notes=use_notes,
                facility=facility,
                dataset_name=key,
                group_by_angle=group_by_angle,
                anglePV=anglePV,
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


# ocl = oncat_login()
# print(get_dataset_names(ocl, IPTSnum='27032', instrument="ARCS"))
# print(get_dataset_names(ocl, IPTSnum='27382', instrument="HYS", use_notes=True))
print(
    write_json(
        filename="/home/3y9/Desktop/deleteme.txt",
        login=ocl,
        IPTSnum="27032",
        instrument="ARCS",
        group_by_angle=True,
        include_runs=range(208063, 208066),
    )
)
# print(get_dataset_info(login=ocl, dataset_name='FeGe100meV_120K_base', IPTSnum='27032', instrument="ARCS", group_by_angle=True))
