$(document).ready(function() {
    $('#table thead tr').clone(true).appendTo('#table thead');
    $('#table thead tr:eq(1) th').each( function (i) {
        var title = $(this).text();
        $(this).html( '<input type="text" placeholder="'+title+'" />' );
 
        $( 'input', this ).on( 'keyup change', function () {
            if ( table.column(i).search() !== this.value ) {
                table
                    .column(i)
                    .search( this.value )
                    .draw();
            }
        } );
    } );

    $("tr:first").css("visibility", "hidden");

    var table = $('#table').DataTable( {
        dom: 'Bfrtip',
        "pageLength": 50,

        //orderCellsTop: true,
        fixedHeader: true,

        buttons: [
            'excel',
        ]
    } )
})