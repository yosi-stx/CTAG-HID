function showClicks( click_detect_pos,zoo )
% showClicks( click_detect_pos, 0.1 )
for j=click_detect_pos
  myZoom(j,zoo);
  kbhit();
endfor
endfunction
