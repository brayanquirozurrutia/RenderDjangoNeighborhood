const multipleItemCarousel = document.querySelector('#carouselzonas');

if(window.matchMedia("(min-width:576px)").matches) {
    const carousel = new bootstrap.Carousel(multipleItemCarousel, {
        interval: false
    })

    var carouselWidth = $('.carousel_iner')[0].scrollWidth;
    var cardWidth = $('.carousel_item').width();
    var scrollPosition = 0;

    $('.siguiente').on('click', function(){
        if(scrollPosition < (carouselWidth - (cardWidth * 4))){
            scrollPosition = scrollPosition + cardWidth;
            $('.carousel_iner').animate({scrollLeft:
                scrollPosition},1000);
        }
    });

    $('.anterior').on('click', function(){
        if(scrollPosition > 0){
            scrollPosition = scrollPosition - cardWidth;
            $('.carousel_iner').animate({scrollLeft:
                scrollPosition},1000);
        }
    });
} else {
    $(multipleItemCarousel).addClass('slide')
}