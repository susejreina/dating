$(document).ready(function(){
    $("#id_username").keypress(function(e){
        //Only letters and numbers
        e.preventDefault();
        var numberAscci = e.keyCode;
        if ((numberAscci>=48 && numberAscci<=57) || (numberAscci>=65 && numberAscci<=90) || (numberAscci==8)|| (numberAscci==46)){
            return true;
        }
        else{
            return false;
        }
    });
});
