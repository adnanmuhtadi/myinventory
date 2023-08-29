$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})



$(document).ready(function () {

  NProgress.start();
  NProgress.done();

  $(".datetimeinput").datepicker({
      changeYear: true,
      changeMonth: true,
      dateFormat: 'yy-mm-dd'
  });
});




