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

    // --- TOPIC SUGGESTION FEATURE ---
    let lensIcon = null;
    let selectedText = '';
    let currentTopic = typeof topic !== 'undefined' ? topic : '';

    // Add blur class to background when modal is open
    function blurBackground(enable) {
        if (enable) {
            $('.container, .page-header, .site-footer').addClass('modal-blur');
        } else {
            $('.container, .page-header, .site-footer').removeClass('modal-blur');
        }
    }

    // Create lens icon
    function createLensIcon() {
        if (lensIcon) lensIcon.remove();
        lensIcon = $('<button class="lens-icon" title="Explore related topics">🔍</button>');
        $('body').append(lensIcon);
        return lensIcon;
    }

    // Position lens icon near selection
    function positionLensIcon(selection) {
        if (!selection.rangeCount) return;
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;
        const lensIcon = createLensIcon();
        const iconSize = 32;
        let left = rect.left + rect.width / 2 - iconSize / 2;
        let top = rect.top - iconSize - 10;
        left = Math.max(10, Math.min(left, window.innerWidth - iconSize - 10));
        top = Math.max(10, Math.min(top, window.innerHeight - iconSize - 10));
        lensIcon.css({ position: 'fixed', left: left + 'px', top: top + 'px' });
        lensIcon.show();
    }

    // Hide lens icon
    function hideLensIcon() {
        if (lensIcon) { lensIcon.remove(); lensIcon = null; }
    }

    // Show lens icon on mouseup after selection (not on right-click)
    $(document).on('mouseup', function(e) {
        setTimeout(function() { // Wait for selection to update
            const selection = window.getSelection();
            selectedText = selection.toString().trim();
            if (!selectedText || selectedText.length < 10) {
                hideLensIcon();
                return;
            }
            const articleContent = document.getElementById('article-content');
            if (articleContent && selection.anchorNode && articleContent.contains(selection.anchorNode)) {
                positionLensIcon(selection);
            } else {
                hideLensIcon();
            }
        }, 1);
    });

    // Hide lens icon on scroll, resize, or clicking elsewhere
    $(window).on('scroll resize', hideLensIcon);
    $(document).on('mousedown', function(e) {
        if (!$(e.target).hasClass('lens-icon')) hideLensIcon();
    });

    // --- Modal logic ---
    function openTopicSuggestionModal(text) {
        $('#selected-text-display').text(text);
        $('#custom-topic-input').val('');
        $('#topic-suggestion-modal').show();
        blurBackground(true);
        // Show loading spinner in modal
        $('#suggestions-list').html('<div class="suggestions-loading" style="text-align:center;"><div class="spinner" style="margin:0 auto;"></div><div style="margin-top:10px;">Generating suggestions...</div></div>');
        generateTopicSuggestions(text);
    }

    function closeTopicSuggestionModal() {
        $('#topic-suggestion-modal').hide();
        blurBackground(false);
        $('#custom-topic-input').val('');
    }

    // Lens icon click opens modal and triggers suggestions
    $(document).on('click', '.lens-icon', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (selectedText) {
            openTopicSuggestionModal(selectedText);
            hideLensIcon();
        }
    });

    // Generate topic suggestions via API
    function generateTopicSuggestions(text) {
        $.ajax({
            url: '/suggest_topics',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ selected_text: text, current_topic: currentTopic }),
            success: function(response) {
                if (response.suggestions && response.suggestions.length > 0) {
                    displaySuggestions(response.suggestions);
                } else {
                    $('#suggestions-list').html('<p>No suggestions available. Try selecting different text or enter your own topic.</p>');
                }
            },
            error: function(xhr) {
                let errorMessage = 'Error generating suggestions.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }
                $('#suggestions-list').html(`<p style="color: #e74c3c;">${errorMessage}</p>`);
            }
        });
    }

    // Display clickable suggestions
    function displaySuggestions(suggestions) {
        let html = '';
        suggestions.forEach(function(suggestion) {
            html += `<a href="/${encodeURIComponent(suggestion)}" class="suggestion-item">${suggestion}</a>`;
        });
        $('#suggestions-list').html(html);
    }

    // Custom topic generation
    $('#generate-custom-btn').click(function() {
        const customTopic = $('#custom-topic-input').val().trim();
        if (customTopic) {
            window.location.href = `/${encodeURIComponent(customTopic)}`;
        }
    });
    $('#custom-topic-input').keypress(function(e) {
        if (e.which === 13) { $('#generate-custom-btn').click(); }
    });

    // Modal close logic
    $('#close-topic-suggestion').click(closeTopicSuggestionModal);
    $(window).on('mousedown', function(e) {
        if ($(e.target).is('#topic-suggestion-modal')) closeTopicSuggestionModal();
    });

    // --- Accessibility: focus trap and ESC close ---
    $(document).on('keydown', function(e) {
        if ($('#topic-suggestion-modal').is(':visible')) {
            if (e.key === 'Escape') closeTopicSuggestionModal();
        }
    });

    // --- Add blur CSS ---
    if (!$('style#modal-blur-style').length) {
        $('head').append('<style id="modal-blur-style">.modal-blur { filter: blur(4px) !important; transition: filter 0.2s; }</style>');
    }
});












