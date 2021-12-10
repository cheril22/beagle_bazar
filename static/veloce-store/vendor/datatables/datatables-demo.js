// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable( { "order": [[ 0, "desc" ]] } );
  $('#inq-data-Table').DataTable( { "order": [[ 0, "desc" ]] } );
  $('#purchase-inq-data-table').DataTable( { "order": [[ 0, "desc" ]] } );
  $('#financeTable').DataTable( { "order": [[ 0, "desc" ]] } );
  $('#dealer-rewards-data-Table').DataTable( { "order": [[ 0, "desc" ]] } );
  $('#purchase-rewards-data-Table').DataTable( { "order": [[ 0, "desc" ]] } );
});
