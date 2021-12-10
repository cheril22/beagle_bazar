$(document).ready(function(){
    $(document).on("click",".delete-btn",function() {
        $('#delete-record').attr('href', $(this).attr('id'));
    });

    $(document).on("click","#add-price",function() {
        $("input").prop('required',true);
        $.ajax({
            url: "/dashboard/get-price-structure/",
            dataType: 'json',
            success: function (data) {
                var form = '<div class="d-flex dynamic-form-fields">' + data.form + '<i class="fa fa-trash del-price" aria-hidden="true" style="font-size: 25px; color: #ff0000; padding: 0px 10px;margin-top: 5%;cursor: pointer;"></i></div>';
                $("#dynamicForm").append(form);
                if($('#initial_field').find('.del-price').length < 1){
                    $('#initial_field').append('<i class="fa fa-trash del-price" aria-hidden="true" style="font-size: 25px; color: #ff0000; padding: 0px 10px;margin-top: 5%;cursor: pointer;"></i></div>');
                }
                console.log($('#initial_field').length, $(".dynamic-form-fields").length)
                if($('#initial_field').length < 1 && $(".dynamic-form-fields").length <= 1){
                    console.log($(".dynamic-form-fields").first());
                }
            }
        });
    });

    $(document).on("click",".feature-img",function() {
        var this_val = $(this);
        $.ajax({
            url: "/dashboard/make-featured-img/" + $(this).attr('id'),
            dataType: 'json',
            success: function (data) {
                if (data.status)
                {
                    $(".feature-img").prop("checked", false);
                    this_val.attr("checked", "checked");
                    this_val.prop("checked", true);
                }
            }
        });
    });

    //dynamically load categories by category id
    var check_cat_id = $('#id_category option:selected').val();
    var sub_cat_id = $('#id_sub_category option:selected').val();
    if (check_cat_id != ''){
        $.ajax({
            url: '/ajax_calls/get-sub-categories/',
             data: {
                'cat_id': check_cat_id
            },
            dataType: 'json',
            success: function (data) {
                if (data.status)
                {
                    $('#id_sub_category').html(data.sub_category);
                    $("#id_sub_category  option").each(function()
                    {
                        if ($(this).val() == sub_cat_id){
                            $(this).attr("selected", "selected");
                        }
                    });
                }
            }
        });
        $(document).on("change","#id_category",function() {
            var cat_id = $(this).val();
            getSubCategory(cat_id);
        });
    }
    else{
        $('#id_sub_category').find('option').not(':first').remove();
        $(document).on("change","#id_category",function() {
            var cat_id = $(this).val();
            getSubCategory(cat_id);
        });
    }
    function getSubCategory(id){
        $.ajax({
            url: '/ajax_calls/get-sub-categories/',
             data: {
                'cat_id': id
            },
            dataType: 'json',
            success: function (data) {
                if (data.status)
                {
                    $('#id_sub_category').html(data.sub_category);
                }
            }
        });
    }
    $(document).on("click",".del-price",function() {
        $(this).parent('.d-flex').remove();
        $(this).parent('.price-frm').remove();
        if($('.del-price').length <= 1){
            $('.del-price').remove();
        }
    });

    $(document).on("click",".check-auth",function(e) {
        e.preventDefault()
        var next = window.location.protocol + "//" + window.location.host + "/login/vauth";
        window.location.replace(next);
    });

    $(document).on("click",".final-save-review",function(event) {
        event.preventDefault()
        var form = $(this).closest("form");
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            dataType: 'json',
            type: 'POST',
            success: function (data) {
                if (data.status) {
                    $('.add-review-error').remove();
                    $('<div class="alert alert-success alert-dismissible fade show" role="alert"><strong>Success!</strong> Your review has submitted successfully!<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>').insertAfter(".search");
                    $('#ratingModal').modal('toggle');
                    setTimeout(function() {
                        location.reload();
                    }, 1000);
                }
                else{
                    if ($('.add-review-error').length <= 0){
                        $('<div class="alert alert-danger add-review-error" role="alert"><strong>Error !</strong> '+ data.message +'</div>').insertBefore(".user-review-section");
                    }
                }
            }
        });
    });

    $(document).on("click",".final-edit-review",function(event) {
        event.preventDefault()
        var token = '{{csrf_token}}';
        var form = $(this).closest("form");
        $.ajax({
            headers: { "X-CSRFToken": token },
            type: 'POST',
            url: '/edit-rating/',
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if (data.status) {
                    $('.add-review-error').remove();
                    $('<div class="alert alert-success alert-dismissible fade show" role="alert"><strong>Success!</strong> Your review has updated successfully!<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>').insertAfter(".search");
                    $('#ratingModal').modal('toggle');
                    setTimeout(function() {
                        location.reload();
                    }, 1000);
                }
                else{
                    if ($('.add-review-error').length <= 0){
                        $('<div class="alert alert-danger add-review-error" role="alert"><strong>Error !</strong> '+ data.message +'</div>').insertBefore(".user-review-section");
                    }
                }
            }
        });
    });

    $(document).on("click",".edit-review",function(event) {
        event.preventDefault();
        $.ajax({
            url: '/give-rating/',
            data: {product_id: $(this).data('product-id')},
            dataType: 'json',
            success: function (data) {
                if (data.status){
                    $($('.user-review-section label').get().reverse()).each(function(i)
                    {
                        var index_val = i + 1
                        if (index_val <= data.rated_value){
                            $(this).addClass("highlight");
                        }
                    });
                    $("#rating-val").val(data.rated_value)
                    $("#product-val").val(data.product_id)
                    $("#message-text").val(data.message)
                }
            }
        });
    });

    $(document).on("click",".user-review-section label",function() {
        $(".user-review-section label").removeClass("highlight");
        var to_mark = $(this).prev().val();
        $($('.user-review-section label').get().reverse()).each(function(i)
        {
            var index_val = i + 1
            if (index_val <= to_mark){
                $(this).addClass("highlight");
            }
        });
    })
    $(document).on("click",".review-btn",function() {
        $(".user-review-section label").removeClass("highlight");
        $("#message-text").val("");
        if ($(this).hasClass("save-review")){
            $('.js-save-rating').removeClass('final-edit-review');
            $('.js-save-rating').addClass('final-save-review');
        }
        else{
            $('.js-save-rating').removeClass('final-save-review');
            $('.js-save-rating').addClass('final-edit-review');
        }
        $("#product-val").val($(this).data('product-id'));
    });
    $(".rating label").click(function(){
        $('#rating-val').val($(this).prev().val());
	});
	if ($('#id_is_this_physical_product').prop('checked') == true){
	    getDeliveryForm();
	}
    $(document).on("change","#id_is_this_physical_product",function() {
        getDeliveryForm();
    });
    function getDeliveryForm(){
        $.ajax({
            url: "/dashboard/get-product-delivery-form/",
            dataType: 'json',
            success: function (data) {
                if ($('.delivery-form').length <= 0){
                    console.log(data)
                    var form = '<h5>Packaging and Delivery Details</h5><div class="delivery-form" id="delivery_form">' + data.form + '</div>';
                    $(".pack_and_del_frm").append(form);
                }
                else{
                    $('.pack_and_del_frm').html('');
                }
            }
        });
    }
    setTimeout(function(){
        var url = window.location.pathname;
        var splittedStr = url.split('/');
        if (url.indexOf("products/edit/") > -1) {
            $.ajax({
                url: "/dashboard/get-product-delivery-details/",
                data: {product_id: splittedStr[splittedStr.length-2]},
                dataType: 'json',
                success: function (data) {
                    if(data.status){
                        $.each(data.data[0], function(key, value) {
                            if(key !== "picture"){
                                $("#id_" + key).val(value);
                            }
                        });
                    }
                }
            });
        }
    }, 1000);
    var initial_amt = 0;
    var disc_per = 0;
    var dis_amt = 0;
    var tax_amt = 0;
    var per_amt = 0;
    var final_amt = 0;
    $(document).on("change paste keydown","#id_amount",function(event) {
        initial_amt = this.value;
        var cur_obj = $(this).parent().parent();
        disc_per = cur_obj.find('#id_disc_per').val();
        dis_amt = cur_obj.find('#id_disc_amt').val();
        tax_amt = cur_obj.find('#id_taxes').val();
        per_amt = parseInt((parseInt(initial_amt) * parseInt(disc_per) ) / 100);
        cur_obj.find('#id_disc_amt').val(per_amt);
        final_amt = (parseInt(initial_amt) - parseInt(dis_amt)) + parseInt(tax_amt);
//        if(initial_amt > disc_per){
            if (initial_amt.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(initial_amt)));
            }
            if (initial_amt.length > 0 && disc_per.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(initial_amt) - parseInt(dis_amt)));
            }
            if (initial_amt.length > 0 && disc_per.length > 0 && tax_amt.length > 0){
                cur_obj.find('#id_final_amt').val(final_amt);
            }
//        }
//       else{
//            alert("Discount amount should not be greater than Amount");
//            $(this).val(0);
//       }
    });
    $(document).on("change paste keydown","#id_disc_per",function(e) {
        var cur_obj = $(this).parent().parent();
        initial_amt = cur_obj.find('#id_amount').val();
        disc_per = this.value;
        dis_amt = cur_obj.find('#id_disc_amt').val();
        tax_amt = cur_obj.find('#id_taxes').val();
        per_amt = parseInt((parseInt(initial_amt) * parseInt(disc_per) ) / 100);
        cur_obj.find('#id_disc_amt').val(per_amt);
        final_amt = (parseInt(initial_amt) - parseInt(dis_amt)) + parseInt(tax_amt)
        if(initial_amt > disc_per){
            if (initial_amt.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(initial_amt)));
            }
            if (initial_amt.length > 0 && disc_per.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(initial_amt) - parseInt(dis_amt)));
            }
            if (initial_amt.length > 0 && disc_per.length > 0 && tax_amt.length > 0){
                cur_obj.find('#id_final_amt').val(final_amt);
            }
        }
    });
    $(document).on("change paste keydown","#id_disc_amt",function(event) {
        var cur_obj = $(this).parent().parent();
        initial_amt = cur_obj.find('#id_amount').val();
        disc_per = cur_obj.find('#id_disc_per').val();
        dis_amt = this.value;
        tax_amt = cur_obj.find('#id_taxes').val();
        per_amt = parseInt((parseInt(dis_amt) / parseInt(initial_amt) ) * 100);
        cur_obj.find('#id_disc_per').val(per_amt);
        final_amt = (parseInt(initial_amt) - parseInt(dis_amt)) + parseInt(tax_amt);
        if(initial_amt > dis_amt){
            if (initial_amt.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(initial_amt)));
            }
            if (initial_amt.length > 0 && disc_per.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(initial_amt) - parseInt(dis_amt)));
            }
            if (initial_amt.length > 0 && disc_per.length > 0 && tax_amt.length > 0){
                cur_obj.find('#id_final_amt').val(final_amt);
            }
        }
       else{
            alert("Discount amount should not be greater than Amount");
            $(this).val(0);
       }
    });
    $(document).on("change paste keydown","#id_taxes",function(event) {
        var cur_obj = $(this).parent().parent();
        initial_amt = cur_obj.find('#id_amount').val();
        disc_per = cur_obj.find('#id_disc_per').val();
        dis_amt = cur_obj.find('#id_disc_amt').val();
        tax_amt = this.value;
        final_amt = (parseInt(initial_amt) - parseInt(dis_amt)) + parseInt(tax_amt);
        if(initial_amt > tax_amt){
            if (initial_amt.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(initial_amt)));
            }
            if (initial_amt.length > 0 && disc_per.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(initial_amt) - parseInt(dis_amt)));
            }
            if (initial_amt.length > 0 && disc_per.length > 0 && tax_amt.length > 0){
                cur_obj.find('#id_final_amt').val(final_amt);
            }
        }
       else{
            alert("Tax should not be greater than Amount");
            $(this).val(0);
       }
    });
    $('[data-filter="trigger"]').on("change", function() {
        var t = $(this).find("option:selected").val().toLowerCase();
        $('[data-filter="target"]').css("display", "none");
        $("#" + t).css("display", "table-row-group");
        if(t == "all") {
            $('[data-filter="target"]').css("display", "table-row-group")
        }
        $(this).css("display", "block");
        
    });

    if (window.File && window.FileList && window.FileReader) {
        $("#id_image").on("change", fileSelection);
        $("#id_demo_video").on("change", fileSelection);
        $("#id_upload_bill").on("change", fileSelection);
    } else {
        alert("Your browser doesn't support to File API")
    }

    function fileSelection(e) {
        var img = e.target.files;
        var img_ext = img[0].name.split('.')[1].toLowerCase();
        if( img_ext == 'png'|| img_ext == 'jpeg'|| img_ext == 'jpg'){
            uploadImg(e, $(this));
        }else if(img_ext == 'mp4' || img_ext == 'mov' || img_ext == 'avi' || img_ext == 'wmv'){
            uploadVideo(e, $(this));
        } else{
            uploadPdf(e, $(this));
        }
    };

    function uploadImg(e, location){
        var files = e.target.files,
            filesLength = files.length;
            for (var i = 0; i < filesLength; i++) {
            var f = files[i]
            var fileReader = new FileReader();
            fileReader.onload = (function(e) {
                var file = e.target;
                $("<div class=\"img-wrap\">" +
                "<img class=\"imageThumb preview-img\" id=\"id_pro_img\" src=\"" + e.target.result + "\" title=\"" + file.name + "\"/>" +
                "<span class=\"remove\">X</span>" +
                "</div>").insertAfter(location);
                $(".remove").click(function(){
                $(this).parent(".img-wrap").remove();
                if($(".remove").length == 0){
                    $("#id_image").val('');
                    $('#id_upload_bill').val('');
                }
                });

            });
            fileReader.readAsDataURL(f);
            }
        }

    function uploadVideo(e, location){
        var files = e.target.files,
            filesLength = files.length;
            for (var i = 0; i < filesLength; i++) {
            var f = files[i]
            var fileReader = new FileReader();
            fileReader.onload = (function(e) {
                var file = e.target;
                $("<div class=\"img-wrap-video\">" +
                "<video class=\"videoThumb\" width=\"200\" height=\"150\" controls>" +
                "<source src=\"" + e.target.result + "\" title=\"" + file.name + "\">" +
                "</video>" +
                "<span class=\"remove-video\">X</span>" +
                "</div>").insertAfter(location);
                $(".remove-video").click(function(){
                $(this).parent(".img-wrap-video").remove();
                if($(".remove-video").length == 0){
                    $("#id_demo_video").val('');
                }
                });

            });
            fileReader.readAsDataURL(f);
            }
        }

        function uploadPdf(e, location){
            var files = e.target.files;
            var filesLength = files.length;
            for (var i = 0; i < filesLength; i++) {
                var f = files[i];
                var fileReader = new FileReader();
                fileReader.onload = (function(e) {
                    var file = e.target;
                    $("<div class=\"pdf-wrap\">" +
                    "<i class=\"fa fa-file-pdf-o\" aria-hidden=\"true\" style=\"font-size:40px;\"></i>" +
                    "<a href=\"" + e.target.result + "\" title=\"" + file.name + "\"></a>" +
                    "<span class=\"removePdf\">X</span>" +
                    "</div>").insertAfter(location);

                    $(".removePdf").click(function(){
                        $(this).parent(".pdf-wrap").remove();
                        if($(".removePdf").length == 0){
                            $("#id_upload_bill").val('');
                        }
                    });
                });
                fileReader.readAsDataURL(f);
            }
        }

    $("#id_start_date").on("keypress", function(){
        return false;
    });
    $("#id_end_date").on("keypress", function(){
        return false;
    });
    $("#id_bill_date").on("keypress", function(){
        return false;
    });

    $(".close-modal").on("click", function(){
        $('.add-review-error').remove();
    });

    var inq_initial_amt = 0;
    var inq_disc_per = 0;
    var inq_dis_amt = 0;
    var inq_tax_amt = 0;
    var inq_per_amt = 0;
    var inq_final_amt = 0;
    $(document).on("change paste keydown","#id_amount",function(event) {
        inq_initial_amt = this.value;
        var cur_obj = $(this).parent().parent();
        inq_disc_per = cur_obj.find('#id_disc_per').val();
        inq_dis_amt = cur_obj.find('#id_disc_amt').val();
        inq_tax_amt = cur_obj.find('#id_taxes').val();
        inq_per_amt = parseInt((parseInt(inq_initial_amt) * parseInt(inq_disc_per) ) / 100);
        cur_obj.find('#id_disc_amt').val(inq_per_amt);
        inq_final_amt = (parseInt(inq_initial_amt) - parseInt(inq_dis_amt)) + parseInt(inq_tax_amt);
//        if(inq_initial_amt > inq_disc_per){
            if (inq_initial_amt.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(inq_initial_amt)));
            }
            if (inq_initial_amt.length > 0 && inq_disc_per.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(inq_initial_amt) - parseInt(inq_dis_amt)));
            }
            if (inq_initial_amt.length > 0 && inq_disc_per.length > 0 && inq_tax_amt.length > 0){
                cur_obj.find('#id_final_amt').val(inq_final_amt);
            }
//        }
//       else{
//            event.preventDefault();
//       }
    });
    $(document).on("change paste keydown","#id_disc_per",function(e) {
        var cur_obj = $(this).parent().parent();
        inq_initial_amt = cur_obj.find('#id_amount').val();
        inq_disc_per = this.value;
        inq_dis_amt = cur_obj.find('#id_disc_amt').val();
        inq_tax_amt = cur_obj.find('#id_taxes').val();
        inq_per_amt = parseInt((parseInt(inq_initial_amt) * parseInt(inq_disc_per) ) / 100);
        cur_obj.find('#id_disc_amt').val(inq_per_amt);
        inq_final_amt = (parseInt(inq_initial_amt) - parseInt(inq_dis_amt)) + parseInt(inq_tax_amt)
        if(inq_initial_amt > inq_disc_per){
            if (inq_initial_amt.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(inq_initial_amt)));
            }
            if (inq_initial_amt.length > 0 && inq_disc_per.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(inq_initial_amt) - parseInt(inq_dis_amt)));
            }
            if (inq_initial_amt.length > 0 && inq_disc_per.length > 0 && inq_tax_amt.length > 0){
                cur_obj.find('#id_final_amt').val(inq_final_amt);
            }
        }
       else{
            alert("Discount amount should not be greater than Amount");
//            event.preventDefault();
       }
    });
    $(document).on("change paste keydown","#id_disc_amt",function(event) {
        var cur_obj = $(this).parent().parent();
        inq_initial_amt = cur_obj.find('#id_amount').val();
        inq_disc_per = cur_obj.find('#id_disc_per').val();
        inq_dis_amt = this.value;
        inq_tax_amt = cur_obj.find('#id_taxes').val();
        inq_per_amt = parseInt((parseInt(inq_dis_amt) / parseInt(inq_initial_amt) ) * 100);
        cur_obj.find('#id_disc_per').val(inq_per_amt);
        inq_final_amt = (parseInt(inq_initial_amt) - parseInt(inq_dis_amt)) + parseInt(inq_tax_amt);
        if(inq_initial_amt > inq_disc_per){
            if (inq_initial_amt.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(inq_initial_amt)));
            }
            if (inq_initial_amt.length > 0 && inq_disc_per.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(inq_initial_amt) - parseInt(inq_dis_amt)));
            }
            if (inq_initial_amt.length > 0 && inq_disc_per.length > 0 && inq_tax_amt.length > 0){
                cur_obj.find('#id_final_amt').val(inq_final_amt);
            }
        }
       else{
            alert("Discount amount should not be greater than Amount");
//            alert(cur_obj.find('#id_disc_amt').val(0));
//            event.preventDefault();
       }
    });
    $(document).on("change paste keydown","#id_taxes",function(event) {
        var cur_obj = $(this).parent().parent();
        inq_initial_amt = cur_obj.find('#id_amount').val();
        inq_disc_per = cur_obj.find('#id_disc_per').val();
        inq_dis_amt = cur_obj.find('#id_disc_amt').val();
        inq_tax_amt = this.value;
        inq_final_amt = (parseInt(inq_initial_amt) - parseInt(inq_dis_amt)) + parseInt(inq_tax_amt);
        if(inq_initial_amt > inq_disc_per){
            if (inq_initial_amt.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(inq_initial_amt)));
            }
            if (inq_initial_amt.length > 0 && inq_disc_per.length > 0){
                cur_obj.find('#id_final_amt').val((parseInt(inq_initial_amt) - parseInt(inq_dis_amt)));
            }
            if (inq_initial_amt.length > 0 && inq_disc_per.length > 0 && inq_tax_amt.length > 0){
                cur_obj.find('#id_final_amt').val(inq_final_amt);
            }
        }
       else{
            alert("Discount amount should not be greater than Amount Ajay2");
//            event.preventDefault();
       }
    });
});
function validateMaxLength(e, thisobj, maxlength)
    {
        var a = [];
        var length = thisobj.value.length;

        for (i = 48; i < 58; i++){
            a.push(i);
        }

        if (length > maxlength){
            e.preventDefault();
        }
    }

  $('#id_rate_of_interest').keypress(function(e)
  {
        validateMaxLength(e, this, '2');
  });
  $('#id_tenure').keypress(function(e)
  {
        validateMaxLength(e, this, '2');
  });

  $('#id_disc_per').keypress(function(e)
  {
        validateMaxLength(e, this, '2');
  });

var id = "{{ pk|safe }}";
//$("#post_form").validate({
//    errorClass: 'alert alert-danger',
//    validClass: 'form-control',
//    errorElement: 'label',
//    highlight: function(element, errorClass, validClass) {
//      $(element).parents("div.form-control").addClass("form-control");
//      $(element).parents("div.form-control").addClass("error");
//    },
//    unhighlight: function(element, errorClass, validClass) {
//      $(element).parents(".error").removeClass("error");
//      $(element).parents(".error").removeClass("alert alert-danger");
//    },
//        rules: {
//            "selling_units": {
//                required: true,
//                  maxlength: 8
//            },
//            "single_package_size": {
//                required: true,
//                maxlength: 8
//            },
//            "single_gross_weight": {
//                required: true,
//                maxlength: 8
//            },
//            "package_type": {
//                required: true,
//            },
//            "packing_size": {
//                required: true,
//                maxlength: 8
//            },
//            "packing_weight": {
//                required: true,
//                maxlength: 8
//            },
//            "picture": {
//                required: true,
//                maxlength: 8
//            },
//            "lead_time": {
//                required: true,
//                maxlength: 5
//            },
//            "shipping_charges": {
//                maxlength: 8
//            },
//            "shipping_time": {
//                required: true,
//                maxlength: 5
//            }
//        },
//        messages: {
//            "name": {
//                required: "This field is required."
//            },
//            "brand_name": {
//                required: "This field is required."
//            },
//            "specification": {
//                required: "This field is required."
//            },
//            "after_warranty_service": {
//                required: "This field is required."
//            },
//            "local_service_location": {
//                required: "This field is required."
//            },
//            "condition": {
//                required: "This field is required."
//            },
//            "place_of_origin": {
//                required: "This field is required."
//            },
//            "dimension": {
//                required: "This field is required."
//            },
//            "certification": {
//                required: "This field is required."
//            },
//            "warranty": {
//                required: "This field is required."
//            },
//            "after_sales_service_provided": {
//                required: "This field is required."
//            },
//            "selling_units": {
//                required: "This field is required."
//            },
//            "single_package_size": {
//                required: "This field is required."
//            },
//            "single_gross_weight": {
//                required: "This field is required."
//            },
//            "package_type": {
//                required: "This field is required."
//            },
//            "packing_size": {
//                required: "This field is required."
//            },
//            "packing_weight": {
//                required: "This field is required."
//            },
//            "picture": {
//                required: "This field is required."
//            },
//            "lead_time": {
//                required: "This field is required."
//            },
//            "shipping_time": {
//                required: "This field is required."
//            },
//            "frequency": {
//                required: "Required"
//            },
//            "label": {
//                required: "Required"
//            },
//            "currency": {
//                required: "Required"
//            },
//            "amount": {
//                required: "Required"
//            },
//            "disc_per": {
//                required: "Required"
//            },
//            "disc_amt": {
//                required: "Required"
//            },
//            "taxes": {
//                required: "Required"
//            },
//        },
//        submitHandler: function (form) {
//            $.ajax({
//                url: "dashboard/products/edit/" + id,
//                type: "POST",
//                data: new FormData($(form)),
//                cache: false,
//                processData: false,
//                success: function (data) {
//                    location.reload();
//                }
//            });
//            return false;
//        }
//
//    });

$("#book-sales-btn").on("click", function(){

})