% example: myZoom(i,.2)
function retval = myZoom(point,scale)
	axis([point-50/scale point+50/scale -2 4050])
	plot([point point],[-2 4050],'y-.')
endfunction