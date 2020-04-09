% glitch.m
% find the glitches in the recording of the clicker over-sampling.
clear glitches glitchs_points glitchs_5p glitches_5p glitchs_6p glitches_4p glitchs_3p glitches_3p

glitches = zeros(size(xb));
glitchs_5p = 0;
glitchs_6p = 0;
glitches_5p = 0;
glitchs_4p = 0;
glitches_4p = 0;
glitchs_3p = 0;
glitches_3p = 0;
hold on
for j = 10:(rows(xb)-20)
	% ignore the standby time
	if ( b(j,2) > 400 )
		% if the change from last point is more the 2 points
		if( abs(b(j-1,2) - b(j,2)) > 2 )
			if ( b(j-1,2) != b(j+9,2))
				if ( b(j,2) == b(j+10,2))
					if (b(j+1,2)==b(j+11,2))
						if (b(j+2,2)==b(j+12,2))
							% if(b(j,2) > 1000)
								glitches(j)= b(j,2);
								plot([j j+10],[b(j,2) b(j+10,2)],'g-x')
								plot([j+1 j+11],[b(j+1,2) b(j+11,2)],'y-x')
								plot([j+2 j+12],[b(j+2,2) b(j+12,2)],'k-x')
								if( abs(b(j-1,2) - b(j,2)) > 5 )
									glitchs_3p++;
									glitches_3p(glitchs_3p) = j
								endif	
								if (b(j+3,2)==b(j+13,2))
									plot([j+3 j+13],[b(j+3,2) b(j+13,2)],'b--x')
									if( abs(b(j-1,2) - b(j,2)) > 5 )
										glitchs_4p++;
										glitches_4p(glitchs_4p) = j
									endif	
									if (b(j+4,2)==b(j+14,2))
										plot([j+4 j+14],[b(j+4,2) b(j+14,2)],'m-.x')
										if (b(j+5,2)==b(j+15,2))
											plot([j+5 j+15],[b(j+5,2) b(j+15,2)],'c-o')
											glitchs_6p++
										endif
										glitchs_5p++;
										glitches_5p(glitchs_5p) = j;
										j = j + 4;
									endif
								endif
							% endif
						endif
					endif
				endif
			endif
		endif
	endif
endfor

glitchs_points = find(glitches > 10 );
glitchs_3p
glitchs_4p
glitchs_5p

for i=1:999
	% axis([glitches_4p(i)-50 glitches_4p(i)+50 b(glitches_4p(i),2)-30 b(glitches_4p(i),2)+30 ])
	axis([glitches_3p(i)-50 glitches_3p(i)+50 min(b(glitches_3p,2))-30 max(b(glitches_3p,2))+30 ])
	ch = kbhit ()
	if( ch == 'q') 
		break;
	endif
endfor
hold off
