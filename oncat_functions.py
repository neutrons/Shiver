from oncat_util import get_fromoncat, oncat_login
import numpy as np

def get_dataset_names(ocl, IPTSnum='27032', instrument="ARCS", use_notes=False, facility="SNS"):
    projection=['metadata.entry.daslogs.sequencename',
                'metadata.entry.notes']
    ds = get_fromoncat(ocl, projection, IPTSnum, instrument, facility)
    
    if use_notes:
        v=[ds[i]['metadata']['entry']['notes'] for i in range(len(ds))]
    else:
        v=[ds[i]['metadata']['entry']['daslogs']['sequencename']['value'] for i in range(len(ds))]

    return set(v)


def get_dataset_info(ocl, *,
                     dataset_name='FeGe100meV_120K_base', 
                     use_notes=False, 
                     IPTSnum, 
                     instrument, 
                     facility="SNS",
                     group_by_angle=False, 
                     anglePV="omega", 
                     angle_bin=0.5, 
                     include_runs=None, 
                     exclude_runs=None):

    # get run number, angle, and sequence names from oncat 
    projection=["indexed.run_number", f'metadata.entry.daslogs.{anglePV}']
    if use_notes:
        projection.append('metadata.entry.notes')
    else:
        projection.append('metadata.entry.daslogs.sequencename')
    datafiles = get_fromoncat(ocl, projection, IPTSnum, instrument, facility)
    
    run_number = np.empty(len(datafiles), dtype='int') 
    angle = {}
    sequence = np.empty(len(datafiles),dtype='U50')
    for idx, df in enumerate(datafiles):
        run_number[idx] = df['indexed']['run_number']
        angle[str(run_number[idx])] = df['metadata']['entry']['daslogs'][anglePV]['average_value']
        if use_notes:
            sequence[idx] =  df['metadata']['entry']['notes']
        else:
            sequence[idx] =  df['metadata']['entry']['daslogs']['sequencename']['value']
    
    if dataset_name:
        good_runs = run_number[sequence == dataset_name]
    else:
        good_runs = np.array([], dtype='int')

    # include runs
    if include_runs:
        # check if all include_runs are part of this IPTS
        if not np.all(np.in1d(include_runs, run_number)):
            raise ValueError("Could not find all the 'include_runs' in this IPTS")
        # check if runs already in the good_runs
        if np.any(np.in1d(include_runs, good_runs)):
            raise ValueError("Some 'include_runs' are already part of the dataset")
        good_runs=np.append(good_runs, include_runs)

    # exclude runs
    if exclude_runs:
        # check if all the exclude_runs are already selected
        if not np.all(np.in1d(exclude_runs, good_runs)):
            raise ValueError("Could not find all the 'exclude_runs' in this dataset")
        good_runs=good_runs[np.isin(good_runs,exclude_runs,invert=True)]
    
    #group by angle if desired
    if group_by_angle:
        angle_list=[angle[str(r)] for r in good_runs]
        # sort runs by angle
        z=[(x,y) for x,y in sorted(zip(angle_list,good_runs))]
        angle_list,good_runs=zip(*z)
        angle_list=np.array(angle_list)
        good_runs=np.array(good_runs)
        grouped_runs=[]
        while len(good_runs)>0:
            inds=angle_list-angle_list[0] < angle_bin      
            grouped_runs.append(good_runs[inds].tolist())
            good_runs=good_runs[np.logical_not(inds)] 
            angle_list=angle_list[np.logical_not(inds)]
        good_runs=grouped_runs
    return good_runs

#ocl = oncat_login()
#print(get_dataset_names(ocl, IPTSnum='27032', instrument="ARCS"))
#print(get_dataset_names(ocl, IPTSnum='27382', instrument="HYS", use_notes=True))
print(get_dataset_info(ocl, IPTSnum='27032', instrument="ARCS", group_by_angle=True))
