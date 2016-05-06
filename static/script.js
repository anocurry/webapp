$(document).ready(function() {
  //hide the post id at the start
  $('#id_postid').parent().parent().hide();
  //$('.postform').addClass('animated bounceIn');

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

   animationHover('#connectedbutton', 'bounceIn');
 });
