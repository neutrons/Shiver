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
        filename="/home/3y9/Desktop/deleteme.txt",
        login=ocl,
        ipts_number="27023",
        instrument="ARCS",
        group_by_angle=True,
    )
)

# delete one particular run from a particular dataset
write_json_from_oncat(
    filename="/home/3y9/Desktop/deleteme.txt",
    login=ocl,
    ipts_number="27023",
    instrument="ARCS",
    dataset_name="U2Zn17_30meV_res_5K",
    exclude_runs=[222669],
    group_by_angle=True,
    append=True,
)
