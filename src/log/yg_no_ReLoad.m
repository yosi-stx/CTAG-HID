% a = csvread('C:\Work\Python\CTAG_HID\src\log\clicker_log.csv');
figure(1)
hold off
% x1=100;
x1=length(a);
% x2= 9*x1;
x2= 10*x1;
% plot(x,'o')

% adjust the X axis index of the 2 mSec sample to the overSample indices 
% xa = 9*a(:,1)-8;
% xa = 10*a(:,1)-9;

% always start the indices from 1
xa = a(:,1) -(a(1,1) -1);
xa = 10*xa-9;
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


%derivative
a_diff = diff(a(:,2));
a_diff_p= find(a_diff==0);
% plot(xa(a_diff_p),a(a_diff_p,2),'k-x')


d=diff(b(:,2));
% plot(-d,'o-r')
% plot(-d,'p-m')

%plot(-d,'p-k')
% glitch

hold off
% q = min(find(b(1:x2,2)>6));
% X_LO = q - 50;
% X_HI = q + 50;
% Y_LO = -2;
% Y_HI = b(X_HI,2) + 5;
% axis ([X_LO X_HI Y_LO Y_HI])
 
% axis ([8800 8880 -2 30])
% max count_dif
max(b(1:x2,3))
%display the glitches
% plot(xb(1:x2),glitchs_points,'-*b')

% axis ([21400 22000 -2 4030])