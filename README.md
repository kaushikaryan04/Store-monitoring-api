
To understand the problem see this link -> https://loopxyz.notion.site/Take-home-interview-Store-Monitoring-12664a3c7fdf472883a41457f0c9347d



Wrote a custom script that triggers via python manage.py that add csv files to python models as per requirnments specified in assignment [See here](api/management/commands/importcsv.py)  
To run it run command python manage.py importcsv [filename]

Models with thier relations have also been added

Logic for interpolation is here [completed](api/trigger_functions.py)

End points 
-> trigger_report/<int:store_id>
-> get_report/<str:report_id>




