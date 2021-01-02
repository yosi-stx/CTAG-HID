% plotting of: 2 encoders from  encoders_pos.csv
a = csvread('C:\Work\Python\CTAG_HID\src\log\encoders_pos.csv');
figure(1)
clf;
hold off
% x1=100;
x1=length(a);

bool_reset = a(1:x1,3);

% subplot (2, 1, 1)
plot((1:x1),a(1:x1,2),'-or')  % red is Active_Encoder = 0
hold on
plot((1:x1),a(1:x1,1),'-ob')  % BLUE is Active_Encoder = 1
% plot((1:x1),100*a(1:x1,1),'-*b')  % BLUE is Delta_Inner
% plot((1:x1),a(1:x1,1),'-*b')  % BLUE is Delta_Inner
hold on
% plot((1:x1),4000*a(1:x1,4),'-.k') % used to be Active_Encoder
plot((1:x1),a(1:x1,4),'-ok')  % FW_DeltaInner
plot((1:x1),4000*bool_reset,'-oc')  % bool_reset

MAX_ENC = max(a(1:x1,2));
MAX_AGRREGATE = max(a(1:x1,3));
ratio_agg = MAX_ENC/MAX_AGRREGATE;
% plot((1:x1),ratio_agg*(a(1:x1,3)),'-og')
plot(3300*ones(size(a(1:x1,2))),'-m')
plot(300*ones(size(a(1:x1,2))),'-m')
% plot(300*ones(1:x1),'m')
AGRR_COUNTS = 150;

% find the index of the start of pressing the button:
first_press=min(find(bool_reset));

% fill values to vector "moving_agrr" until first_press
for i = 1:AGRR_COUNTS:first_press
		temp_agrr = a(i,1);
endfor

for i = first_press+1:AGRR_COUNTS:x1-AGRR_COUNTS
	temp_agrr = sum(a(i:i+AGRR_COUNTS,1));
	for j = 1:AGRR_COUNTS
		moving_agrr(i+j) = temp_agrr;
	endfor
endfor

plot((1:length(moving_agrr)),moving_agrr,'-og')


axis([0,x1,-10,4040])

figure(1)
grid
return
hold off

subplot (2, 1, 2)
% plot((1:x1-1),diff(a(1:x1,1)),'-og')
plot((1:x1),(a(1:x1,3)),'-og')
% return
hold off

figure(1)
% hold on

