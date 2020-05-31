a = csvread('C:\Work\Python\CTAG_HID\src\log\motor_current.csv');
figure(1)
clf;
hold off
% x1=100;
x1=length(a);

subplot (2, 1, 1)
plot((1:x1),a(1:x1,2),'-or')
hold on
plot((1:x1),a(1:x1,1),'-ob')
hold off

subplot (2, 1, 2)
% plot((1:x1-1),diff(a(1:x1,1)),'-og')
plot((1:x1),(a(1:x1,3)),'-og')
% return
hold off

figure(1)
% hold on

