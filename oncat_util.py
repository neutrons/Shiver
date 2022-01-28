import pyoncat
import getpass as gp
ONCAT_URL = "https://oncat.ornl.gov"
CLIENT_ID = '34c6317e-c4cf-4501-9bb7-61de0b152c36'


def oncat_login():
    oncat = pyoncat.ONCat(ONCAT_URL,client_id=CLIENT_ID,
                          flow=pyoncat.RESOURCE_OWNER_CREDENTIALS_FLOW)
    username = gp.getuser()
    oncat.login(username,
                gp.getpass("Enter password for \"" + username + "\":"))
    return oncat


def get_fromoncat(ocl, projection, IPTSnum, instrument="ARCS", facility="SNS", tags='type/raw'):
    """
    get data according to a projection from oncat
    """
    datafiles = ocl.Datafile.list(facility=facility,
                                  instrument=instrument,
                                  experiment="IPTS-{}".format(IPTSnum),
                                  projection=projection,
                                  tags=tags)
    return datafiles
