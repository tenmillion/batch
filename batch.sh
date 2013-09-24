# cat batch.sh
for phi in 3.0 1.0 9.0 #1.7320508075688772 5.196152422706632
do
    for aee in 0.1 0.15 0.2 0.215 0.25
    do
   	for aei in 0.1 0.15 0.2 0.215 0.25
       	do
	    for pulse in 60 70 80
       	    do
                if ! test -s "*_aee$aeeaei$aeiphi$phipulse$pulse.txt"; then
                    ~/python batch_model.py 1.0 0.1 $aee $aei 0.06 0.02 $phi $pulse
                fi
            done
        done
    done
done
