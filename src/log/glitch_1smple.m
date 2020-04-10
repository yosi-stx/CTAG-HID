% glitch_1smple.m
% find the glitches in the recording of the clicker over-sampling.
clear glitches glitchs_points glitchs_5p glitches_5p glitchs_6p glitches_4p glitchs_3p glitches_3p

% glitches = zeros(size(xb));
% glitches = 0;
glitchs_5p = 0;
glitchs_6p = 0;
glitches_5p = 0;
glitchs_4p = 0;
glitches_4p = 0;
glitchs_3p = 0;
glitches_3p = 0;
glitchs_1p = 0;
glitches_1p = 0;
hold on
for j = 10:(rows(xb)-20)
	% ignore the standby time
	if ( b(j,2) > 400 )
	% {
		% if the change from last point is more the X points
		% "filter"  before the beginning of glitch there is a change
		if( abs(b(j-1,2) - b(j,2)) > 2 )
		% {
			if (b(j-1,2) != b(j+9,2))        % sync with glitch start.
			% {
				if (b(j,2) == b(j+10,2))
				% {
					if( abs(b(j-1,2) - b(j,2)) > 5 )
						if( mod(j,10)==1 ) % only on "first" samplings of the over-sampling group...
							plot([j j+10],[b(j,2) b(j+10,2)],'g-.x')
							glitchs_1p++;
							glitches_1p(glitchs_1p) = j;
						endif	
					endif	
					if (b(j+1,2) == b(j+11,2))
					% {
						if (b(j+2,2) ==b (j+12,2))
						% {
								if( (b(j,2) != b(j+1,2)) && (b(j+1,2) != b(j+2,2)) && (abs(b(j,2)-b(j+2,2))>1) ) 
									plot([j j+10],[b(j,2) b(j+10,2)],'g-x')
									plot([j+1 j+11],[b(j+1,2) b(j+11,2)],'y-x')
									plot([j+2 j+12],[b(j+2,2) b(j+12,2)],'k-x')
									if( abs(b(j-1,2) - b(j,2)) > 2  )							% extra "filter" 
									% {
										glitchs_3p++;
										glitches_3p(glitchs_3p) = j;
									% }
									endif	
								endif	
								if (b(j+3,2)==b(j+13,2))
								% {
									plot([j+3 j+13],[b(j+3,2) b(j+13,2)],'b--x')
									if( abs(b(j-1,2) - b(j,2)) > 5 )
									% {
										glitchs_4p++;
										glitches_4p(glitchs_4p) = j;
									% }
									endif	
									if (b(j+4,2)==b(j+14,2))
									% {
										plot([j+4 j+14],[b(j+4,2) b(j+14,2)],'m-.x')
										if (b(j+5,2)==b(j+15,2))
										% {
											plot([j+5 j+15],[b(j+5,2) b(j+15,2)],'c-o')
											glitchs_6p++;
										% }
										endif
										glitchs_5p++;
										glitches_5p(glitchs_5p) = j;
										j = j + 4;
									% }
									endif
								% }
								endif
						% }
						endif
					% }
					endif
				% }
				endif
			% }
			endif
		% }
		endif
	% }
	endif
endfor

% glitchs_points = find(glitches > 10 );
% glitches;
glitchs_3p
glitchs_1p
% glitchs_5p

loop_index = 1;
for i=1:999
	glitch_index = glitches_1p(loop_index);
	% glitch_index = glitches_4p(loop_index);
	glitch_indexes = [glitch_index:glitch_index+4];
	
	y_max = max(b(glitch_indexes,2))+15;
	y_min = min(b(glitch_indexes,2))-15;
	[glitch_index-30 glitch_index+30 y_min y_max];
	i
	axis([glitch_index-30 glitch_index+30 y_min y_max])
	
	% axis([glitches_3p(i)-50 glitches_3p(i)+50 min(b(glitches_3p,2))-30 max(b(glitches_3p,2))+30 ])
	ch = kbhit ();
	if( ch == 'b') 
		loop_index--;
	else
		loop_index++;
	endif
	if( ch == 'q') 
		break;
	endif
endfor
hold off
clear i j glitch_index glitch_indexes y_min y_max ch
clear glitchs_5p 
clear glitchs_6p 
clear glitches_5p
clear glitchs_4p 
clear glitches_4p
clear glitchs_3p 
clear glitches_3p
% clear glitchs_1p 
clear glitches_1p
clear loop_index
