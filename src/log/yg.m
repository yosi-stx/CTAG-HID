a = csvread('C:\Work\Python\CTAG_HID\src\log\clicker_log.csv');
figure(1)
x1=100;
x2= 9*x1;
% plot(x,'o')
xa = a(:,1);
% plot(9*a,a(:,2),'o')
% plot(9*a(1:x1),a(1:x1,2),'-*g')
plot(9*xa(1:x1),a(1:x1,2),'-*g')
% return

hold on

b = csvread('C:\Work\Python\CTAG_HID\src\log\clicker_overSample.csv');
% figure(2)

% plot(y(:,2))
% plot(y(:,1),y(:,2),'.')
% plot(b(:,1),b(:,2),'.')
last_b_index = length(b);
xb = [1:last_b_index];
plot(xb(1:x2),b(1:x2,2),'-*b')
hold off
