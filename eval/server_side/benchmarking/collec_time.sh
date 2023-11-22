find . -type f -name slurm-3914*.err -exec sh -c 'if tail -n 10  | grep -q real|user|sys; then echo ; tail -n 3 ; echo; fi' _ {} \; | grep real > times.txt
