function planWise(e) {
    /*var startDate = $('input[id=startDate]').val();
    var endDate = $('input[id=endDate]').val();*/
    var inpYear = $('#yearSelection').val();
    var inpBudget = $('input[id=daysBudget]').val();
    var inpRegion = $('#regionSelection').val();

    $('#alertzone').empty();
    //if (isValidDate(startDate) && isValidDate(endDate) && 0 < daysBudget <= 365 && region.length > 0) {
    if (['2020', '2021', '2022', '2023', '2024', '2025'].indexOf(inpYear) > -1 && 0 < inpBudget <= 365 && inpRegion.length > 0) {

        toggleElements();

        //define correct API url
        var apiURL = 'http://planwi.se/api/plan' + '?start=' + inpYear + '-01-01' +
            '&end=' + inpYear + '-12-31&budget=' + inpBudget + '&region=' + inpRegion;
        console.log(apiURL);
        //execute api call
        $.ajax({
            url: apiURL,
            success: function (result) {
                var resObj = JSON.parse(result);

                var regionValues = resObj.region.split(',');
                var regionString = 'unknown'
                if (regionValues.length > 2) {
                    regionString = regionValues[0] + ' - ' + regionValues[2];
                }
                else if (regionValues.length == 1) {
                    regionString = regionValues[0];
                }
                
                var eventData = [];
                for (var proposal of resObj.proposals) {
                    //add new option to front end here (e.g. tabs?)
                    for (var p of proposal.proposal_items) {
                        var startDate = new Date(p.start);
                        var endDate = new Date(p.end);
                        eventData.push({
                            name: 'From ' + startDate.toDateString() + ' to ' + endDate.toDateString(),
                            caption: 'Take ' + p.cost + ' days off and relax ' + p.benefit + ' days 🌴',
                            startDate: startDate,
                            endDate: endDate
                        });
                    }

                    //add proposal info to card under calendar (unallocated budget exists per option)
                    var infoSentenceHTML = 'This is how you could plan <b>' + (resObj.budget - proposal.unallocated_budget) +
                        '</b> days of leave to make best use of public holidays in <b>' + regionString + '</b>.';
                    if (proposal.unallocated_budget > 0) {
                        infoSentenceHTML += ' With this leave plan you still have <b>' + proposal.unallocated_budget + '</b> day(s) to plan freely.';
                    }
                    $('#detailzone').empty();
                    $('#detailzone').append(
                        '<div class="card"><div class="card-header"><b>When to travel in ' + inpYear + '?</b></div>' +
                        '<div class="card-body"><p class="card-text">' + infoSentenceHTML + '</p> </div></div>'
                    );
                }

                var holidays = JSON.parse(resObj.public_holidays);
                for (var h of holidays) {
                    eventData.push({ name: h.description, caption: regionString, startDate: new Date(h.date), endDate: new Date(h.date), color: '#17a2b8' })
                }

                var alerts = Object.values(JSON.parse(resObj.alerts));
                //display alerts
                for (var alert of alerts) {
                    $('#alertzone').append(
                        '<div class="button alert-warning horizontalspacing">' +
                        alert + '</div>');
                }

                showCalendar(inpYear, eventData)
                toggleElements();
            },
            error: function (jqXHR, textStatus, errorThrown) {
                $('#alertzone').append(
                    '<div class="alert alert-danger horizontalspacing">' +
                    textStatus + ': ' + jqXHR.responseText +
                    '</div>');
                toggleElements();
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

function toggleElements() {
    $('#planspinner').toggle();
    $('#calendar').toggle();
    $('#detailzone').toggle();
}

function showCalendar(year, calendarEvents) {

    calendar = new Calendar('#calendar', {
        enableContextMenu: false,
        enableRangeSelection: false,
        weekStart: 1,
        startYear: year,
        displayHeader: false,
        //disabledWeekDays: [0, 6],
        mouseOnDay: function (e) {
            if (e.events.length > 0) {
                var content = '';

                for (var i in e.events) {
                    content += '<div class="event-tooltip-content">'
                        + '<div class="event-name" style="color:' + e.events[i].color + '">' + e.events[i].name + '</div>'
                        + '<div class="event-location">' + e.events[i].caption + '</div>'
                        + '</div>';
                }

                $(e.element).popover({
                    trigger: 'manual',
                    container: 'body',
                    html: true,
                    content: content
                });

                $(e.element).popover('show');
            }
        },
        mouseOutDay: function (e) {
            if (e.events.length > 0) {
                $(e.element).popover('hide');
            }
        },
        dayContextMenu: function (e) {
            $(e.element).popover('hide');
        },
        dataSource: calendarEvents
    });

}

function isValidDate(dateString) {
    var regEx = /^\d{4}-\d{2}-\d{2}$/;
    return dateString.match(regEx) != null;
}
