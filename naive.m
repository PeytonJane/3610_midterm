%% initial parameters
P_tot=107000;
V=3500;

iniP_G1=P_tot*0.137; %<18
iniP_G2=P_tot*0.164; %>65
iniP_G3=P_tot-P_G1-P_G2; %18-65
% unvaccinated uninfected population
P_G1=iniP_G1;
P_G2=iniP_G2;
P_G3=iniP_G3;
% vaccinated uninfected population
V_P_G1=0; %no one is vaccinated at the beginning
V_P_G2=0;
V_P_G3=0;
% unvaccinated infected population
I_G1=[5]; %initial infected population
I_G2=[5];
I_G3=[5];
% vaccinated infected population
V_I_G1=[0];
V_I_G2=[0];
V_I_G3=[0];
% unvaccinated dead population
D_G1=[0];
D_G2=[0];
D_G3=[0];
% vaccinated dead population
V_D_G1=[0];
V_D_G2=[0];
V_D_G3=[0];
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
while (I_G1(end)+I_G2(end)+I_G3(end)+V_I_G1(end)+V_I_G2(end)+V_I_G3(end))>=0 && (P_G1+P_G2+P_G3)>0

    %give vaccine proportion to each group
    temp=P_G1+P_G2+P_G3;

    V_P_G1=V_P_G1+V*P_G1/temp;
    V_P_G2=V_P_G2+V*P_G2/temp;
    V_P_G3=V_P_G3+V*P_G3/temp;

    P_G1=P_G1-V*P_G1/temp;
    if P_G1<0
        P_G1=0;
    end
    P_G2=P_G2-V*P_G2/temp;
    if P_G2<0
        P_G2=0;
    end
    P_G3=P_G3-V*P_G3/temp;
    if P_G3<0
        P_G3=0;
    end

    %get infected
    new_I_G1=(P_G1/iniP_G1)*(IR_G1toG1*I_G1(end)+IR_G2toG1*I_G2(end)+IR_G3toG1*I_G3(end)+VIR*(V_I_G1(end)*IR_G1toG1+V_I_G2(end)*IR_G2toG1+V_I_G3(end)*IR_G3toG1));
    new_I_G2=(P_G2/iniP_G2)*(IR_G1toG2*I_G1(end)+IR_G2toG2*I_G2(end)+IR_G3toG2*I_G3(end)+VIR*(V_I_G1(end)*IR_G1toG2+V_I_G2(end)*IR_G2toG2+V_I_G3(end)*IR_G3toG2));
    new_I_G3=(P_G3/iniP_G3)*(IR_G1toG3*I_G1(end)+IR_G2toG3*I_G2(end)+IR_G3toG3*I_G3(end)+VIR*(V_I_G1(end)*IR_G1toG3+V_I_G2(end)*IR_G2toG3+V_I_G3(end)*IR_G3toG3));

    new_V_I_G1=VIR*(V_P_G1/iniP_G1)*(IR_G1toG1*I_G1(end)+IR_G2toG1*I_G2(end)+IR_G3toG1*I_G3(end)+VIR*(V_I_G1(end)*IR_G1toG1+V_I_G2(end)*IR_G2toG1+V_I_G3(end)*IR_G3toG1));
    new_V_I_G2=VIR*(V_P_G2/iniP_G2)*(IR_G1toG2*I_G1(end)+IR_G2toG2*I_G2(end)+IR_G3toG2*I_G3(end)+VIR*(V_I_G1(end)*IR_G1toG2+V_I_G2(end)*IR_G2toG2+V_I_G3(end)*IR_G3toG2));
    new_V_I_G3=VIR*(V_P_G3/iniP_G3)*(IR_G1toG3*I_G1(end)+IR_G2toG3*I_G2(end)+IR_G3toG3*I_G3(end)+VIR*(V_I_G1(end)*IR_G1toG3+V_I_G2(end)*IR_G2toG3+V_I_G3(end)*IR_G3toG3));

    if new_I_G1>P_G1
        new_I_G1=P_G1;
    end
    P_G1=P_G1-new_I_G1;
    if new_I_G2>P_G2
        new_I_G2=P_G2;
    end
    P_G2=P_G2-new_I_G2;
    if new_I_G3>P_G3
        new_I_G3=P_G3;
    end
    P_G3=P_G3-new_I_G3;

    if new_V_I_G1>V_P_G1
        new_V_I_G1=V_P_G1;
    end
    V_P_G1=V_P_G1-new_V_I_G1;
    if new_V_I_G2>V_P_G2
        new_V_I_G2=V_P_G2;
    end
    V_P_G2=V_P_G2-new_V_I_G2;
    if new_V_I_G3>V_P_G3
        new_V_I_G3=V_P_G3;
    end
    V_P_G3=V_P_G3-new_V_I_G3;

    I_G1=[I_G1 new_I_G1];
    I_G2=[I_G2 new_I_G2];
    I_G3=[I_G3 new_I_G3];

    V_I_G1=[V_I_G1 new_V_I_G1];
    V_I_G2=[V_I_G2 new_V_I_G2];
    V_I_G3=[V_I_G3 new_V_I_G3];

    %get dead
    D_G1=[D_G1 DR_G1*I_G1(end)];
    D_G2=[D_G2 DR_G2*I_G2(end)];
    D_G3=[D_G3 DR_G3*I_G3(end)];

    V_D_G1=[V_D_G1 VDR*DR_G1*V_I_G1(end)];
    V_D_G2=[V_D_G2 VDR*DR_G2*V_I_G2(end)];
    V_D_G3=[V_D_G3 VDR*DR_G3*V_I_G3(end)];
end