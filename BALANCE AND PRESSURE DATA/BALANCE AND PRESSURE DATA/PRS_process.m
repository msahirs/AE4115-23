%% function used to read LTT pressure data (profMeas)
% T Sinnige
% 25 February 2022
%
% Inputs:  diskpath - folder in which data files are stored
%          fn       - filename of data file that is to be loaded
%          idxP     - structure containing indices of variables in the raw, unc, cor data files
% Outputs: PRS     - structure containing the output pressure data
function [PRS] = PRS_process(diskPath,fn_PRS,idxP)

%% Check inputs
% check whether diskPath ends with slash, and if not, append it
if ~strcmpi(diskPath(end),'/') || ~strcmpi(diskPath(end),'\')
    diskPath = [diskPath,'/'];    
end

%% Load raw Data
for i=1:length(fn_PRS)
    
    % extract configuration name
    PRS.config(i) = extractBetween(char(fn_PRS{i}),'raw_','.txt');
    
%     if isletter(PRS.config{i}(1))
%         % first character is letter so can be used as field name -> continue
%     else
%         if strcmpi(PRS.config{i}(1),'+')
%             PRS.config{i}(1) = 'p';
%         elseif strcmpi(PRS.config{i}(1),'-')
%             PRS.config{i}(1) = 'm';
%         else
%            error('Unexpected character used as first character of PRS filename. Please add if statement here that catches this exception and changes the character into a letter.') 
%         end
%     end

    % remove plus/minus symbols (if applicable)  
    PRS.config{i} = strrep(PRS.config{i},'+','p');
    PRS.config{i} = strrep(PRS.config{i},'-','n');    
    if PRS.config{i}(1) == '_'
        PRS.config{i}(1) = [];

    % give status update
    display(['Processing pressure data; configuration ''',PRS.config{i},'''; filename ''',fn_PRS{i},'''.']);

    % load and process measurement data
    PRS.(PRS.config{i}) = PRS_readData([diskPath,fn_PRS{i}],idxP);
    
end

end % end of function PRS_readData.m