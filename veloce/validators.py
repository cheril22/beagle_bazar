import re
from django.core import validators
from django.core.exceptions import ValidationError
from veloce import models

NameValidator = validators.RegexValidator(
    regex='^[A-Za-z]{2,20}$',
    message='Invalid characters in name.'
)

EmailValidatorBase = validators.EmailValidator(
    message='Invalid email.'
)


def EmailValidator(value):
    EmailValidatorBase(value)
    # TODO: Add domain check in the future


def PasswordValidator(value):
    if not len(value) >= 8 or not len(value) <= 50:
        raise ValidationError(
            'Password should be between 8-50 characters long.'
        )
    if not re.search('[A-Z]', value) or not re.search('[a-z]', value) \
            or not re.search('[0-9]', value) or not re.search('[^A-Za-z0-9]', value):
        raise ValidationError(
            'Password should contain at least one numeric, uppercase, lowercase and special letter.'
        )


def validate_file_extension_video(self):
    """ This function is an amalgamation of two validations,
    file size validation, file type validation, anf file extension validation"""

    import os
    ext = os.path.splitext(self.name)[1]
    valid_extensions = ['.mp4', '.mov', '.avi', '.wmv', '.mkv', '.3gp']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension, please upload a file with a '
                              'valid extension ie: mp4, mov, avi, or wmv')

    file_size = self.size

    if file_size > 10485760:  # 10MB
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    else:
        return self


def validate_file_extension_image(self):
    """ This function is an amalgamation of two validations,
        file size validation, file type validation, anf file extension validation"""

    import os
    ext = os.path.splitext(self.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']

    # Checks whether the file has a valid extension.
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension, please upload a file '
                              'with a valid extension, ie: jpg, jpeg, png, gif ')

    file_size = self.size

    if file_size > 2621440:  # 2.5MB
        raise ValidationError("The maximum file size that can be uploaded is 2.5MB")
    else:
        return self


def check_user_level_and_has_product(user):
    check_has_product = models.Product.objects.filter(vendor=user)
    check_user_eligibility = models.Profile.objects.get(user=user)
    if check_has_product.count() > 0 and check_user_eligibility.is_complete and check_user_eligibility.is_verified:
        return True
    else:
        return False
