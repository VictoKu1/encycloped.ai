$(document).ready(function () {
    // --- HAMBURGER MENU FUNCTIONALITY ---
    // Recent topics storage key
    const RECENT_TOPICS_KEY = 'encycloped_ai_recent_topics';
    const MAX_RECENT_TOPICS = 20;

    // Get current topic from page
    function getCurrentTopic() {
        // Try to get topic from various sources
        const topicHeader = $('.page-topic-header h1').text().trim();
        if (topicHeader) return topicHeader;

        // Try to get from URL if on topic page
        const path = window.location.pathname;
        if (path && path !== '/' && path !== '/index.html') {
            return decodeURIComponent(path.substring(1));
        }

        return null;
    }

    // Save topic to recent topics
    function saveTopicToRecent(topic) {
        if (!topic) return;

        let recentTopics = JSON.parse(localStorage.getItem(RECENT_TOPICS_KEY) || '[]');

        // Remove if already exists (to move to top)
        recentTopics = recentTopics.filter(t => t.topic !== topic);

        // Add to beginning
        recentTopics.unshift({
            topic: topic,
            timestamp: Date.now(),
            url: window.location.href
        });

        // Keep only the most recent topics
        if (recentTopics.length > MAX_RECENT_TOPICS) {
            recentTopics = recentTopics.slice(0, MAX_RECENT_TOPICS);
        }

        localStorage.setItem(RECENT_TOPICS_KEY, JSON.stringify(recentTopics));
        updateRecentTopicsDisplay();
    }

    // Update the recent topics display
    function updateRecentTopicsDisplay() {
        const recentTopics = JSON.parse(localStorage.getItem(RECENT_TOPICS_KEY) || '[]');
        const $list = $('#recent-topics-list');

        if (recentTopics.length === 0) {
            $list.html('<p class="no-topics">No recent topics yet</p>');
            return;
        }

        let html = '';
        recentTopics.forEach(function (item) {
            const timeAgo = getTimeAgo(item.timestamp);
            html += `
                <a href="/${encodeURIComponent(item.topic)}" class="recent-topic-item" data-topic="${encodeURIComponent(item.topic)}">
                    <div class="topic-name">${item.topic}</div>
                    <div class="topic-time">${timeAgo}</div>
                </a>
            `;
        });

        $list.html(html);
    }

    // Get time ago string
    function getTimeAgo(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        return new Date(timestamp).toLocaleDateString();
    }

    // Toggle sidebar
    function toggleSidebar() {
        const $sidebar = $('#sidebar');
        const $overlay = $('#sidebar-overlay');
        const $hamburger = $('#hamburger-menu');

        $sidebar.toggleClass('open');
        $overlay.toggleClass('open');
        $hamburger.toggleClass('active');
        $('body').toggleClass('sidebar-open');
    }

    // Close sidebar
    function closeSidebar() {
        const $sidebar = $('#sidebar');
        const $overlay = $('#sidebar-overlay');
        const $hamburger = $('#hamburger-menu');

        $sidebar.removeClass('open');
        $overlay.removeClass('open');
        $hamburger.removeClass('active');
        $('body').removeClass('sidebar-open');
    }

    // Event handlers for hamburger menu
    $('#hamburger-menu').click(function (e) {
        e.preventDefault();
        e.stopPropagation();
        toggleSidebar();
    });

    $('#close-sidebar').click(function (e) {
        e.preventDefault();
        closeSidebar();
    });

    $('#sidebar-overlay').click(function (e) {
        e.preventDefault();
        closeSidebar();
    });

    // Close sidebar on escape key
    $(document).keydown(function (e) {
        if (e.key === 'Escape' && $('#sidebar').hasClass('open')) {
            closeSidebar();
        }
    });

    // Save current topic when page loads
    const currentTopicForRecent = getCurrentTopic();
    if (currentTopicForRecent) {
        saveTopicToRecent(currentTopicForRecent);
    }

    // Update display on page load
    updateRecentTopicsDisplay();

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

    // Function to check for Wikipedia URLs
    function hasWikipediaUrl(sources) {
        return sources.some(url => {
            const cleanUrl = url.trim().toLowerCase();
            return cleanUrl.includes('wikipedia.org') || cleanUrl.includes('en.wikipedia.org');
        });
    }

    // Function to validate sources and update button state
    function validateSourcesAndUpdateButton(sourcesInput, submitButton) {
        const sources = sourcesInput.val().split(',').map(s => s.trim()).filter(s => s.length > 0);
        const hasWikipedia = hasWikipediaUrl(sources);

        if (hasWikipedia) {
            submitButton.prop('disabled', true).text('Remove Wikipedia URLs to submit');
            submitButton.addClass('disabled-wikipedia');
        } else {
            submitButton.prop('disabled', false).text('Submit');
            submitButton.removeClass('disabled-wikipedia');
        }
    }

    // Real-time validation for report sources
    $("#report-sources").on('input', function () {
        validateSourcesAndUpdateButton($(this), $("#send-report"));
    });

    // Handle report submission
    $("#send-report").click(function () {
        let topic = "{{ topic }}";
        let report_details = $("#report-details").val();
        let sources = $("#report-sources").val().split(',').map(s => s.trim()).filter(s => s.length > 0);

        // Double-check for Wikipedia URLs before submission
        if (hasWikipediaUrl(sources)) {
            alert("Please remove Wikipedia URLs from sources before submitting.");
            return;
        }

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

    // Real-time validation for add info sources
    $("#info-sources").on('input', function () {
        validateSourcesAndUpdateButton($(this), $("#send-add-info"));
    });

    // Handle add info submission
    $("#send-add-info").click(function () {
        let topic = "{{ topic }}";
        let subtopic = $("#subtopic-name").val();
        let info = $("#additional-info").val();
        let sources = $("#info-sources").val().split(',').map(s => s.trim()).filter(s => s.length > 0);

        // Double-check for Wikipedia URLs before submission
        if (hasWikipediaUrl(sources)) {
            alert("Please remove Wikipedia URLs from sources before submitting.");
            return;
        }

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
    $(document).on('submit', 'form[action="/"], form[action^="/"]', function (e) {
        showSpinner();
    });
    // Show spinner on topic link click
    $(document).on('click', 'a', function (e) {
        var href = $(this).attr('href');
        if (href && href.startsWith('/') && !href.startsWith('/static/')) {
            showSpinner();
        }
    });
    // Hide spinner when content is loaded
    $(window).on('load', function () {
        hideSpinner();
    });
    // Hide spinner after AJAX loads article content
    $(document).ajaxComplete(function () {
        hideSpinner();
    });

    // Show spinner immediately on topic pages (not main index)
    if ($('#article-content').length > 0) {
        showSpinner();
    }

    // --- TOPIC SUGGESTION FEATURE ---
    let lensIcon = null;
    let selectedText = '';
    let currentTopicForSelection = typeof topic !== 'undefined' ? topic : '';
    let selectionRange = null; // Store the selection range for precise replacement

    // Utility: Check if a node is inside a link
    function isNodeInsideLink(node) {
        while (node) {
            if (node.nodeType === 1 && node.tagName === 'A') return true;
            node = node.parentNode;
        }
        return false;
    }

    // Utility: Get all non-linked text nodes in a selection
    function getNonLinkedTextNodes(range) {
        const nodes = [];
        function getTextNodes(node) {
            if (node.nodeType === 3 && !isNodeInsideLink(node)) {
                nodes.push(node);
            } else if (node.nodeType === 1 && node.childNodes) {
                for (let child of node.childNodes) getTextNodes(child);
            }
        }
        getTextNodes(range.commonAncestorContainer);
        // Filter nodes that are actually within the range
        return nodes.filter(node => {
            const nodeRange = document.createRange();
            nodeRange.selectNodeContents(node);
            return range.compareBoundaryPoints(Range.END_TO_START, nodeRange) < 0 &&
                range.compareBoundaryPoints(Range.START_TO_END, nodeRange) > 0;
        });
    }

    // Utility: Get all linked text nodes in a selection
    function getLinkedTextNodes(range) {
        const nodes = [];
        function getTextNodes(node) {
            if (node.nodeType === 3 && isNodeInsideLink(node)) {
                nodes.push(node);
            } else if (node.nodeType === 1 && node.childNodes) {
                for (let child of node.childNodes) getTextNodes(child);
            }
        }
        getTextNodes(range.commonAncestorContainer);
        // Filter nodes that are actually within the range
        return nodes.filter(node => {
            const nodeRange = document.createRange();
            nodeRange.selectNodeContents(node);
            return range.compareBoundaryPoints(Range.END_TO_START, nodeRange) < 0 &&
                range.compareBoundaryPoints(Range.START_TO_END, nodeRange) > 0;
        });
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
    $(document).on('mouseup', function (e) {
        setTimeout(function () { // Wait for selection to update
            const selection = window.getSelection();
            selectedText = selection.toString().trim();
            selectionRange = selection.rangeCount ? selection.getRangeAt(0).cloneRange() : null;
            // Debug: log the selected text
            console.log('Selected text captured:', selectedText);
            console.log('Selected text length:', selectedText.length);
            if (!selectedText || selectedText.length < 2) {
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
    $(document).on('mousedown', function (e) {
        if (!$(e.target).hasClass('lens-icon')) hideLensIcon();
    });

    // --- Modal logic ---
    function openTopicSuggestionModal(text) {
        // Always use the user's actual selected text for display and backend
        const textToUse = selectedText || text;
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
    $(document).on('click', '.lens-icon', function (e) {
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
        console.log('Sending to API:', { selected_text: text, current_topic: currentTopicForSelection }); // Debug log

        // Collect all already-referenced topics in the article
        const referencedTopics = [];
        $('#article-content a[href^="/"]').each(function () {
            let href = $(this).attr('href');
            if (href.startsWith('/')) {
                let topic = decodeURIComponent(href.slice(1));
                referencedTopics.push(topic);
            }
        });

        $.ajax({
            url: '/suggest_topics',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ selected_text: text, current_topic: currentTopicForSelection, referenced_topics: referencedTopics }),
            success: function (response) {
                console.log('API response:', response); // Debug log
                if (response.suggestions && response.suggestions.length > 0) {
                    displaySuggestions(response.suggestions);
                } else {
                    $('#suggestions-list').html('<p>No topics found in the selected text. Try selecting different text or enter your own topic.</p>');
                }
            },
            error: function (xhr) {
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
        // Only show suggestions that are not already linked in the selection,
        // not the current topic, and not already referenced in the article
        let html = '';
        let validSuggestions = [];
        // Normalization function: remove parenthesis and their contents, trim, lowercase
        function normalizeTopic(t) {
            return t.replace(/\s*\([^)]*\)/g, '').trim().toLowerCase();
        }
        const currentTopicLower = normalizeTopic(currentTopicForSelection ? currentTopicForSelection : '');

        // Collect all already-referenced topics in the article (normalized)
        const referencedTopics = new Set();
        $('#article-content a[href^="/"]').each(function () {
            let href = $(this).attr('href');
            if (href.startsWith('/')) {
                let topic = decodeURIComponent(href.slice(1));
                referencedTopics.add(normalizeTopic(topic));
            }
        });

        if (selectionRange) {
            let nonLinkedNodes = getNonLinkedTextNodes(selectionRange);
            let nonLinkedText = nonLinkedNodes.map(n => n.textContent).join(' ').toLowerCase();
            validSuggestions = suggestions.filter(suggestion => {
                const suggestionLower = normalizeTopic(suggestion);
                // Exclude if matches current topic
                if (suggestionLower === currentTopicLower) return false;
                // Exclude if already referenced in article
                if (referencedTopics.has(suggestionLower)) return false;
                // Exclude if not in non-linked text
                return nonLinkedText.includes(suggestionLower);
            });
        } else {
            validSuggestions = suggestions.filter(suggestion => {
                const suggestionLower = normalizeTopic(suggestion);
                if (suggestionLower === currentTopicLower) return false;
                if (referencedTopics.has(suggestionLower)) return false;
                return true;
            });
        }
        if (validSuggestions.length === 0 && suggestions.length > 0) {
            // If all suggestions are already linked, show the linked text as the only option
            html += `<div class="suggestion-item unclickable" style="cursor: not-allowed; opacity: 0.6;">${selectedText}</div>`;
        } else {
            validSuggestions.forEach(function (suggestion) {
                html += `<a href="#" class="suggestion-item topic-link" data-topic="${encodeURIComponent(suggestion)}">${suggestion}</a>`;
            });
        }
        $('#suggestions-list').html(html);
    }

    // Handle topic suggestion clicks
    $(document).on('click', '.topic-link', function (e) {
        e.preventDefault();
        const topic = decodeURIComponent($(this).data('topic'));
        // Only link the chosen suggestion, not the whole selection
        const chosenText = topic;
        convertSelectedTextToLink(chosenText, topic);
        closeTopicSuggestionModal();
        window.location.href = `/${encodeURIComponent(topic)}`;
    });

    // Function to convert selected text to a link
    function convertSelectedTextToLink(chosenText, topic) {
        const articleContent = $('#article-content');
        const content = articleContent.html();
        // Create the link HTML
        const linkHtml = `<a href="/${encodeURIComponent(topic)}">${chosenText}</a>`;
        // Replace only the first occurrence of the chosen text that is not already inside a link
        // Use a DOM approach for safety
        let replaced = false;
        articleContent.find('*').addBack().contents().each(function () {
            if (this.nodeType === 3 && !isNodeInsideLink(this)) {
                const idx = this.data.indexOf(chosenText);
                if (idx !== -1 && !replaced) {
                    const before = this.data.slice(0, idx);
                    const after = this.data.slice(idx + chosenText.length);
                    const newNode = document.createElement('span');
                    if (before) newNode.appendChild(document.createTextNode(before));
                    const linkNode = document.createElement('a');
                    linkNode.href = `/${encodeURIComponent(topic)}`;
                    linkNode.textContent = chosenText;
                    newNode.appendChild(linkNode);
                    if (after) newNode.appendChild(document.createTextNode(after));
                    $(this).replaceWith(newNode);
                    replaced = true;
                }
            }
        });
        // Persist the new reference to the backend
        saveTopicLinkToBackend(chosenText, topic);
    }

    // Function to save the topic link to backend (now implemented)
    function saveTopicLinkToBackend(selectedText, topic) {
        // Get the current article topic from the page (assume it's in a header or variable)
        let articleTopic = $(".page-topic-header h1").text().trim() || currentTopic;
        $.ajax({
            url: '/add_reference',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                article_topic: articleTopic,
                selected_text: selectedText,
                reference_topic: topic
            }),
            success: function (response) {
                if (response && response.updated_content) {
                    $('#article-content').html(response.updated_content);
                }
            },
            error: function (xhr) {
                console.error('Error saving topic link to backend:', xhr);
            }
        });
    }

    // Custom topic generation with validation
    $('#generate-custom-btn').click(function () {
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
    $('#custom-topic-input').on('input', function () {
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

    $('#custom-topic-input').keypress(function (e) {
        if (e.which === 13) { $('#generate-custom-btn').click(); }
    });

    // Modal close logic
    $('#close-topic-suggestion').click(closeTopicSuggestionModal);
    $(window).on('mousedown', function (e) {
        if ($(e.target).is('#topic-suggestion-modal')) closeTopicSuggestionModal();
    });

    // --- Accessibility: focus trap and ESC close ---
    $(document).on('keydown', function (e) {
        if ($('#topic-suggestion-modal').is(':visible')) {
            if (e.key === 'Escape') closeTopicSuggestionModal();
        }
    });

    // --- Add blur CSS ---
    if (!$('style#modal-blur-style').length) {
        $('head').append('<style id="modal-blur-style">.modal-blur { filter: blur(4px) !important; transition: filter 0.2s; }</style>');
    }
});












