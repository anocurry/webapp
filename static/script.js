$(document).ready(function() {

  //Initialization
  new WOW().init();
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
             $('.postform').removeClass('animated bounceOut');
             $('.postform').addClass('animated bounceIn');
             initsitename();
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
             $('.postform').removeClass('animated bounceOut');
             $('.postform').addClass('animated bounceIn');
             initsitename();
         },
         failure: function(data) {
             alert('Got an error dude');
         }
     });
   });

   $('#closebutton').click(function() {
     $('#overlay').fadeOut(500);
     $('.error-message').hide();
     $('.postform').removeClass('animated bounceIn');
     $('.postform').addClass('animated bounceOut');
     $('#sitename-find').html('');
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
   $('#connectedbutton').mouseenter(function() {
     var t = $(this);
     var i = t.find('i');
     i.removeClass('fa-check');
     i.addClass('fa-times');
     t.find('span').html(' Disconnect');
   })

   $('#connectedbutton').mouseleave(function() {
     var t = $(this);
     var i = t.find('i');
     i.removeClass('fa-times');
     i.addClass('fa-check');
     t.find('span').html(' Connected');
   })

   $('#requestsentbutton').mouseenter(function() {
     var t = $(this);
     var i = t.find('i');
     i.removeClass('fa-check');
     i.addClass('fa-times');
     t.find('span').html(' Cancel request');
   })

   $('#requestsentbutton').mouseleave(function() {
     var t = $(this);
     var i = t.find('i');
     i.removeClass('fa-times');
     i.addClass('fa-check');
     t.find('span').html(' Request sent');
   })

    $('.post-bottomright').mouseenter(function() {
        $(this).find('span').removeClass('transparent');
    });

    $('.post-bottomright').mouseleave(function() {
        $(this).find('span').addClass('transparent');
    });

    $('.postborder').mouseenter(function() {
      $(this).find('.post-postdate').removeClass('transparent');
    })

    $('.postborder').mouseleave(function() {
      $(this).find('.post-postdate').addClass('transparent');
    })

    function initsitename() {
      $('#id_sitename').change(function() {
        var sitename = $(this).val();
        $.ajax({
            url: '/user/sitenamefind/',
            type: 'get',
  				  data: {'sitename': sitename},
            success: function(data) {
              $('#sitename-find').html(data);
            },
            failure: function(data) {
                alert('Got an error dude');
            }
        });
      })
    }

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
              $('.contentboxbg').attr('style', 'background:url("'+this.src+'") no-repeat center;');
              $('#bgimginput').css('opacity', '0');
              $('#bgimginputbutton').removeClass('transparent');
              $('#bgimginputbutton').addClass('animated bounceIn');
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
              if (this.width > this.height) { /* 170 - 12 */
                this.width = Math.floor(this.width / this.height * 158);
                this.height = 158;
              } else {
                this.height = Math.floor(this.height / this.width * 158);
                this.width = 158;
              }
              s = "background:url('"+this.src+"') no-repeat center; background-size:"+this.width+"px "+this.height+"px;";
              $('#contentprofileimg').attr('style', s);
              $('#profileimginput').css('opacity', '0');
              $('#profileimginputbutton').removeClass('transparent');
              $('#profileimginputbutton').addClass('animated bounceIn');
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
