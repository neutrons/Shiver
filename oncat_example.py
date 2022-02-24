import pyoncat
from oncat_util import oncat_login, write_json_from_oncat

# login to oncat if required
try:
    ocl.Facility.list()
except (NameError, pyoncat.LoginRequiredError, pyoncat.InvalidRefreshTokenError):
    ocl = oncat_login()

# generate file and print the keys
print(
    write_json_from_oncat(
        filename="/SNS/users/3y9/Desktop/deleteme.txt",
        login=ocl,
        ipts_number="27023",
        instrument="ARCS",
        group_by_angle=True,
    )
)

# delete one particular run from a particular dataset
write_json_from_oncat(
    filename="/SNS/users/3y9/Desktop/deleteme.txt",
    login=ocl,
    ipts_number="27023",
    instrument="ARCS",
    dataset_name="need_correct_label_30meV_res_5K",
    exclude_runs=[222669],
    group_by_angle=True,
    append=True,
)

# add entry for some runs that were not labeled as part of a dataset
write_json_from_oncat(
    filename="/SNS/users/3y9/Desktop/deleteme.txt",
    login=ocl,
    ipts_number="27023",
    instrument="ARCS",
    dataset_name="NewDataset",
    include_runs=range(222204, 222210),
    group_by_angle=True,
    angle_bin=10.,
    append=True,
)

# generate file for HYSPEC where datasets were labeled by the notes
print(
    write_json_from_oncat(
        filename="/SNS/users/3y9/Desktop/deleteme1.txt",
        login=ocl,
        ipts_number="27585",
        instrument="HYS",
        use_notes=True,
    )
)

