@echo off
cd /d d:\123\cowkb
echo Starting enhancement engine...
C:\Python314\python.exe scripts\discover\enhance_engine.py --batch_size 10 --workers 2
echo Enhancement completed.