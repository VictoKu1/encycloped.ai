$(document).ready( function () {
    // Toggle edit form when the edit (pen) icon is clicked
    $("#search-btn").click(function () {
        $("#edit-form").toggle();
    });
    // Show/hide report modal
    $("#report-btn").click(function () {
        $("#report-modal").show();
    });
    $("#close-report").click(function () {
        $("#report-modal").hide();
    });

    // Handle report submission
    $("#send-report").click(function () {
        let topic = "{{ topic }}";
        let report_details = $("#report-details").val();
        let sources = $("#report-sources").val().split(',');

        $.ajax({
            url: "/report",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                topic: topic,
                report_details: report_details,
                sources: sources
            }),
            success: function (response) {
                // Check reply code
                if (response.reply === "1") {
                    $("#article-content").html(response.updated_content);
                    alert("Article updated!");
                } else {
                    alert("Report deemed irrelevant.");
                }
                $("#report-modal").hide();
            },
            error: function () {
                alert("Error processing the report.");
            }
        });
    });

    // Show/hide add info modal
    $("#add-info-btn").click(function () {
        $("#add-info-modal").show();
    });
    $("#close-add-info").click(function () {
        $("#add-info-modal").hide();
    });

    // Handle add info submission
    $("#send-add-info").click(function () {
        let topic = "{{ topic }}";
        let subtopic = $("#subtopic-name").val();
        let info = $("#additional-info").val();
        let sources = $("#info-sources").val().split(',');

        $.ajax({
            url: "/add_info",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                topic: topic,
                subtopic: subtopic,
                info: info,
                sources: sources
            }),
            success: function (response) {
                if (response.reply === "1") {
                    $("#article-content").html(response.updated_content);
                    alert("Information added!");
                } else {
                    alert("The addition was deemed irrelevant.");
                }
                $("#add-info-modal").hide();
            },
            error: function () {
                alert("Error processing the request.");
            }
        });
    });

    // Spinner overlay logic
    function showSpinner() {
        if ($('.spinner-overlay').length === 0) {
            $('body').append('<div class="spinner-overlay"><div class="spinner"></div></div>');
        }
    }
    function hideSpinner() {
        $('.spinner-overlay').remove();
    }

    // Show spinner on search submit
    $(document).on('submit', 'form[action="/"], form[action^="/"]', function(e) {
        showSpinner();
    });
    // Show spinner on topic link click
    $(document).on('click', 'a', function(e) {
        var href = $(this).attr('href');
        if (href && href.startsWith('/') && !href.startsWith('/static/')) {
            showSpinner();
        }
    });
    // Hide spinner when content is loaded
    $(window).on('load', function() {
        hideSpinner();
    });
    // Hide spinner after AJAX loads article content
    $(document).ajaxComplete(function() {
        hideSpinner();
    });

    // Show spinner immediately on topic pages (not main index)
    if ($('#article-content').length > 0) {
        showSpinner();
    }
});












