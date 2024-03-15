%% Function PRS_readData.m
% Reads LTT pressure data files
% =========================================================================
% Tomas Sinnige - T.Sinnige@tudelft.nl 
% TU Delft - LR - AWEP - Flight Performance and Propulsion
%
% Version: 0.0
% Last updated:  25 Feb 2022
% First version: 25 Feb 2022
% =========================================================================
% |---------|-----------|-----------|-------------------------------------|
% |   0.0   | 25/02/'22 | T.Sinnige | First version                       |
% |---------|-----------|-----------|-------------------------------------|
% =========================================================================
% Inputs:  fn     - filename of the raw measurement file
%          idxB   - indices in Balance data structures
%          dPbCut - cut-off dPb for filtering of outliers 
% -------------------------------------------------------------------------
% Outputs: data - structure containing output data
%                  
% =========================================================================
function DATA = PRS_readData(fn,idxP)

% %% Print status update
% display(['Loading pressure data: ',fn])
% data.fn = fn

%% Load Data
% raw data
fid      = fopen(fn);
read_data = cell2mat(textscan(fid,['%f %f:%f:%f',repmat(' %f',1,292)],'headerlines',2));
fclose(fid);
    
% % sometimes a zero m'ment dataline is written to the PRS files which is not
% % used in processing, and needs to be removed to prevent issues later on in
% % the processing. Such outliers are identified here as points with a dPb of
% % less than 1 Pa
% idxOutlier = read_data(:,idxP.dPb) < 1;
% read_data(idxOutlier,:) = [];

%% Insert data into structure 
DATA.run    = read_data(:,idxP.run);
DATA.hr     = read_data(:,idxP.hr);
DATA.min    = read_data(:,idxP.min);
DATA.sec    = read_data(:,idxP.sec);
DATA.AoA    = read_data(:,idxP.AoA);
DATA.AoS    = read_data(:,idxP.AoS);
DATA.dPb    = read_data(:,idxP.dPb);
DATA.pBar   = read_data(:,idxP.pBar);
DATA.temp   = read_data(:,idxP.temp);
DATA.rpmWT  = read_data(:,idxP.rpmWT);
DATA.rho    = read_data(:,idxP.rho);
DATA.q      = read_data(:,idxP.q);
DATA.V      = read_data(:,idxP.V);
DATA.Re     = read_data(:,idxP.Re);
DATA.pTfs   = read_data(:,idxP.pTfs);  % total-pressure measurement upstream in test section [Pa]
DATA.pSfs   = read_data(:,idxP.pSfs);  % static-pressure measurement upstream in test section [Pa] 
DATA.pTaps  = read_data(:,idxP.presTaps); % pressure readings pressure taps on fuselage [Pa]
DATA.CpTaps = (DATA.pTaps-(DATA.pTfs-DATA.q))./DATA.q; % pressure coefficients on fuselage [Pa]
DATA.rpsM1 = read_data(:,idxP.rps_ac); % RPS of motor 1 [Hz]

end % end of function BAL_readData.m