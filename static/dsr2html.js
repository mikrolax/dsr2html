$(document).ready(function() 
    { 
      if($("#globaltable").find('tbody:first tr').length > 0){
           $("#globaltable").tablesorter(); 
	}
      
      if($("#testtable").find('tbody:first tr').length > 0){
           $("#testtable").tablesorter(); 
	}
    } 
); 

