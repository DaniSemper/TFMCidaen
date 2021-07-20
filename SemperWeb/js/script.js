var BASE_URL = 'https://6n8omq8ii0.execute-api.us-east-1.amazonaws.com/dev';

function inputFileChange() {
    var filename = $('#input-image').val().split('\\').pop();
    if (filename.length) {
        $('#input-image').next('.custom-file-label').addClass("selected").html(filename);
        $('#upload-image').prop('disabled', false);
    } else {
        $('#input-image').next('.custom-file-label').removeClass("selected").html('Choose file...');
    }
}

function inputFileClear() {
    $('#input-image').next('.custom-file-label').removeClass("selected").html('Choose file...');
    $('#upload-image').prop('disabled', true);
}

function getSignedUrlAndSend(e) {
    e.preventDefault();

    var filedata = $('#input-image').get()[0].files[0];
    inputFileClear();
    $.ajax({
        type: 'GET',
	url: BASE_URL + '/signed-url'
    })
    .done(function(data) {
        sendFile(data.url, filedata);
        
    })
    .fail(function(err) {
        alert('File NOT uploaded');
    });
    return false;
}




function getPrediction(url,image) {
        
    $.ajax({
        type: 'GET',
	url: BASE_URL + '/upload-prediction/'+ url
    })
    .done(function(data) {
        document.getElementById("myImg").src = image             
        // console.log(data)
        setTimeout(function(){
            document.getElementById("covid").textContent = data['COVID']
            document.getElementById("normal").textContent = data['NORMAL']
            document.getElementById("other").textContent = data['VIRAL']  
              $("div.hidden").fadeOut(1000);                   
           }, 1000); //10 seconds
        
        
        
    })
    .fail(function(err) {
        alert('Error en la predicción');
    });
    return false;
}

function sendFile(url, filedata) {
    
    $.ajax({
        type: 'PUT',
        url: url,
        contentType: 'image/jpeg',
        processData: false,
        data: filedata
    })
    .done(function(e) {
       
        // var splitUrl = url.split('?')[0].split('/');
        var splitUrl = url.split('?')[0]   
        var splitUrl2 = url.split('?')[0].split('/');     
        // var urlPredict = splitUrl[0]+ "//" + splitUrl[2] + "/Analisis/" + "Analisis-"+ splitUrl[4];       
        getPrediction(splitUrl2[4],splitUrl)
       
        
    })
    .fail(function(arguments) {
        alert('File NOT uploaded');
        console.log( arguments);
    })
    

    return false;
}



var wordCloudInterval = null;

    $('#input-image').on('change', inputFileChange);
    $('#upload-image').on('click', getSignedUrlAndSend);
    
    $('#upload-image').on('click', function(e)
    {
        
        $('div.hidden').fadeIn(1000)     
    //     e.preventDefault();
    //     // setTimeout(function(){
    //     //     $("div.hidden").fadeOut(1000);
           
    //     //   }, 20000); //10 seconds
        
    });
   
