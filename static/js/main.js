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

    // Test function to verify substring logic
    function testSubstringLogic() {
        const testText = "interpreted programming language";
        const testTopic = "programming";
        const result = testText.toLowerCase().includes(testTopic.toLowerCase());
        console.log('Test substring logic:');
        console.log('Test text:', testText);
        console.log('Test topic:', testTopic);
        console.log('Result:', result);
        return result;
    }

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
            
            // Debug: log the selected text
            console.log('Selected text captured:', selectedText);
            console.log('Selected text length:', selectedText.length);
            
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
        console.log('Opening modal with text:', text); // Debug log
        console.log('Global selectedText variable:', selectedText); // Debug log
        
        // Test the substring logic
        testSubstringLogic();
        
        // Use the global selectedText variable, not the parameter
        const textToUse = selectedText || text;
        console.log('Text to use for validation:', textToUse);
        
        $('#selected-text-display').text(textToUse);
        $('#custom-topic-input').val('');
        $('#topic-suggestion-modal').show();
        blurBackground(true);
        // Show loading spinner in modal
        $('#suggestions-list').html('<div class="suggestions-loading" style="text-align:center;"><div class="spinner" style="margin:0 auto;"></div><div style="margin-top:10px;">Extracting topics from selected text...</div></div>');
        generateTopicSuggestions(textToUse);
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
        console.log('Lens icon clicked, selectedText:', selectedText); // Debug log
        if (selectedText) {
            openTopicSuggestionModal(selectedText);
            hideLensIcon();
        }
    });

    // Generate topic suggestions via API
    function generateTopicSuggestions(text) {
        console.log('Sending to API:', { selected_text: text, current_topic: currentTopic }); // Debug log
        
        $.ajax({
            url: '/suggest_topics',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ selected_text: text, current_topic: currentTopic }),
            success: function(response) {
                console.log('API response:', response); // Debug log
                if (response.suggestions && response.suggestions.length > 0) {
                    displaySuggestions(response.suggestions);
                } else {
                    $('#suggestions-list').html('<p>No topics found in the selected text. Try selecting different text or enter your own topic.</p>');
                }
            },
            error: function(xhr) {
                console.error('API error:', xhr); // Debug log
                let errorMessage = 'Error extracting topics from text.';
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
            if (suggestion.toLowerCase().includes('no additional terms found') || 
                suggestion.toLowerCase().includes('no terms found') ||
                suggestion.toLowerCase().includes('topic extraction unavailable')) {
                // Make unclickable for fallback/error messages
                html += `<div class="suggestion-item unclickable" style="cursor: not-allowed; opacity: 0.6;">${suggestion}</div>`;
            } else {
                // Make clickable for valid suggestions with custom click handler
                html += `<a href="#" class="suggestion-item topic-link" data-topic="${encodeURIComponent(suggestion)}">${suggestion}</a>`;
            }
        });
        $('#suggestions-list').html(html);
    }

    // Handle topic suggestion clicks
    $(document).on('click', '.topic-link', function(e) {
        e.preventDefault();
        const topic = decodeURIComponent($(this).data('topic'));
        const selectedTextLower = selectedText.toLowerCase();
        
        console.log('Topic suggestion clicked:', topic);
        console.log('Selected text:', selectedText);
        
        // Convert selected text to link in the article content
        convertSelectedTextToLink(selectedText, topic);
        
        // Close the modal
        closeTopicSuggestionModal();
        
        // Navigate to the new topic
        window.location.href = `/${encodeURIComponent(topic)}`;
    });

    // Function to convert selected text to a link
    function convertSelectedTextToLink(selectedText, topic) {
        const articleContent = $('#article-content');
        const content = articleContent.html();
        
        // Create the link HTML
        const linkHtml = `<a href="/${encodeURIComponent(topic)}">${selectedText}</a>`;
        
        // Replace the selected text with the link
        // Use a more robust replacement that handles HTML entities and case variations
        const escapedSelectedText = selectedText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(escapedSelectedText, 'gi');
        const newContent = content.replace(regex, linkHtml);
        
        // Update the article content
        articleContent.html(newContent);
        
        console.log('Converted selected text to link:', selectedText, '→', topic);
        
        // Optionally save this change to the backend (you can implement this later)
        saveTopicLinkToBackend(selectedText, topic);
    }

    // Function to save the topic link to backend (optional)
    function saveTopicLinkToBackend(selectedText, topic) {
        // This could be implemented to persist the link changes
        // For now, we'll just log it
        console.log('Saving topic link to backend:', {
            selected_text: selectedText,
            topic: topic,
            current_page: window.location.pathname
        });
        
        // You could make an AJAX call here to save the link to your backend
        // $.ajax({
        //     url: '/save_topic_link',
        //     method: 'POST',
        //     data: {
        //         selected_text: selectedText,
        //         topic: topic,
        //         current_page: window.location.pathname
        //     }
        // });
    }

    // Custom topic generation with validation
    $('#generate-custom-btn').click(function() {
        const customTopic = $('#custom-topic-input').val().trim();
        const selectedTextLower = selectedText.toLowerCase();
        const customTopicLower = customTopic.toLowerCase();
        
        // Debug logging
        console.log('Debug substring check:');
        console.log('Selected text:', selectedText);
        console.log('Selected text (lower):', selectedTextLower);
        console.log('Custom topic:', customTopic);
        console.log('Custom topic (lower):', customTopicLower);
        console.log('Includes check:', selectedTextLower.includes(customTopicLower));
        
        if (!customTopic) {
            alert('Please enter a topic.');
            return;
        }
        
        // Check if custom topic is a substring of selected text (case-insensitive)
        if (selectedTextLower.includes(customTopicLower)) {
            // Topic is part of selected text - proceed normally
            console.log('Topic is part of selected text - proceeding');
            
            // Convert selected text to link in the article content
            convertSelectedTextToLink(selectedText, customTopic);
            
            // Close the modal
            closeTopicSuggestionModal();
            
            // Navigate to the new topic
            window.location.href = `/${encodeURIComponent(customTopic)}`;
        } else {
            // Topic is not part of selected text - show warning but still allow
            console.log('Topic is NOT part of selected text - showing confirmation');
            if (confirm(`"${customTopic}" is not part of the selected text. Do you want to generate an article about this topic anyway?`)) {
                // Convert selected text to link in the article content
                convertSelectedTextToLink(selectedText, customTopic);
                
                // Close the modal
                closeTopicSuggestionModal();
                
                // Navigate to the new topic
                window.location.href = `/${encodeURIComponent(customTopic)}`;
            }
        }
    });

    // Real-time validation for custom topic input
    $('#custom-topic-input').on('input', function() {
        const customTopic = $(this).val().trim();
        const selectedTextLower = selectedText.toLowerCase();
        const customTopicLower = customTopic.toLowerCase();
        const generateBtn = $('#generate-custom-btn');
        
        // Debug logging for real-time validation
        console.log('Real-time validation:');
        console.log('Selected text (lower):', selectedTextLower);
        console.log('Custom topic (lower):', customTopicLower);
        console.log('Includes check:', selectedTextLower.includes(customTopicLower));
        
        if (!customTopic) {
            generateBtn.text('Generate Article').removeClass('warning');
            return;
        }
        
        if (selectedTextLower.includes(customTopicLower)) {
            generateBtn.text('Generate Article').removeClass('warning');
        } else {
            generateBtn.text('Generate Article (Not in selected text)').addClass('warning');
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












