# cat batch.sh
for pulse in 25 50 100 #1.0 9.0 #1.7320508075688772 5.196152422706632
do
    for aei in 5.0 10.0 12.0
    do
        for aee in 5.0 10.0 12.0
        do
            if ! test -s "*_aee$aeeaei$aeiphi$phipulse$pulse.txt"; then
                ~/python batch_model.py 1.0 0.1 $aee $aei 0.1 2.0 9.0 $pulse
            fi
        done
    done
done