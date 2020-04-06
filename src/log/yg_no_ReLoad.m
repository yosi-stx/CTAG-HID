% a = csvread('C:\Work\Python\CTAG_HID\src\log\clicker_log.csv');
figure(1)
% x1=100;
x1=length(a);
% x2= 9*x1;
x2= 10*x1;
% plot(x,'o')

% adjust the X axis index of the 2 mSec sample to the overSample indices 
% xa = 9*a(:,1)-8;
xa = 10*a(:,1)-9;
plot(xa(1:x1),a(1:x1,2),'-or')
% return

hold on

% b = csvread('C:\Work\Python\CTAG_HID\src\log\clicker_overSample.csv');
% figure(2)

% plot(y(:,2))
% plot(y(:,1),y(:,2),'.')
% plot(b(:,1),b(:,2),'.')
last_b_index = length(b);
xb = [1:last_b_index] ;
xb=xb';
plot(xb(1:x2),b(1:x2,2),'-*b')
hold off
axis ([8800 8880 -2 30])
