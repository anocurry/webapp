$(document).ready(function() {

  //Initialization
  new WOW().init();
  $('#id_postid').parent().parent().hide();
  initPostForm_closebutton();

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

    function openPostForm() {
        $('#overlay').fadeIn(500);
        $('.postform').removeClass('animated fadeOutDown');
        $('.postform').addClass('animated fadeInUp');
    }

    function initPostForm_closebutton() {
      $('#closebutton').click(function() {
        closePostForm();
        $('#sitename-find').html('');
      })
    }

    function closePostForm() {
      $('#overlay').fadeOut(500);
      $('.error-message').hide();
      $('.postform').removeClass('animated fadeInUp');
      $('.postform').addClass('animated fadeOutDown');
    }

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
             openPostForm();
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
             openPostForm();
             initsitename();
         },
         failure: function(data) {
             alert('Got an error dude');
         }
     });
   });

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

    initsitename();
    function initsitename() {
      //create an empty div element in the td
      $('#id_sitename').parent().append("<div></div>");
      var sitenamelist = $('#id_sitename').parent().find('div');
      sitenamelist.attr('id', 'sitename-list');

      $('#id_sitename').focusout(function() {
        initsitename_find();
        if (!resultsSelected) {  //if you click on anything other than the results
            $("#sitename-list").hide();  //hide the results
          }
      })

      $('#id_sitename').focus(function() {
        $('#sitename-list').show();
      })

      //this is for the dropdown list
      $('#id_sitename').keyup(function() {
        var sitename = $('#id_sitename').val();
        $('#id_sitename').parent().css('position', 'relative');
        var offset = $('#id_sitename').parent().height();
        $.ajax({
            url: '/user/sitenamelist/',
            type: 'get',
            data: {'sitename': sitename},
            success: function(data) {

              var sitenamelist = $('#sitename-list');
              sitenamelist.html(''); //clear the list first

              $.each(data, function(key, value) {
                if (value.count == 1)
                {
                   sitenamelist.append("<div><span>"+value.sitename+"</span>"+value.count+" user</div>");
                 } else {
                   sitenamelist.append("<div><span>"+value.sitename+"</span>"+value.count+" users</div>");
                 }

                var div = sitenamelist.find('div').last();
                div.addClass('sitename-selection');
                div.css('top', offset);
                offset += div.outerHeight();
              })
              var lastdiv = sitenamelist.find('div').last();
              lastdiv.css('border-bottom', '1px solid #ababab');
              lastdiv.css('border-radius', '0px 0px 5px 5px');
              initsitename_selection();

            },
            failure: function(data) {
                alert('Got an error dude');
            }
        });
      })

      $('#sitename-list').hover(function() {
        resultsSelected = true;
      }, function() {
        resultsSelected = false;
      })
    }

    function initsitename_selection() {
      $('.sitename-selection').click(function() {
        $('#id_sitename').val($(this).find('span').html())
        $('#sitename-list').hide();
        initsitename_find();
      })
    }

    function initsitename_find() {
      var sitename = $('#id_sitename').val();
      var offset = $('#id_sitename').parent().height();
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

    function connectionlogo_hovered(embed_a) {
      var connectionlogo_hover = $(this).parent().find('.connectionlogo_hover');
      connectionlogo_hover.hover(function() {
        return true;
      }, function() {
        return false;
      })
    }

    $('.embed_twitter').hover(function() {
      var connectionlogo_hover = $(this).find('.connectionlogo-hover');
      connectionlogo_hover.append("<button class='embed_button'>Latest tweet</button>");
      var thenewbutton = connectionlogo_hover.find('.embed_button');

      thenewbutton.click(function() {
        embed_button = $(this);
        var embed_loading = $(this).parent().parent().parent().find('.embed_loading');
        var screen_name = $(this).parent().find('.embed_siteusername').html();
        embed_loading.html('<br/><i class="fa fa-spinner fa-spin fa-fw" aria-hidden="true"></i> Fetching data from Twitter...');
        $.ajax({
            url: '/user/get_status_twitter',
            type: 'get',
            data: {'screen_name': screen_name},
            success: function(data) {
              //alert(data);
              $('#embed_box').html(data);
              embed_loading.html('');
              openPostForm();
            },
            failure: function(data) {
                alert('Got an error dude');
            }
        })
      })
    }, function() {
        var embed_button = $(this).find('.embed_button');
        embed_button.remove();
    })
 });
