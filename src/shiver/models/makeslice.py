"""The Shiver MakeSlice mantid algorithm"""
#https://ornlrse.clm.ibmcloud.com/ccm/web/projects/Neutron%20Data%20Project%20(Change%20Management)#action=com.ibm.team.workitem.viewWorkItem&id=704
from mantid.api import (
    DataProcessorAlgorithm,
    AlgorithmFactory,
    PropertyMode,
    #WorkspaceGroupProperty,
    #Progress,
    mtd,
    #SpectraAxis,
    WorkspaceGroup,
    WorkspaceProperty,
    IMDEventWorkspaceProperty,
    MatrixWorkspaceProperty,
    IMDHistoWorkspaceProperty
)  # pylint: disable=no-name-in-module


from mantid.kernel import (
    VisibleWhenProperty,
    PropertyCriterion,
    StringListValidator,
    IntBoundedValidator,
    FloatBoundedValidator,
    Direction,
    logger,
    LogicOperator,
    config,
    FloatArrayProperty,
    FloatArrayLengthValidator,
    Property,
    SpecialCoordinateSystem
) # pylint: disable=no-name-in-module



import math
import numpy as np
import os.path


class MakeSlice(DataProcessorAlgorithm):
    # pylint: disable=invalid-name,missing-function-docstring
    """MakeSlice algorithm"""

    def name(self):
        return "MakeSlice"

    def category(self):
        return "Shiver"

    def PyInit(self):
        #Workspaces
        self.declareProperty(
            IMDEventWorkspaceProperty("InputWorkspace", defaultValue="", optional=PropertyMode.Mandatory, direction=Direction.Input),
            doc="Input MDEvent workspace",
        )

        self.declareProperty(
            IMDEventWorkspaceProperty("BackgroundWorkspace", defaultValue="", optional=PropertyMode.Optional, direction=Direction.Input),
            doc="Background Workspace MDEvent workspace",
        )
        
        self.declareProperty(
            MatrixWorkspaceProperty("NormalizationWorkspace", defaultValue="", optional=PropertyMode.Optional, direction=Direction.Input),
            doc="A Matrix workspace.",
        )
        
        
        #from https://github.com/mantidproject/mantid/blob/758f72fbd6ee670ceefbce49e469fbdc1a8430a0/Framework/PythonInterface/plugins/algorithms/WorkflowAlgorithms/SingleCrystalDiffuseReduction.py
        self.declareProperty(
            FloatArrayProperty("QDimension0", [1, 0, 0], FloatArrayLengthValidator(3), direction=Direction.Input),
            "The first Q projection axis",
        )
        self.declareProperty(
            FloatArrayProperty("QDimension1", [0, 1, 0], FloatArrayLengthValidator(3), direction=Direction.Input),
            "The second Q projection axis",
        )
        self.declareProperty(
            FloatArrayProperty("QDimension2", [0, 0, 1], FloatArrayLengthValidator(3), direction=Direction.Input),
            "The third Q projection axis",
        )

        self.copyProperties("MDNorm", 
            ["Dimension0Name",
            "Dimension0Binning",
            "Dimension1Name",
            "Dimension1Binning",
            "Dimension2Name",
            "Dimension2Binning",
            "Dimension3Name",
            "Dimension3Binning",
            "SymmetryOperations"]
        )        
        
        self.declareProperty(
            name="ConvertToChi", defaultValue=False,direction=Direction.Input, doc="Convert To Chi"
        )
  
        self.declareProperty(
            name="Temperature", defaultValue="",direction=Direction.Input, doc="Temperature"
        ) 
         
        self.declareProperty(
            IMDHistoWorkspaceProperty("OutputWorkspace", defaultValue="", optional=PropertyMode.Mandatory, direction=Direction.Output),
            doc="OutputWorkspace IMDHisto workspace",
        ) 
        self.declareProperty(
            name="Smoothing",defaultValue=Property.EMPTY_DBL,direction=Direction.Input, doc="Smoothing"
        )  
              

        #here https://github.com/mantidproject/mantid/blob/758f72fbd6ee670ceefbce49e469fbdc1a8430a0/Framework/PythonInterface/plugins/algorithms/DeltaPDF3D.py
        #https://docs.mantidproject.org/v4.0.0/algorithms/SmoothMD-v1.html
        #groups? default EMPTY_DBL, Property.EMPTY_INT 
        #https://github.com/neutrons/Shiver/blob/main/slice_utils.py#L17

    def validateInputs(self):
        issues = {}

        #smoothing needs to be float
        #if self.getProperty("Smoothing").value:
        #    try:
        #        smoothing = float(self.getProperty("Smoothing").value)
        #    except ValueEsetPropertyrror:
        #        issues["Smoothing"] = "Smoothing is not valid. Float Number is required"
        return issues
    
    def PyExec(self):
        from mantid.simpleapi import MDNorm, DivideMD, MinusMD, CreateMDHistoWorkspace,SmoothMD
        
        slice_name = str(self.getProperty("OutputWorkspace").value).strip(); #Name
        mde_name= str(self.getProperty("InputWorkspace").value).strip(); #MdeName
        out = None
        mdnorm_parameters={'InputWorkspace': mde_name,
           'OutputWorkspace': slice_name,
           'OutputDataWorkspace':'_data',
           'OutputNormalizationWorkspace':'_norm'}
         
        try:
            norm_file = self.getProperty("NormalizationWorkspace").value
        except:
            norm_file = None
        
        if norm_file:
            #norm_ws_name=os.path.split(norm_file)[-1] this is not a path anymore? it is 'norm'
            norm_ws_name = str(norm_file).strip()
            if not mtd.doesExist(norm_ws_name):
                print('Loading normalization and masking file '+norm_file)
                #Load(norm_file,OutputWorkspace=norm_ws_name) ?? what is this??
            mdnorm_parameters['SolidAngleWorkspace']=norm_ws_name
                        
        #what about SolidAngleWorkspace in line35-37?    
        
        for par_name in ['QDimension0','QDimension1','QDimension2','Dimension0Name','Dimension0Binning',
                     'Dimension1Name','Dimension1Binning','Dimension2Name','Dimension2Binning',
                     'Dimension3Name','Dimension3Binning','SymmetryOperations']:
            mdnorm_parameters[par_name]=self.getProperty(par_name).value

        is_chi = self.getProperty("ConvertToChi").value

        temperature = 0
        if is_chi:
            try:         
                temperature = self.getProperty("Temperature").value
            except:
                raise ValueError("For calculating chi'' one needs to set the temperature in the dataset definition. See example.") 
            if not mtd.doesExist(mde_name+'_chi'):
                ApplyDetailedBalanceMD(InputWorkspace=mde_name, Temperature=str(data_set['SampleLogVariables']['Temperature']), OutputWorkspace=mde_name+'_chi')
            mdnorm_parameters['InputWorkspace']=mde_name+'_chi'
        
        
        bg_type=None
        #get the background workspace
        bg_mde_name= self.getProperty("BackgroundWorkspace").value
        if bg_mde_name is not None:
            bg_mde_name= str(bg_mde_name).strip()

        #if background workspace is given
        if bg_mde_name:
            if not mtd.doesExist(bg_mde_name):
                #bg_mde_filename what is this: data_set['MdeFolder']?
                bg_mde_filename=os.path.join(data_set['MdeFolder'],bg_mde_name+'.nxs')
                try:
                    print(bg_mde_name+'background MDE specified in data set is not loaded: try loading from '+bg_mde_filename)
                    LoadMD(bg_mde_filename,OutputWorkspace=data_mde_name, LoadHistory=False)
                except:
                    raise ValueError('BG MDE not found: please run the reduction on BG runs to make the BG MDE '+bg_mde_name)
            if is_chi:
                if not mtd.doesExist(bg_mde_name+'_chi'):
                    ApplyDetailedBalanceMD(InputWorkspace=bg_mde_name, Temperature=str(temperature), OutputWorkspace=bg_mde_name+'_chi')
                bg_mde_name+='_chi'

            if mtd[bg_mde_name].getSpecialCoordinateSystem()==SpecialCoordinateSystem.QLab:
                mdnorm_parameters['BackgroundWorkspace'] = bg_mde_name
                mdnorm_parameters['OutputBackgroundDataWorkspace'] = '_bkg_data'
                mdnorm_parameters['OutputBackgroundNormalizationWorkspace'] = '_bkg_norm'
            elif mtd[bg_mde_name].getSpecialCoordinateSystem()==SpecialCoordinateSystem.QSample:
                mdnorm_bkg_parameters=mdnorm_parameters.copy()
                mdnorm_bkg_parameters['InputWorkspace']= bg_mde_name
                mdnorm_bkg_parameters['OutputWorkspace']= '_bkg'
                mdnorm_bkg_parameters['OutputDataWorkspace']='_bkg_data'
                mdnorm_bkg_parameters['OutputNormalizationWorkspace']='_bkg_norm'
                bg_type='sample'
                MDNorm(**mdnorm_bkg_parameters)
                
        MDNorm(**mdnorm_parameters)
        SmoothingFWHM=self.getProperty("Smoothing").value
        
        if SmoothingFWHM:
            SmoothMD(InputWorkspace='_data', 
                     WidthVector=SmoothingFWHM,
                     Function='Gaussian',
                     InputNormalizationWorkspace='_norm',
                     OutputWorkspace='_data')
            SmoothMD(InputWorkspace='_norm', 
                     WidthVector=SmoothingFWHM,
                     Function='Gaussian',
                     InputNormalizationWorkspace='_norm',
                     OutputWorkspace='_norm')
            DivideMD(LHSWorkspace='_data', RHSWorkspace='_norm', OutputWorkspace=slice_name)
            if bg_mde_name:
                SmoothMD(InputWorkspace='_bkg_data',
                         WidthVector=SmoothingFWHM,
                         Function='Gaussian',
                         InputNormalizationWorkspace='_bkg_norm',
                         OutputWorkspace='_bkg_data')
                SmoothMD(InputWorkspace='_bkg_norm',
                         WidthVector=SmoothingFWHM,
                         Function='Gaussian',
                         InputNormalizationWorkspace='_bkg_norm',
                         OutputWorkspace='_bkg_norm')
                DivideMD(LHSWorkspace='_bkg_data', RHSWorkspace='_bkg_norm', OutputWorkspace='_bkg')

                MinusMD(LHSWorkspace=slice_name,RHSWorkspace='_bkg', OutputWorkspace=slice_name)
        elif bg_type=='sample': # there is background from multi-angle
            MinusMD(LHSWorkspace=slice_name,RHSWorkspace='_bkg', OutputWorkspace=slice_name)        
        

        self.setProperty("OutputWorkspace", mtd[slice_name])
        return slice_name
        
AlgorithmFactory.subscribe(MakeSlice)
