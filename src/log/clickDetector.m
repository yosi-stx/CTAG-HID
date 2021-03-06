% clickDetector.m
% finds a click signal in a vector.
sig = b(1:x2,2);
hold on

TRESH_LO = 700;
TRESH_HI = 2800;
##MAX_HI_STATE = 180;
MAX_HI_STATE = 290;
%MAX_FALL_DOWN = 150; % enable 30 ms from Hi to Low.
MAX_FALL_DOWN = 175; % enable 30 ms from Hi to Low.
LINE_SIMB = 250;
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
      % check cross of TRESH_LO
      if( sig(i-1) <= TRESH_LO && sig(i) > TRESH_LO )
##        myZoom(i,0.2);
        click_state++;
        cross_lo_up_pos = i;
      endif
    case {2,3,4} % 3 rises in signal. -> filter out to fast rise.
      if( sig(i-1) <= sig(i) )
##        myZoom(i,0.2);
##        click_state++;
        click_state = 5;
      else
##        myZoom(i,0.2);
        fail_cntr++;
        fail_reason(fail_cntr) = click_state;
        fail_pos(fail_cntr) = i;
        click_state = 1;
        plot_ix(i,LINE_SIMB/2,sig)
      endif
    case 5  % getting to the high point ...
      if( sig(i) > TRESH_HI )
        click_state++;
        cross_hi_up_pos = i;
      endif
    case 6  % is is enough to be only one sample above TRESH_HI
      if( sig(i) < TRESH_HI )
        click_state++;
        cross_hi_down_pos = i;
      endif
    case 7
      if( cross_hi_down_pos - cross_hi_up_pos < MAX_HI_STATE )
        click_state++;
      else
        plot_ix(i,LINE_SIMB,sig)
        fail_cntr++;
        fail_reason(fail_cntr) = click_state;
        fail_pos(fail_cntr) = i;
        click_state = 1;
      endif
    case 8
      if( sig(i) < TRESH_LO )
        click_state++;
        cross_lo_down_pos = i;
      endif
    case 9
      if( sig(i) < TRESH_LO )
        if( cross_lo_down_pos -  cross_hi_down_pos <= MAX_FALL_DOWN )
          click_state++;
        else
          plot_ix(i,LINE_SIMB,sig)
          fail_cntr++;
          fail_reason(fail_cntr) = click_state;
          fail_pos(fail_cntr) = i;
          click_state = 1;
        endif
      endif
    case 10
      % we have a click !!
      click_index++;
      click_detect_pos(click_index) = i;
      click_hi_pos(click_index) = cross_hi_up_pos;
      % line indication of click:
      %plot([cross_hi_up_pos i],[sig(cross_hi_up_pos) sig(i)], '-m')
      % rectangle indication of click:
      plot([cross_hi_up_pos cross_hi_up_pos],[TRESH_HI 4000], '-m')
      plot([cross_hi_up_pos cross_lo_down_pos],[4000 4000], '-m')
      plot([cross_lo_down_pos cross_lo_down_pos],[4000 TRESH_LO], '-m')
      click_state = 1;
      myZoom(i,0.2);
      %ch = kbhit ();
    otherwise
      otherwise_cntr++;
  endswitch
  
  
endfor
axis("auto")
##print the detected clicks positions
click_detect_pos


