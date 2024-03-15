%% Main processing file LTT data AE4115 lab exercise 2021-2022
% T Sinnige
% 28 March 2022

%% Initialization
% clear workspace, figures, command window
clear 
close all
clc

%% Inputs

% define root path on disk where data is stored
%diskPath = './DATA';
diskPath = './Group25';

% get indices balance and pressure data files
[idxB,idxP] = SUP_getIdx;

% filename(s) of the raw balance files - DEFINE AS STRUCTURE WITH AS MANY FILENAMES AS DESIRED 
% The name of the file must start with "raw_". If the filename starts with
% a character that is not a letter, a plus sign, or a minus sign, the code
% will throw an error in BAL_process.m and you will have to add some code 
% there to handle the exception. (the filenames are used as fields in a 
% structure and these must start with a letter, so you will need to replace
% the first character with a letter. For the + and - signs this has already
% been implemented.
%fn_BAL = {'BAL/raw_proponzerodef.txt'};
fn_BAL = {'BAL/raw_test_29.txt', 'BAL/raw_test_30.txt'};

% Starting index for extension
start_index = 29; % Starting index from which to extend
end_index = 88;   % Ending index

% Numbers to skip
skip_numbers = [58, 69];

% Initialize extended filenames
extended_filenames = cell(1, end_index - start_index + 1 - numel(skip_numbers));

% Extend filenames from start_index to end_index excluding skip_numbers
counter = 1;
for i = start_index:end_index
    if any(i == skip_numbers)
        continue; % Skip this number
    end
    filename = sprintf('BAL/raw_test_%d.txt', i);
    extended_filenames{counter} = filename;
    counter = counter + 1;
end

% Concatenate with existing filenames
extended_filenames = [fn_BAL, extended_filenames];
fn_BAL=extended_filenames;

% filename(s) of the zero-measurement (tare) data files. Define an entry
% per raw data files. In case multiple zero-measurements are available for
% a datapoint, then add a structure with the filenames of the zero 
% measurements at the index of that datapoint.
%fn0 = {'BAL/zer_ 20220216-085611.txt'}; 
fn0 = {'BAL/zer_ 20240306-131745.txt ' ,'BAL/zer_ 20240306-121817.txt '};

x = 30; % Number of times to repeat the first filename
y = 30; % Number of times to repeat the second filename

% Extract the filenames
filename1 = fn0{1};
filename2 = fn0{2};

% Repeat filenames
extended_filenames = cell(1, x + y);
for i = 1:x
    extended_filenames{i} = filename1;
end
for i = x+1:x+y
    extended_filenames{i} = filename2;
end

fn0=extended_filenames;

% filenames of the pressure data files (same comments apply as for balance 
% data files)
fn_PRS = {'PRESSURE/raw_test_29.txt'};
   
% wing geometry
b     = 1.4*cosd(4); % span [m]
cR    = 0.222; % root chord [m]
cT    = 0.089; % tip chord [m]
S     = b/2*(cT+cR);   % reference area [m^2]
taper = cT/cR; % taper ratio
c     = 2*cR/3*(1+taper+taper^2)/(1+taper); % mean aerodynamic chord [m]

% prop geometry
D        = 0.2032; % propeller diameter [m]
R        = D/2;   % propeller radius [m]

% moment reference points
XmRefB    = [0,0,0.0465/c]; % moment reference points (x,y,z coordinates) in balance reference system [1/c] 
XmRefM    = [0.25,0,0];     % moment reference points (x,y,z coordinates) in model reference system [1/c] 

% incidence angle settings
dAoA      = 0.0; % angle of attack offset (subtracted from measured values)   
dAoS      = 0.0; % angle of sideslip offset (subtracted from measured values)
modelType = 'aircraft'; % options: aircraft, 3dwing, halfwing
modelPos  = 'inverted'; % options: normal, inverted
testSec   = 5;    % test-section number   

%% Run the processing code to get balance and pressure data
PRS = PRS_process(diskPath,fn_PRS,idxP);
BAL = BAL_process(diskPath,fn_BAL,fn0,idxB,D,S,b,c,XmRefB,XmRefM,dAoA,dAoS,modelType,modelPos,testSec,PRS);

%% Write your code here to apply the corrections and visualize the data
BAL.windOn.test_88
% example of how to access balance data (adapt the names of the fields of
% the structure to your data)
figure
%plot(BAL.windOn.proponzerodef.AoA,BAL.windOn.proponzerodef.CL,'*b')
plot(BAL.windOn.test_37.AoA,BAL.windOn.test_37.CL,'*b')


