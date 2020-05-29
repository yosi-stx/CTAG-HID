a = csvread('C:\Work\Python\CTAG_HID\src\log\motor_current.csv');
figure(1)
hold off
% x1=100;
x1=length(a);

plot((1:x1),a(1:x1,2),'-or')
% return

hold on

