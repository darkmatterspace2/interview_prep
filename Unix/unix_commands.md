# Unix Audit & Scripting Interview Questions for Data Engineers

## Beginner Level

1.  **How do you check the first and last 10 lines of a large file?**
    *   **Answer:**
        *   `head -n 10 filename` (First 10 lines)
        *   `tail -n 10 filename` (Last 10 lines)
        *   **Input:** A file `data.log` with 1000 lines.
        *   **Output:**
            ```
            [2023-10-27 10:00:01] INFO: Started
            ... (8 lines) ...
            [2023-10-27 10:00:10] INFO: Processing
            ```

2.  **What does `grep` do, and how would you case-insensitively search for "ERROR" in a file?**
    *   **Answer:** `grep` searches for text patterns.
        *   Command: `grep -i "error" logfile.txt`
        *   **Input:** `logfile.txt` containing "Info: ok", "Error: failed", "ERROR: fatal".
        *   **Output:**
            ```
            Error: failed
            ERROR: fatal
            ```

3.  **How do you change file permissions to make a script executable?**
    *   **Answer:** Use `chmod`.
        *   Command: `chmod +x script.sh`
        *   **Input:** file `script.sh` with permissions `-rw-r--r--`.
        *   **Output:** `ls -l` now shows `-rwxr-xr-x` (color changes to green in many terminals).

4.  **Explain the difference between `cp`, `mv`, and `rm`.**
    *   **Answer:**
        *   `cp source dest` (Copy), `mv source dest` (Move), `rm source` (Remove).
        *   **Input:** `file1.txt` exists.
        *   **Command:** `cp file1.txt file2.txt`
        *   **Output:** Both `file1.txt` and `file2.txt` exist with same content.

5.  **How do you count the number of records (lines) in a CSV file?**
    *   **Answer:** Use `wc -l`.
        *   Command: `wc -l data.csv`
        *   **Input:** `data.csv` having header + 99 data rows.
        *   **Output:** `100 data.csv`

6.  **What is the difference between `>` and `>>` redirection operators?**
    *   **Answer:** `>` overwrites, `>>` appends.
        *   **Input:** `log.txt` contains "Line 1".
        *   **Command:** `echo "Line 2" >> log.txt`
        *   **Output:** `log.txt` now contains:
            ```
            Line 1
            Line 2
            ```

7.  **How do you list all files, including hidden ones, showing file sizes and permissions?**
    *   **Answer:** `ls -la`.
        *   **Input:** Directory containing `.gitignore` and `main.py`.
        *   **Output:**
            ```
            drwxr-xr-x  .
            drwxr-xr-x  ..
            -rw-r--r--  .gitignore
            -rw-r--r--  main.py
            ```

8.  **How do you check your current directory path?**
    *   **Answer:** `pwd`.
        *   **Input:** User is in `/home/user/projects`
        *   **Output:** `/home/user/projects`

9.  **What command allows you to view a very large file without loading it all into memory/screen?**
    *   **Answer:** `less filename`.
        *   **Input:** `access.log` (5GB).
        *   **Output:** Interactive screen showing the top of the file, allowing scrolling with arrow keys.

10. **How do you verify the exit status of the previously executed command?**
    *   **Answer:** `echo $?`.
        *   **Input:** Run `ls non_existent_file`.
        *   **Command:** `echo $?`
        *   **Output:** `2` (or non-zero value indicating error).

## Medium Level

11. **How do you find the 3rd column of a comma-separated file?**
    *   **Answer:** `awk -F, '{print $3}'`.
        *   **Input:** `file.csv`: `1,John,NYC`
        *   **Output:** `NYC`

12. **How do you replace all occurrences of the string "NULL" with empty space in a file?**
    *   **Answer:** `sed -i 's/NULL//g'`.
        *   **Input:** `data.csv`: `1,John,NULL,NYC`
        *   **Output:** `data.csv` becomes: `1,John,,NYC`

13. **How do you find all files ending with `.json` in the `/data` directory and its subdirectories?**
    *   **Answer:** `find /data -name "*.json"`.
        *   **Input:** Directory structure with multiple file types.
        *   **Output:**
            ```
            /data/users/user1.json
            /data/config/settings.json
            ```

14. **The disk is full. How do you check which directory is consuming the most space?**
    *   **Answer:** `du -ah . | sort -rh | head -n 5`.
        *   **Input:** Current directory with various subfolders.
        *   **Output:**
            ```
            5.0G    .
            2.0G    ./logs
            1.5G    ./data
            ```

15. **How do you debug a shell script that is failing?**
    *   **Answer:** Run with `bash -x script.sh`.
        *   **Input:** `script.sh` that sets `VAR=hello`.
        *   **Output:**
            ```
            + VAR=hello
            + echo hello
            hello
            ```

16. **How do you run a long-running process in the background so it survives if your session disconnects?**
    *   **Answer:** `nohup ./script.sh &`.
        *   **Input:** Script that takes 2 hours.
        *   **Output:** `[1] 12345` (Returns PID, keeps running in background).

17. **How do you combine two commands, using the output of the first as input to the second?**
    *   **Answer:** Pipe `|`.
        *   **Input:** `logs.txt` with 50 lines containing "ERROR".
        *   **Command:** `grep "ERROR" logs.txt | wc -l`
        *   **Output:** `50`

18. **How do you archive and compress a directory `logs/` for backup?**
    *   **Answer:** `tar -czvf backup.tar.gz logs/`.
        *   **Input:** Directory `logs/` containing `a.log`, `b.log`.
        *   **Output:** Creates `backup.tar.gz`. Terminal shows:
            ```
            logs/
            logs/a.log
            logs/b.log
            ```

19. **How do you remove duplicate lines from a sorted file?**
    *   **Answer:** `uniq`.
        *   **Input:** `sorted.txt`: `A, A, B`.
        *   **Command:** `uniq sorted.txt`
        *   **Output:** `A, B`.

20. **How do you iterate through all files in a directory and move them to an archive folder?**
    *   **Answer:** `for` loop.
        *   **Input:** `file1.csv`, `file2.csv` in current dir.
        *   **Command:** `for f in *.csv; do mv "$f" archive/; done`
        *   **Output:** Current dir is empty of csvs; `archive/` now contains them.

## Advanced Level

21. **How do you schedule a script to run every day at 2 AM?**
    *   **Answer:** `crontab -e`.
        *   **Input:** Edit mode opens.
        *   **Entry:** `0 2 * * * /home/user/script.sh`
        *   **Output:** Script runs automatically at 02:00 system time.

22. **What is `xargs` and why is it useful in data engineering?**
    *   **Answer:** Converts stdin to arguments.
        *   **Command:** `find . -name "*.tmp" | xargs rm`
        *   **Input:** `find` returns `a.tmp`, `b.tmp`.
        *   **Output:** Executes `rm a.tmp b.tmp`. Files are deleted.

23. **How do you check for zombie processes or high CPU usage?**
    *   **Answer:** `top` or `ps`.
        *   **Command:** `top`
        *   **Output:** Dashboard showing `PID 1234 user 99% CPU python`.

24. **Write a one-liner to sum up the values in the 3rd column of a CSV file.**
    *   **Answer:** `awk`.
        *   **Input:** `sales.csv`: `1,TV,500\n2,Radio,200`
        *   **Command:** `awk -F, '{s+=$3} END {print s}' sales.csv`
        *   **Output:** `700`

25. **How do you efficiently check if a variable exists or is empty in a script?**
    *   **Answer:** `if [ -z "$VAR" ]`.
        *   **Input:** `VAR=""`
        *   **Output:** Echoes "Empty" if logic handles it.

26. **What is the difference between Hard Links and Symbolic (Soft) Links?**
    *   **Answer:**
        *   **Hard Link:** `ln A B`. Deleting A, B still has content.
        *   **Soft Link:** `ln -s A B`. Deleting A, B is broken.
        *   **Output:** `ls -l` shows `B -> A` for soft link.

27. **How do you watch a log file in real-time as it is being written to?**
    *   **Answer:** `tail -f`.
        *   **Command:** `tail -f app.log`
        *   **Input:** App writes "New Request" to log.
        *   **Output:** "New Request" appears on screen immediately.

28. **How do you compare two sorted files line by line?**
    *   **Answer:** `comm file1 file2`.
        *   **Input:** `f1: A, B`; `f2: A, C`
        *   **Output:**
            ```
                    B
                            C
            A
            ```
            (Col 1: unique to f1, Col 2: unique to f2, Col 3: common).

29. **Explain the usage of `ssh` and `scp`.**
    *   **Answer:**
        *   **Command:** `scp data.csv user@remote:/tmp`
        *   **Output:** Progress bar `100% 50KB` showing file transfer to remote server.

30. **How do you monitor memory usage to check for a "Memory Leak" or OOM issue?**
    *   **Answer:** `free -m`.
        *   **Command:** `free -m`
        *   **Output:**
            ```
                  total        used        free
            Mem:   16000       15000         500
            ```
            (Shows high memory usage).
