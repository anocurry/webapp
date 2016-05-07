$(document).ready(function() {
  //hide the post id at the start
  $('#id_postid').parent().parent().hide();

  function animationHover(element, animation) {
   element = $(element);
   element.hover(
       function() {
           element.addClass('animated ' + animation);
       },
       function(){
           //wait for animation to finish before removing classes
           window.setTimeout( function(){
               element.removeClass('animated ' + animation);
           }, 2000);
       });
   };

   function animationClick(clicked, target, animation){
    clicked = $(clicked);
    target = $(target);
    clicked.click(
        function() {
            target.addClass('animated ' + animation);
            //wait for animation to finish before removing classes
            window.setTimeout( function(){
                target.removeClass('animated ' + animation);
            }, 2000);

        });
    };

   $('.editpostbutton').click(function() {
     //alert("clicked " + $(this).attr('id'));
     postid = $(this).attr('id');
     $.ajax({
         url: '/user/' + postid + '/newpostform',
         type: 'get',
         success: function(data) {
             //alert(data);
             $('#theform').html(data);
             $('#id_postid').val(postid);
             $('.postformheader h1').html("Edit account information");
             $('#id_postid').parent().parent().hide();
             $('#overlay').fadeIn(500);
         },
         failure: function(data) {
             alert('Got an error dude');
         }
     });
   });

   $('#newpostbutton').click(function() {
     $.ajax({
         url: '/user/newpostform',
         type: 'get',
         success: function(data) {
             //alert(data);
             $('#theform').html(data);
             $('#id_postid').val('');
             $('.postformheader h1').html("Add account information");
             $('#id_postid').parent().parent().hide();
             $('#overlay').fadeIn(500);
         },
         failure: function(data) {
             alert('Got an error dude');
         }
     });
   });

   $('#closebutton').click(function() {
     $('#overlay').fadeOut(500);
   })

   $('.deletepostbutton').click(function() {
    // alert($(this).parent().find('input[name="deletepostid"]').val());
     if (confirm("Are you sure you want to delete this?")) {
       $(this).submit();
     } else {
       return false;
     }
   });

   //animationHover('#connectedbutton', 'bounceIn');

    $('.post-bottomright').mouseenter(function() {
        $(this).find('span').removeClass('transparent');
        $(this).find('span').removeClass('animated bounceOut');
        $(this).find('span').addClass('animated bounceIn');
    });

    $('.post-bottomright').mouseleave(function() {
        $(this).find('span').removeClass('animated bounceIn');
        $(this).find('span').addClass('animated bounceOut');
    });

    $('#bgimginput').change(function() {
  		if (this.files[0].size > 1500000) {
        //display errors here
        alert("The file size is too big. Please keep the file size less than 1.5MB.");
  		}
      else {
        var F = this.files[0];
        var reader = new FileReader();
        var image = new Image();
        reader.onload = function(_file) {
            image.src    = _file.target.result;              // url.createObjectURL(file);
            image.onload = function() {
              $('.contentboxbg').attr('style', 'background:url("'+this.src+'") no-repeat fixed center;');
              $('#bgimginput').css('opacity', '0');
              $('#bgimginputbutton').removeClass('transparent');
            };
            image.onerror= function() {
              alert('Invalid file type: '+ F.type);
            };
        }
        reader.readAsDataURL(F);
      }
    });

    $('#profileimginput').change(function() {
  		if (this.files[0].size > 300000) {
        //display errors here
        alert("The file size is too big. Please keep the file size less than 300KB.");
  		}
      else {
        var F = this.files[0];
        var reader = new FileReader();
        var image = new Image();
        reader.onload = function(_file) {
            image.src    = _file.target.result;              // url.createObjectURL(file);
            image.onload = function() {
              $('#contentprofileimg').attr('src', this.src);
              $('#profileimginput').css('opacity', '0');
              $('#profileimginputbutton').removeClass('transparent');
            };
            image.onerror= function() {
              alert('Invalid file type: '+ F.type);
            };
        }
        reader.readAsDataURL(F);
      }
    });

    $('#bgimginput').mouseenter(function() {
      $('.contentboxbgoverlay').css('background-color', 'rgba(0,0,0,0.5)');
      $('.bgimginputicon').css('opacity', 1);
    })

    $('#bgimginput').mouseleave(function() {
      $('.contentboxbgoverlay').css('background-color', 'transparent');
      $('.bgimginputicon').css('opacity', 0);
    })

    $('#profileimginput').mouseenter(function() {
      $('.profileimginputdiv').css('background-color', 'rgba(0,0,0,0.5)');
      $('.profileimginputicon').css('opacity', 1);
    })

    $('#profileimginput').mouseleave(function() {
      $('.profileimginputdiv').css('background-color', 'transparent');
      $('.profileimginputicon').css('opacity', 0);
    })
 });
