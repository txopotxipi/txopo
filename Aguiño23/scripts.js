// Galería de fotos
$(document).ready(function(){

    $('.gallery-item').click(function(){
      let images = [];
      
      images.push('img1.jpg');
      images.push('img2.jpg');
      // Resto de imágenes
      
      let gallery = $(this).attr('data-gallery');
      
      $.photos({
        images: images,
        gallery: gallery,
        onClose: function(){
          $(document).unbind('keydown');
        }
      });
      
      return false;
      
    });
    
  });
  
  
  // Videos de Youtube
  $('.video').click(function() {
    let videoId = $(this).attr('href');
    
    $(this).replaceWith('<iframe src="' + videoId + '?autoplay=1&showinfo=0"></iframe>');
    
    return false;
  });

  $('.slider').slick({
    infinite: true,
    slidesToShow: 1, 
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000
  });