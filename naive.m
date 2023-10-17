%% initial parameters
P_tot=107000;
V=3500;
% unvaccinated uninfected population
P_G1=P_tot*0.137; %<18
P_G2=P_tot*0.164; %>65
P_G3=P_tot-P_G1-P_G2; %18-65
% vaccinated uninfected population
V_P_G1=0; %no one is vaccinated at the beginning
V_P_G2=0;
V_P_G3=0;
% unvaccinated infected population
I_G1=5; %initial infected population
I_G2=5;
I_G3=5;
% vaccinated infected population
V_I_G1=0;
V_I_G2=0;
V_I_G3=0;
% unvaccinated dead population
D_G1=0;
D_G2=0;
D_G3=0;
% vaccinated dead population
V_D_G1=0;
V_D_G2=0;
V_D_G3=0;
%death rate
DR_G1=0.001;
DR_G2=0.18;
DR_G3=0.02;
%infection rate
IR_G1toG1=5.4; %0.18*30
IR_G1toG2=8.4; %0.28*30
IR_G1toG3=5.4; %0.18*30
IR_G2toG1=5.1; %0.17*30
IR_G2toG2=7.4; %0.25*30
IR_G2toG3=5.1; %0.17*30
IR_G3toG1=2.3; %the ratio of parents to children : children to parents is about 3:7
IR_G3toG2=8.4; %0.28*30
IR_G3toG3=5.4; %0.18*30

VDR=0.1; %vaccine effect on death rate
VIR=0.3; %vaccine effect on infection rate
% assume people always either die or recover after 30 days, so there is no need to recover group

%% time to stimulate

%give vaccine proportion to each group
temp=P_G1+P_G2+P_G3;

V_P_G1=V_P_G1+V*P_G1/temp;
V_P_G2=V_P_G2+V*P_G2/temp;
V_P_G3=V_P_G3+V*P_G3/temp;

P_G1=P_G1-V*P_G1/temp;
P_G2=P_G2-V*P_G2/temp;
P_G3=P_G3-V*P_G3/temp;

%get infected



