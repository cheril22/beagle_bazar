// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable( { "order": [[ 0, "desc" ]] } );
  $('#inq-data-Table').DataTable( { "order": [[ 0, "desc" ]] } );
  $('#purchase-inq-data-table').DataTable( { "order": [[ 0, "desc" ]] } );
  $('#financeTable').DataTable( { "order": [[ 0, "desc" ]] } );
  $('#dealer-schemes-data-Table').DataTable( { "order": [[ 0, "desc" ]],
        "responsive": true,
		"columnDefs": [
		            { responsivePriority: 1, targets: 0 },
		            { responsivePriority: 2, targets: 1 },
		            { responsivePriority: 3, targets: 2 },
		            { responsivePriority: 4, targets: 3 },
		            { responsivePriority: 5, targets: 4 },
		            { responsivePriority: 6, targets: 7 },
		            { responsivePriority: 7, targets: 8 }
		        ]
   } );
  $('#purchase-rewards-data-Table').DataTable( { "order": [[ 0, "desc" ]] } );
});
