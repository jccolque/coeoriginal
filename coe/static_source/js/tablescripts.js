$(document).ready(function() {
    $('#table').DataTable( {
        dom: 'Bfrtip',
        "pageLength": 50,
        
        buttons: [
            'excel',
        ]
    } );
} );
