% clickDetectorAlt2.m
% finds a click signal in a vector with Alternative 2 algorithm
sig = b(1:x2,2);
hold on

TRESH_LO = 700;
TRESH_HI = 2800;
##MAX_HI_STATE = 180;
MAX_HI_STATE = 290;
%MAX_FALL_DOWN = 150; % enable 30 ms from Hi to Low.
MAX_FALL_DOWN = 175; % enable 30 ms from Hi to Low.
LINE_SIMB = 250;
LINE_SIMB2 = 150;
% WAIT_TO_ARM =  5000*0.3; % =1500
WAIT_TO_ARM =  5000*0.4; 
WAIT_AT_HIGH_TRESH =  5000*0.050; % =250
click_state = 1;
click_state_prev = 1;
click_state_changes = 0;
progress = 0;
progress10 = length(sig)/10;
agr_progress =0;
cross_lo_up_pos = 0;
cross_lo_down_pos = 0;
cross_hi_up_pos = 0;
cross_hi_down_pos = 0;

click_index = 0;
click_detect_pos = 0;
click_hi_pos = 0;
otherwise_cntr = 0;
fail_reason = 0;
fail_cntr = 0;
fail_pos = 0;

% draw thresholds lines..
plot([0 length(sig)],[TRESH_HI TRESH_HI],'c--')
plot([0 length(sig)],[TRESH_LO TRESH_LO],'g--')

function plot_ix(point,LINE_SIMB,sig)
  plot([point+LINE_SIMB point-LINE_SIMB],[sig(point)-LINE_SIMB sig(point)+LINE_SIMB],'-r')
  plot([point-LINE_SIMB point+LINE_SIMB],[sig(point)-LINE_SIMB sig(point)+LINE_SIMB],'-r')
endfunction

function plot_ix_green(point,LINE_SIMB,sig)
  plot([point+LINE_SIMB point-LINE_SIMB],[sig(point)-LINE_SIMB sig(point)+LINE_SIMB],'-g')
  plot([point-LINE_SIMB point+LINE_SIMB],[sig(point)-LINE_SIMB sig(point)+LINE_SIMB],'-g')
endfunction

function plot_ix_m(point,LINE_SIMB,sig)
  plot([point+LINE_SIMB point-LINE_SIMB],[sig(point)-LINE_SIMB sig(point)+LINE_SIMB],'-m')
  plot([point-LINE_SIMB point+LINE_SIMB],[sig(point)-LINE_SIMB sig(point)+LINE_SIMB],'-m')
endfunction

function plot_ix_black(point,LINE_SIMB,sig)
  plot([point+LINE_SIMB point-LINE_SIMB],[sig(point)-LINE_SIMB sig(point)+LINE_SIMB],'-k')
  plot([point-LINE_SIMB point+LINE_SIMB],[sig(point)-LINE_SIMB sig(point)+LINE_SIMB],'-k')
endfunction

for i = 20:length(sig)
##for i = 24200:length(sig)
  progress++;
  agr_progress++;
  if (progress > progress10)
    progress = 0;
    printf(" %d \n", floor(100*agr_progress/length(sig)))
  endif
  if( click_state != click_state_prev )
    click_state_changes++;
  endif
  click_state_prev = click_state;

  switch(click_state)
    case 1
      % check cross of TRESH_HI
      if( sig(i-1) >= TRESH_HI && sig(i) < TRESH_HI )
##        myZoom(i,0.2);
        click_state++;
        cross_hi_down_pos = i;
        plot_ix_m(i,LINE_SIMB2,sig)
				click_index++;
				click_detect_pos(click_index) = i;
      endif
    % case {2,3,4} % 3 rises in signal. -> filter out to fast rise.
		case 2
		% wait for 0.4 sec before enabling next detection (5000*0.4=2000 = WAIT_TO_ARM)
      if( i - cross_hi_down_pos >= WAIT_TO_ARM )
##        myZoom(i,0.2);
        click_state++;
				wait_at_high = 1;
        % click_state = 3; % re-arm the detection for next click detection
        plot_ix_green(i,LINE_SIMB/2,sig)
      endif
			
    case 3  % wait another 0.05 sec at high level.
      if( sig(i) > TRESH_HI )
        % cross_hi_up_pos = i;
				wait_at_high++;
			else
				if (wait_at_high > 0)
					plot_ix(i,LINE_SIMB2,sig)
				endif
				wait_at_high = 0;
      endif
			
			if( wait_at_high >= WAIT_AT_HIGH_TRESH )
        click_state = 1; % return to Armed condition, and wait for next click!
				plot_ix_black(i,LINE_SIMB/2,sig)
			endif
%			
%    case 6  % is is enough to be only one sample above TRESH_HI
%      if( sig(i) < TRESH_HI )
%        click_state++;
%        cross_hi_down_pos = i;
%      endif
%    case 7
%      if( cross_hi_down_pos - cross_hi_up_pos < MAX_HI_STATE )
%        click_state++;
%      else
%        plot_ix(i,LINE_SIMB,sig)
%        fail_cntr++;
%        fail_reason(fail_cntr) = click_state;
%        fail_pos(fail_cntr) = i;
%        click_state = 1;
%      endif
%    case 8
%      if( sig(i) < TRESH_LO )
%        click_state++;
%        cross_lo_down_pos = i;
%      endif
%    case 9
%      if( sig(i) < TRESH_LO )
%        if( cross_lo_down_pos -  cross_hi_down_pos <= MAX_FALL_DOWN )
%          click_state++;
%        else
%          plot_ix(i,LINE_SIMB,sig)
%          fail_cntr++;
%          fail_reason(fail_cntr) = click_state;
%          fail_pos(fail_cntr) = i;
%          click_state = 1;
%        endif
%      endif
%    case 10
%      % we have a click !!
%      click_index++;
%      click_detect_pos(click_index) = i;
%      click_hi_pos(click_index) = cross_hi_up_pos;
%      % line indication of click:
%      %plot([cross_hi_up_pos i],[sig(cross_hi_up_pos) sig(i)], '-m')
%      % rectangle indication of click:
%      plot([cross_hi_up_pos cross_hi_up_pos],[TRESH_HI 4000], '-m')
%      plot([cross_hi_up_pos cross_lo_down_pos],[4000 4000], '-m')
%      plot([cross_lo_down_pos cross_lo_down_pos],[4000 TRESH_LO], '-m')
%      click_state = 1;
%      myZoom(i,0.2);
%      %ch = kbhit ();
    otherwise
      otherwise_cntr++;
  endswitch
  
  
endfor
axis("auto")
##print the detected clicks positions
click_detect_pos
ax_x1 = click_detect_pos(1)-2500;
if(ax_x1 < 0)
	ax_x1 = 0;
endif
ax_x2 = click_detect_pos(length(click_detect_pos))+3000;
axis([ax_x1 ax_x2 -100 4100])
clear ax_x1 ax_x2

