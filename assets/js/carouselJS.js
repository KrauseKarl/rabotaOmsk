var ItemCarousel = document.getElementById('www')
if (window.matchMedia("(min-width:576px)").matches) {
  var carousel = new bootstrap.Carousel(ItemCarousel, {
    interval: 800,
    wrap: true,
    touch: true,
    cycle:true
  });
  var carouselWidth = $("#www-inner")[0].scrollWidth;
  var cardWidth = $(".carousel-item").width();
  var scrollPosition = 0;
  $("#www-next").on("click", function () {
    if (scrollPosition < carouselWidth - cardWidth) {
      scrollPosition = scrollPosition + cardWidth;
      console.log(".carousel-control-next")
      $("#www-inner").animate({ scrollLeft: scrollPosition }, 800);
    }
  });
  $("#www-prev").on("click", function () {
    if (scrollPosition > 0) {
      scrollPosition = scrollPosition - cardWidth;
      $("#www-inner").animate({ scrollLeft: scrollPosition }, 800);
    }
  });
} else {
  $(ItemCarousel).addClass("slide");
};




var YTC = document.getElementById('ytubeCarousel')

if (window.matchMedia("(min-width:576px)").matches) {
  const carouseYTC = new bootstrap.Carousel(YTC, {
    interval: 800,
    wrap: true,
    touch: true,
    cycle:true
  });

  var carouselWidthYTC = $(".inner-ytube")[0].scrollWidth;
  var cardWidthYTC = $(".item-ytube").width();

  var scrollPositionYTC = 0;

  $("#next-ytube").on("click", function () {
    if (scrollPositionYTC < carouselWidthYTC - cardWidthYTC * 4) {
      scrollPositionYTC = scrollPositionYTC + cardWidthYTC;
        console.log(".inner-ytube")
      $(".inner-ytube").animate({ scrollLeft: scrollPositionYTC }, 800);
    }
  });
  $("#prev-ytube").on("click", function () {
    if (scrollPositionYTC > 0) {
      scrollPositionYTC = scrollPositionYTC - cardWidthYTC;
      $(".inner-ytube").animate({ scrollLeft: scrollPositionYTC }, 800);
    }
  });
} else {
  $(YTC).addClass("slide");
};
