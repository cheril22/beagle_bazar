$(document).ready(function(){
    var promo_code_status = true;
    $(".menu-item").click(function (e) {
        e.stopPropagation();
        $(".menu-item").removeClass("active");
        $(this).addClass("active");
    });
    $("#txtSearch").autocomplete({
        source: "/search/",
        minLength: 2,
        appendTo: ".search-box",
        open: function(){
            setTimeout(function () {
                // $('.ui-autocomplete').css("left","450px");
            }, 3000);
        }
    });

    if ($('.sell-with-us').length > 0){
        $('.sell-with-us').click(function(){
            $('#SellWithUsModal').modal('show');
        });
    }

    if ($('.compare-products').length > 0){
        $('.compare-products').click(function(){
            var level = $(this).data('check-level');
            console.log(level)
            $('#CompareProdModal').modal('show');
        });
    }

    if ($('.admin-approval').length > 0){
        $('.admin-approval').click(function(){
            var level = $(this).data('check-level');
            $('#check_level_approval').text(level);
            $('#AdminApprovalModal').modal('show');
        });
    }


    if ($('.list-your-products').length > 0){
        $.ajax({
            url: "/check-auth/",
            dataType: 'json',
            success: function (data) {
                if (!data.status)
                {
                    $(".list-your-products").attr("href", data.url);
                }
            }
        });
    }
    var product_id_for_inquiry = 0;
    $(document).on("click",".inq-btn",function(e) {
        product_id_for_inquiry = $(this).data('product-id');
        var prodtImg = '';
        var prodtTitle = '';
        if ($(this).parent().parent().find('img').attr('src')){
            prodtImg = $(this).parent().parent().find('img').attr('src');
        }
        else{
            prodtImg = $('.slider').find('img').attr('src');
        }
        if($(this).parent().parent().find('.title').text()){
            prodtTitle = $(this).parent().parent().find('.title').text();
        }
        else{
            prodtTitle = $('.product-name').text();
        }
        $('.product-img').attr('src', prodtImg);
        $('.product-name').text(prodtTitle);
        if (promo_code_status == true){
            $('.inquiry-error').remove();
            $("#id_name").val('');
            $("#id_email").val('');
            $("#id_inquiry_message").val('');
            $.ajax({
                url: '/get-inquiry-form/',
                dataType: 'json',
                success: function (data) {
                    if ($('#id_inquiry_message').length <= 0){
                        if (data.status){
                            var form = '<div class="form-group">' + data.form + '</div>';
                            $("#inq-frm").append(form);
                        }
                    }
                }
            });
        }
    })
    $(document).on("submit", "#submit-inquiry", function (e) {
        e.preventDefault();
        var form = $(this).closest("form");
        $.ajax({
            type: 'POST',
            url: form.attr("action"),
            data: form.serialize() + "&product_id=" + product_id_for_inquiry,
            dataType: 'json',
            success: function (data) {
                if(data.status){
                    if($('.alert-success').length > 0){
                        $('.alert-success').remove();
                        if($('.search').find().length > 0){
                            $('<div class="alert alert-success alert-dismissible fade show" role="alert"><strong>Success!</strong>'+ data.message +'<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>').insertAfter(".search");
                        }
                        else{
                            $('<div class="alert alert-success alert-dismissible fade show" style="margin-bottom: 10px !important;" role="alert"><strong>Success!</strong>'+ data.message +'<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>').insertAfter(".breadcrumb");
                        }
                        $('#inquiryModal').modal('toggle');
                    }
                    else{
                        if($('.search').find().length > 0){
                            $('<div class="alert alert-success alert-dismissible fade show" role="alert"><strong>Success!</strong>'+ data.message +'<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>').insertAfter(".search");
                        }
                        else{
                            $('<div class="alert alert-success alert-dismissible fade show" style="margin-bottom: 10px !important;" role="alert"><strong>Success!</strong>'+ data.message +'<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>').insertAfter(".breadcrumb");
                        }
                        $('#inquiryModal').modal('toggle');
                    }
                }
                else{
                    $('.inquiry-error').remove();
                    var error = ''
                    $.each(data.message, function(key, value) { error = value + "<br>" });
                    if ($('.inquiry-error').length <= 0){
                        $('<div class="alert alert-danger inquiry-error" role="alert">'+ error +'</div>').insertBefore("#inq-frm");
                    }
                }
            }
        })
    })
    $("#ytWidget").click(() => {
        $('#yt-widget .yt-listbox__col').children('.yt-listbox__cell').appendTo('.yt-listbox__col:first');
        $('#ytWidget ul').not(':first').remove();
    });
    var promo_product_id = 0;
    var max_price = 0;
    $(document).on("change",".get-promo-code",function(e) {
        promo_product_id = $(this).next().val();
        getPrice(promo_product_id);
        if(this.checked) {
            $(this).closest('.gift-card-block').after('<form class="form-inline promo-code-form"><div class="p-0 promo-code-block"><input type="text" class="form-control col-md-8 promo-code" maxlength=12 placeholder="Promo Code"><button type="button" class="btn btn-primary check-promo-code">Submit</button></div></form>');
//            $('.gift-card-block').after('<form class="form-inline promo-code-form"><div class="p-0 promo-code-block"><input type="text" class="form-control col-md-8 promo-code" maxlength=12 placeholder="Promo Code"><button type="button" class="btn btn-primary check-promo-code">Submit</button></div></form>');
            promo_code_status = false;
        }
        else{
            promo_code_status = true;
            $(this).closest('.gift-card-block').next('.promo-code-form').remove();
        }
    });
    $(document).on("click",".check-promo-code",function(e) {
        var coupon_code = $(this).parent().find("input").val();
        $.ajax({
            url: '/validate-promo-code/',
            data: {
                'coupon_code': coupon_code,
                'product_id': promo_product_id
            },
            dataType: 'json',
            success: function (data) {
                if (data.status){
                    $('.max-amt-' + promo_product_id).text(data.amx_amt);
                    $('.invalid-promo-code').remove()
                    if ($('.valid-promo-code').length <= 0){
                        $('.promo-code-block').after('<div class="valid-feedback d-block valid-promo-code">'+ data.msg +'</div>');
                    }
                    promo_code_status = true;
                    if (data.discount_type == 1){
                        $(".prod-amt").each(function() {
                            amt = parseInt($(this).text())
                            new_amt = (amt * data.value) / 100
                            $(this).text(amt-new_amt);
                        });
                    }
                    else{
                        $(".class").each(function() {
                            amt = parseInt($(this).text())
                            new_amt = (amt - data.value)
                            $(this).text(amt-new_amt);
                        });
                    }
                }
                else{
                    promo_code_status = false;
                    $('.max-amt-' + promo_product_id).text(max_price);
                    getPrice(promo_product_id);
                    $('.valid-promo-code').remove()
                    if ($('.invalid-promo-code').length <= 0){
                        $('.promo-code-block').after('<div class="invalid-feedback d-block invalid-promo-code">'+ data.msg +'</div>');
                    }
                }
            }
        });
    });
    $(document).on("click",".offer",function(e) {
        $('#offerModal').modal('show');
    })
    function getPrice(id){
        $.ajax({
            url: '/get-max-price/',
            data: {
                'product_id': id
            },
            dataType: 'json',
            success: function (data) {
                if (data.status){
                    max_price = data.amx_amt;
                    $('.max-amt-' + promo_product_id).text(data.amx_amt);
                    $('.prod-amt').each(function(index){
                        $(this).text(data.all_price[index].amount);
                    });
                }
            }
        });
    }
    $(document).on("change", "#id_bill_no", function(){
        var cur_bill_no = this.value;
        $.ajax({
            url: '/check-bill-no-exists/',
            data: {'bill_no': cur_bill_no},
            dataType: 'json',
            success: function (data) {
                if(!data.status){
//                    $('#id_bill_no').addClass('error');
                    if ($('#id_bill_no-error').length <= 0){
                        $("#id_bill_no").after('<label id="id_bill_no-error" class="alert alert-danger" for="id_bill_no">Bill number already exists!!!</label>')
                    }
                }
            }
        })
    });
    $("#billGeneratingForm").validate({
    errorClass: 'alert alert-danger',
    validClass: 'form-control',
    errorElement: 'label',
    highlight: function(element, errorClass, validClass) {
      $(element).parents("div.form-control").addClass("form-control");
      $(element).parents("div.form-control").addClass("error");
    },
    unhighlight: function(element, errorClass, validClass) {
      $(element).parents(".error").removeClass("error");
      $(element).parents(".error").removeClass("alert alert-danger");
    },
        rules: {
            "bill_no": {
                required: true,
//                remote:{
//                            url: "/check-bill-no-exists/",
//                            type: "post",
//                            dataType: 'json',
//                            data: {
//                                bill_no: function () {
//                                    return $("#id_bill_no").val();
//                                }
//                            }
//                        }
            },
            "bill_date": {
                required: true,
            },
            "bill_amount": {
                required: true,
                minlength: 0,
                maxlength: 8
            },
            "bill_due_date": {
                required: true,
            },
            "billing_party_name": {
                required: true
            },
            "upload_bill": {
                required: true
            }
        },
        messages: {
            "bill_no": {
                required: "This field is required.",
//                remote: "Bill number already exists!!!"
            },
            "bill_date": {
                required: "This field is required."
            },
            "bill_amount": {
                required: "This field is required."
            },
            "bill_due_date": {
                required: "This field is required."
            },
            "billing_party_name": {
                required: "This field is required."
            },
            "billing_party_name": {
                required: "This field is required."
            },
            "upload_bill": {
                required: "This field is required."
            }
        },
        submitHandler: function (form) {
            $('#billDiscountingModal').modal('hide');
            var started_date = $('#started_date').val();
            var started_date = $('#ended_date').val();
            $('#modal_started_date').text(started_date);
            $('#modal_ended_date').text(ended_date);
            $.ajax({
                url: "/dashboard/inquiries/",
                type: "POST",
                data: new FormData($(form)),
                cache: false,
                processData: false,
                success: function (data) {
                    location.reload();
                }
            });
//            $('#SchemeInfoModal').modal('show');
//            $('#modal-ok').on('click', function(){
//                  saveUploadBill(form);
//            })
//            alert("working");
            return false;
        }
    });

    function saveUploadBill(form){
        console.log("function");
        $.ajax({
                url: "/dashboard/inquiries/",
                type: "POST",
                data: $(form).serialize(),
//                cache: false,
//                processData: false,
                success: function (data) {
                    location.reload();
                }
              });
//        alert("Working");
    }

    $(document).on("click",".book-your-sale",function() {
        $('#billDiscountingModal').on('hidden.bs.modal', function (e) {
            //alert('this is function visiting');
          $(this)
            .find("input,textarea,select")
                .removeClass('is-valid')
               .val('')
               .end()
            .find("input[type=checkbox], input[type=radio]")
                .removeClass('is-valid')
               .prop("checked", "")
               .end();
        });
        var this_val = $(this)
        var this_row = this_val.closest('tr');
        var prod_id = this_val.data('product-id');
        var inq_prod_id = this_val.data('inquiry-id');
        var inq_exists = $('#id_inquiry option[value='+inq_prod_id+']').length;
        if(inq_exists !=0 ) {
            $('#id_inquiry option[value!="'+ inq_prod_id +'"]').remove();
        }
        else{
            $('#id_inquiry option').remove();
            $('#id_inquiry').append('<option value="'+ inq_prod_id +'">"'+ this_row.find('td:eq(3)').text() +'"</option>');
        }
        var inq_product_name = this_row.find('td:eq(2)').text();
        $('.inq-prod-name').text(inq_product_name);
        $('#id_inquired_by').val(this_row.find('td:eq(1)').text());
        $('#id_inquired_by').attr('readonly','readonly');
        $('#id_inquiry').parent().closest('.form-group').css('display', 'none');
        $('#ref_inq_no').val(inq_prod_id);
        $('#inq_product_name').val(inq_product_name);
        // check scheme exists on product
        $.ajax({
            url: '/check-scheme-exists/',
            data: {
                'product_id': prod_id
            },
            dataType: 'json',
            success: function (data) {
                if (data.status){
                    $('#id_dealers_given_finance_scheme').html("<option value=''>-------</option>" + data.scheme_value);
                    $('#started_date').val(data.started_date);
                    $('#ended_date').val(data.started_date);
                    $('#id_dealers_given_finance_scheme').parent().parent().show();
                }
                else{
                    $('#id_dealers_given_finance_scheme').html("<option value=''></option");
                    $('#id_dealers_given_finance_scheme').parent().parent().hide();
                }
            }
        });
    });
    $('#billDiscountingModal').on('hidden.bs.modal', function () {
        $("#billGeneratingForm").validate().resetForm();
        $("#billGeneratingForm").find('.alert-danger').remove();
    });
    $('#billDiscountingModal').on('hidden.bs.modal', function () {
        $("#editbillGeneratingForm").validate().resetForm();
    });
//    calculate total amount on book sale form
    var inq_qty = 0;
    var inq_price = 0;
    var inq_gross_amt = 0;
    var inq_disc_amt = 0;
    var inq_tax = 0;
    var inq_final_amt = 0;
    $('#inq_product_gross_amt').attr('readonly','readonly');
    $('#inq_product_final_amt').attr('readonly','readonly');
    $(document).on("change paste keyup","#qty",function(event) {
        inq_qty = this.value;
        inq_price = $('#inq_product_price').val();
        inq_gross_amt = parseInt(inq_qty) * parseInt(inq_price)
        inq_disc_amt = $('#inq_product_disc_amt').val();
        inq_tax = $('#inGenerate Billq_product_tax').val();
        inq_final_amt = (inq_gross_amt - parseInt(inq_disc_amt)) + parseInt(inq_tax);
        if (inq_qty.length > 0 && inq_price.length > 0){
            $('#inq_product_gross_amt').val(inq_gross_amt);
        }
        if($('#inq_product_gross_amt').val().length > 0 && inq_disc_amt.length > 0 && inq_tax.length > 0){
            $('#inq_product_final_amt').val(inq_final_amt);
        }
        if(parseInt($('#inq_product_final_amt').val()) > 0){
            $('#id_bill_amount').val(parseInt($('#inq_product_final_amt').val()));
        }
    });
    $(document).on("change paste keyup","#inq_product_price",function(event) {
        inq_price = this.value;
        inq_qty = $('#qty').val();
        inq_gross_amt = parseInt(inq_qty) * parseInt(inq_price)
        inq_disc_amt = $('#inq_product_disc_amt').val();
        inq_tax = $('#inq_product_tax').val();
        inq_final_amt = (inq_gross_amt - parseInt(inq_disc_amt)) + parseInt(inq_tax);
        if (inq_qty.length > 0 && inq_price.length > 0){
            $('#inq_product_gross_amt').val(inq_gross_amt);
        }
        if($('#inq_product_gross_amt').val().length > 0 && inq_disc_amt.length > 0 && inq_tax.length > 0){
            $('#inq_product_final_amt').val(inq_final_amt);
        }
        if(parseInt($('#inq_product_final_amt').val()) > 0){
            $('#id_bill_amount').val(parseInt($('#inq_product_final_amt').val()));
        }
    });
    $(document).on("change paste keyup","#inq_product_disc_amt",function(event) {
        inq_disc_amt = this.value;
        inq_price = $('#inq_product_price').val();
        inq_qty = $('#qty').val();
        inq_gross_amt = parseInt(inq_qty) * parseInt(inq_price)
        inq_tax = $('#inq_product_tax').val();
        inq_final_amt = (inq_gross_amt - parseInt(inq_disc_amt)) + parseInt(inq_tax);
        inq_final_amt = (inq_gross_amt - parseInt(inq_disc_amt)) + parseInt(inq_tax);
        if (inq_qty.length > 0 && inq_price.length > 0){
            $('#inq_product_gross_amt').val(inq_gross_amt);
        }
        if($('#inq_product_gross_amt').val().length > 0 && inq_disc_amt.length > 0 && inq_tax.length > 0){
            $('#inq_product_final_amt').val(inq_final_amt);
        }
        if(parseInt($('#inq_product_final_amt').val()) > 0){
            $('#id_bill_amount').val(parseInt($('#inq_product_final_amt').val()));
        }
    });
    $(document).on("change paste keyup","#inq_product_tax",function(event) {
        inq_tax = this.value;
        inq_disc_amt = $('#inq_product_disc_amt').val();
        inq_price = $('#inq_product_price').val();
        inq_qty = $('#qty').val();
        inq_gross_amt = parseInt(inq_qty) * parseInt(inq_price)
        inq_final_amt = (inq_gross_amt - parseInt(inq_disc_amt)) + parseInt(inq_tax);
        inq_final_amt = (inq_gross_amt - parseInt(inq_disc_amt)) + parseInt(inq_tax);
        if (inq_qty.length > 0 && inq_price.length > 0){
            $('#inq_product_gross_amt').val(inq_gross_amt);
        }
        if($('#inq_product_gross_amt').val().length > 0 && inq_disc_amt.length > 0 && inq_tax.length > 0){
            $('#inq_product_final_amt').val(inq_final_amt);
        }
        if(parseInt($('#inq_product_final_amt').val()) > 0){
            $('#id_bill_amount').val(parseInt($('#inq_product_final_amt').val()));
        }
    });

    // On edit bill

    //    calculate total amount on book sale form
    var inq_qty = 0;
    var inq_price = 0;
    var inq_gross_amt = 0;
    var inq_disc_amt = 0;
    var inq_tax = 0;
    var inq_final_amt = 0;
    console.log()
    $('#id_inquired_by').attr('readonly','readonly');
    $('#id_inq_product_gross_amt').attr('readonly','readonly');
    $('#id_inq_product_final_amt').attr('readonly','readonly');
    $('#id_bill_amount').attr('readonly','readonly');
    $(document).on("change paste keypress","#id_qty",function(event) {
        inq_qty = this.value;
        inq_price = $('#id_inq_product_price').val();
        inq_gross_amt = parseInt(inq_qty) * parseInt(inq_price)
        inq_disc_amt = $('#id_inq_product_disc_amt').val();
        inq_tax = $('#id_inq_product_tax').val();
        inq_final_amt = (inq_gross_amt - parseInt(inq_disc_amt)) + parseInt(inq_tax);
        if (inq_qty.length > 0 && inq_price.length > 0){
            $('#id_inq_product_gross_amt').val(inq_gross_amt);
        }
        if($('#id_inq_product_gross_amt').val().length > 0 && inq_disc_amt.length > 0 && inq_tax.length > 0){
            $('#id_inq_product_final_amt').val(inq_final_amt);
        }
        if(parseInt($('#id_inq_product_final_amt').val()) > 0){
            $('#id_bill_amount').val(parseInt($('.edit-bill #id_inq_product_final_amt').val()));
        }
    });
    $(document).on("change paste keyress","#id_inq_product_price",function(event) {
        inq_price = this.value;
        inq_qty = $('#id_qty').val();
        inq_gross_amt = parseInt(inq_qty) * parseInt(inq_price)
        inq_disc_amt = $('#id_inq_product_disc_amt').val();
        inq_tax = $('#id_inq_product_tax').val();
        inq_final_amt = (inq_gross_amt - parseInt(inq_disc_amt)) + parseInt(inq_tax);
        if (inq_qty.length > 0 && inq_price.length > 0){
            $('#id_inq_product_gross_amt').val(inq_gross_amt);
        }
        if($('#id_inq_product_gross_amt').val().length > 0 && inq_disc_amt.length > 0 && inq_tax.length > 0){
            $('#id_inq_product_final_amt').val(inq_final_amt);
        }
        if(parseInt($('#id_inq_product_final_amt').val()) > 0){
            $('#id_bill_amount').val(parseInt($('#id_inq_product_final_amt').val()));
        }
    });
    $(document).on("change paste keypress","#id_inq_product_disc_amt",function(event) {
        inq_disc_amt = this.value;
        inq_price = $('#id_inq_product_price').val();
        inq_qty = $('#id_qty').val();
        inq_gross_amt = parseInt(inq_qty) * parseInt(inq_price)
        inq_tax = $('#id_inq_product_tax').val();
        inq_final_amt = (inq_gross_amt - parseInt(inq_disc_amt)) + parseInt(inq_tax);
        inq_final_amt = (inq_gross_amt - parseInt(inq_disc_amt)) + parseInt(inq_tax);
        console.log("working", inq_gross_amt, inq_gross_amt, inq_tax);
        if(inq_gross_amt > inq_disc_amt){
            if (inq_qty.length > 0 && inq_price.length > 0){
                $('#id_inq_product_gross_amt').val(inq_gross_amt);
            }
            if($('#id_inq_product_gross_amt').val().length > 0 && inq_disc_amt.length > 0 && inq_tax.length > 0){
                $('#id_inq_product_final_amt').val(inq_final_amt);
            }
            if(parseInt($('#id_inq_product_final_amt').val()) > 0){
                $('#id_bill_amount').val(parseInt($('#id_inq_product_final_amt').val()));
            }
        }
        else{
            alert("Discount amount should not be greater than Gross Amount");
            $(this).val(0);
        }
    });
    $(document).on("change paste keypress","#id_inq_product_tax",function(event) {
        inq_tax = this.value;
        inq_disc_amt = $('#id_inq_product_disc_amt').val();
        inq_price = $('#id_inq_product_price').val();
        inq_qty = $('#id_qty').val();
        inq_gross_amt = parseInt(inq_qty) * parseInt(inq_price)
        inq_final_amt = (inq_gross_amt - parseInt(inq_disc_amt)) + parseInt(inq_tax);
        inq_final_amt = (inq_gross_amt - parseInt(inq_disc_amt)) + parseInt(inq_tax);
        if(inq_price > inq_tax){
            if (inq_qty.length > 0 && inq_price.length > 0){
                $('#id_inq_product_gross_amt').val(inq_gross_amt);
            }
            if($('#id_inq_product_gross_amt').val().length > 0 && inq_disc_amt.length > 0 && inq_tax.length > 0){
                $('#id_inq_product_final_amt').val(inq_final_amt);
            }
            if(parseInt($('#id_inq_product_final_amt').val()) > 0){
                $('#id_bill_amount').val(parseInt($('#id_inq_product_final_amt').val()));
            }
        }
        else{
            alert("Tax should not be greater than Gross Amount");
            $(this).val(0);
        }
    });

    $(document).on("click",".finance-btn",function() {
        $('#finance_url').attr('href', $(this).data('url'));
    });

    function restrictAlpha(e){
        var a = [];
        var k = e.which;
        var length = $(this).val().length;

        for (i = 48; i < 58; i++)
            a.push(i);

        if (!(a.indexOf(k)>=0))
            e.preventDefault();
    }

    function restrictNo(e){
        e = (e) ? e : window.event;
        var charCode = (e.which) ? e.which : e.keyCode;
        if ((charCode > 64 && charCode < 91) || (charCode > 96 && charCode < 122)) {
            return true;
        }
        else{ e.preventDefault(); }
    }

    $('#id_billing_party_name').keypress('click', restrictNo);
//    $('#id_loan_emi').keypress('click', restrictAlpha);

});