# cat batch_short.sh
for phi in 3.0 1.0 9.0 #1.7320508075688772 5.196152422706632
do
    for aee in 0.00001 0.00003 0.00005 0.005 0.01
    do
   	for aei in 0.1 0.3 0.5 0.7 1.0
       	do
 	    if ! test -s "*_aee$aeeaei$aeiphi$phi.txt"; then
            	~/python batch_model_short_str.py 0.0015 0.0002 $aee $aei 0.06 0.02 $phi
            fi
	done
    done
done
