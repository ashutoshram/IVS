for i in {1..10}; do 
    echo starting $i; 
    python3 worker.py 2>&1 >/tmp/worker$i.log &
done
