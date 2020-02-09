function submitPlanningForm(e) {
    var startDate = $('input[id=startDate]').val();
    var endDate = $('input[id=endDate]').val();
    var daysBudget = $('input[id=daysBudget]').val();
    $('#alertzone').empty();

    if (isValidDate(startDate) && isValidDate(endDate) && 0 < daysBudget <= 365)  {
        //initialize elements
        $('img.loadinggif').show();

        //define correct API url
        var apiURL = 'http://localhost:5000/api/plan';

        //execute api call
        $.ajax({
            url: apiURL + '?start=' + startDate +
                '&end=' + endDate + '&budget='+daysBudget,
            success: function (result) {
                var resObj = JSON.parse(result)
                var history = JSON.parse(resObj.history)
                var forecast = JSON.parse(resObj.forecast)

                const alerts = Object.values(JSON.parse(resObj.alerts))

                //display alerts
                for (var alert of alerts) {
                    $('#alertzone').append(
                        '<div class="button alert-warning horizontalspacing">' +
                        alert + '</div>');
                }

                $('img.loadinggif').hide();

                //update calendar here
            },
            error: function (jqXHR, textStatus, errorThrown) {
                $('img.loadinggif').hide();
                $('#alertzone').append(
                    '<div class="alert alert-danger horizontalspacing">' +
                    textStatus + ': ' + jqXHR.responseText +
                    '</div>');
                console.log(errorThrown);
            }
        });
    } else {
        $('#alertzone').append(
            '<div class="alert alert-danger horizontalspacing">Invalid input parameters!</div>'
        );
    }
    e.preventDefault();
}

function isValidDate(dateString) {
    var regEx = /^\d{4}-\d{2}-\d{2}$/;
    return dateString.match(regEx) != null;
}
