//
// Tooptip styling
//
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})



$(document).ready(function () {
  // Progress bar for when the page loads
  NProgress.start();
  NProgress.done();

  //
  $(".datetimeinput").datepicker({
      changeYear: true,
      changeMonth: true,
      dateFormat: 'yy-mm-dd'
  });
});

