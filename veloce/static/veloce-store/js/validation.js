 $(document).ready(function($) {
    $("#login-user").validate({
                rules: {

                    username : "required",
                    password: {
                        required: true,
                    },

                messages: {
                    username: "Please enter your given name",
                    password: {
                        required: "Please provide a correct password",
                    },

                 errorPlacement: function(error, element)
        {
            if ( element.is(":radio") )
            {
                error.appendTo( element.parents('.form-group') );
            }
            else
                error.insertAfter( element );
            }
         },
                submitHandler: function(form) {
                    form.submit();
                }

            }
    });
});

 $(document).ready(function($) {
    $("#change-password").validate({
                rules: {

                    current_password: {
                        required: true,
                    },
                    confirm_password: {
                        required: true,
                    },
                    new_password: {
                        required: true,
                    },

                messages: {
                    current_password: "Please enter your current password",
                    new_password: "Please enter your new password",
                    confirm_password: {
                        equalTo : "#password",
                        required: "Please re-enter your new password"
                        }
                    },

                 errorPlacement: function(error, element)
        {
            if ( element.is(":radio") )
            {
                error.appendTo( element.parents('.form-group') );
            }
            else
                error.insertAfter( element );
            }
         },
                submitHandler: function(form) {
                    form.submit();
                }

            })
    });



$(document).ready(function($) {
    $("#signup-user").validate({
                rules: {

                    first_name : {
                        required: true,
                        lettersonly: true
                    },
                    last_name : {
                        required: true,
                        lettersonly: true
                    },
                    email_address: {
                        required: true,
                        email: true,

                    },
                    gender : {
                        required: true,
                    },
                    birthdate: {
                        required: true,
                    },

                messages: {
                    first_name : {

                        required: "Please enter your first name",
                        lettersonly: "This field allows alphabets only"

                    },
                    last_name : {

                        required: "Please enter your last name",
                        lettersonly: "This field allows alphabets only"

                    },

                    email_address: "Please enter a valid email address",

                    gender: "Please select a valid input",

                    birthdate: "Please enter a correct birth date",

                 errorPlacement: function(error, element)
        {
            if ( element.is(":radio") )
            {
                error.appendTo( element.parents('.form-group') );
            }
            else
                error.insertAfter( element );
            }
         },
                submitHandler: function(form) {
                    form.submit();
                }

            }
    });
});