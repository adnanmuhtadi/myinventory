// Room Delete

function deleteRoomConfirmation(roomName, deleteUrl) {
  const swalWithBootstrapButtons = Swal.mixin({
    customClass: {
      confirmButton: 'btn btn-success',
      cancelButton: 'btn btn-danger'
    },
    buttonsStyling: false
  });

  swalWithBootstrapButtons.fire({
    title: `You are about to delete the room "${roomName}". This action cannot be undone.`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Yes, delete it!',
    cancelButtonText: 'No, cancel',
    reverseButtons: true
  }).then((result) => {
    if (result.isConfirmed) {
      // Use AJAX to call the delete_room view
      $.ajax({
        type: 'POST',
        url: deleteUrl,
        headers: {
          'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function (data) {
          swalWithBootstrapButtons.fire('Deleted!', data.message, 'success');

        // Remove the deleted room's row from the table
          const roomId = data.room_id;
          $('#room-' + roomId).remove();
          // Delay the page reload by 2 seconds
          setTimeout(function () {
            location.reload();
          }, 100); // 2000 milliseconds = 2 seconds
        },
        error: function (error) {
          swalWithBootstrapButtons.fire('Error', 'An error occurred while deleting the room.', 'error');
        }
      });
    } else if (result.dismiss === Swal.DismissReason.cancel) {
      swalWithBootstrapButtons.fire('Cancelled', 'Your room is safe :)', 'info');
    }
  });
}

// Location Delete 

function deleteLocationConfirmation(locationName, deleteUrl) {
  const swalWithBootstrapButtons = Swal.mixin({
    customClass: {
      confirmButton: 'btn btn-success',
      cancelButton: 'btn btn-danger'
    },
    buttonsStyling: false
  });

  swalWithBootstrapButtons.fire({
    title: `You are about to delete the location "${locationName}". This action cannot be undone.`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Yes, delete it!',
    cancelButtonText: 'No, cancel',
    reverseButtons: true
  }).then((result) => {
    if (result.isConfirmed) {
      // Use AJAX to call the delete_location view
      $.ajax({
        type: 'POST',
        url: deleteUrl,
        headers: {
          'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function (data) {
          swalWithBootstrapButtons.fire('Deleted!', data.message, 'success');

        // Remove the deleted location's row from the table
          const locationId = data.location_id;
          $('#location-' + locationId).remove();
          // Delay the page reload by 2 seconds
          setTimeout(function () {
            location.reload();
          }, 100); // 1000 milliseconds = 1 seconds
        },
        error: function (error) {
          swalWithBootstrapButtons.fire('Error', 'An error occurred while deleting the location.', 'error');
        }
      });
    } else if (result.dismiss === Swal.DismissReason.cancel) {
      swalWithBootstrapButtons.fire('Cancelled', 'Your location is safe :)', 'info');
    }
  });
}