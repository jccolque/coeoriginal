from django.forms import DateTimeInput, DateInput

class  XDSoftDatePickerInput(DateInput):
    template_name = 'widgets/xdsoft_datepicker.html'

class  XDSoftTimePickerInput(DateTimeInput):
    template_name = 'widgets/xdsoft_timepicker.html'

class XDSoftDateTimePickerInput(DateTimeInput):
    template_name = 'widgets/xdsoft_datetimepicker.html'