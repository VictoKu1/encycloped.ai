# Hamburger Menu Documentation

The hamburger menu is a navigation feature that provides users with quick access to their recently viewed topics. It's implemented using client-side JavaScript and local browser storage.

## Overview

The hamburger menu appears on all pages of the encycloped.ai website and allows users to:
- View recently visited topics
- Navigate back to previously viewed articles
- Access topics sorted by most recent first
- Persist navigation history across browser sessions

## Features

### 🍔 **Hamburger Menu Button**
- **Position**: Top-left corner on all pages
- **Design**: Three horizontal lines that animate when clicked
- **Color**: Light background (#f2f2f2) with dark lines (#2c3e50)
- **Responsive**: Works on desktop and mobile devices

### 📋 **Recent Topics Sidebar**
- **Width**: 300px
- **Position**: Slides in from the left
- **Background**: Dark theme (#2c3e50)
- **Content**: List of recently viewed topics with timestamps

### 💾 **Local Storage**
- **Storage Key**: `encycloped_ai_recent_topics`
- **Capacity**: Up to 20 recent topics
- **Persistence**: Survives browser restarts
- **Data Format**: JSON array with topic metadata

## User Interface

### Visual Design

#### Hamburger Button
```css
.hamburger-menu {
    background-color: #f2f2f2;
    border: none;
    cursor: pointer;
    padding: 8px;
    margin-right: 15px;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    width: 30px;
    height: 30px;
    z-index: 1001;
    position: relative;
    border-radius: 4px;
}
```

#### Sidebar
```css
.sidebar {
    position: fixed;
    top: 0;
    left: -300px;
    width: 300px;
    height: 100vh;
    background-color: #2c3e50;
    color: white;
    transition: left 0.3s ease;
    z-index: 1003;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}
```

### Animation States

#### Closed State
- Sidebar positioned off-screen (`left: -300px`)
- Hamburger button shows three horizontal lines
- Overlay is hidden

#### Open State
- Sidebar slides in (`left: 0`)
- Hamburger button transforms to X shape
- Overlay appears with semi-transparent background

## Functionality

### Topic Tracking

Topics are automatically tracked when users visit article pages:

```javascript
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
```

### Data Structure

Each recent topic entry contains:

```javascript
{
    "topic": "Python (Programming Language)",
    "timestamp": 1703123456789,
    "url": "http://localhost:5000/python%20%28programming%20language%29"
}
```

### Time Display

Topics show relative time since last visit:

- "Just now" - Less than 1 minute
- "5m ago" - 1-59 minutes
- "2h ago" - 1-23 hours
- "3d ago" - 1-6 days
- "12/15/2023" - More than 7 days

## User Interactions

### Opening the Menu

Users can open the hamburger menu by:
1. **Clicking the hamburger button** - Primary method
2. **Keyboard shortcut** - Not currently implemented

### Closing the Menu

Users can close the hamburger menu by:
1. **Clicking the X button** in the sidebar header
2. **Clicking the overlay** outside the sidebar
3. **Pressing the Escape key** on keyboard
4. **Clicking a topic link** (navigates and closes menu)

### Navigation

Users can navigate to topics by:
1. **Clicking any topic** in the recent topics list
2. **Topics are clickable links** that navigate to the article page
3. **Menu automatically closes** after navigation

## Implementation Details

### HTML Structure

The hamburger menu is implemented in all templates:

#### Base Template (`templates/base.html`)
```html
<!-- Hamburger Menu Button -->
<button id="hamburger-menu" class="hamburger-menu" title="Recent Topics">
  <span></span>
  <span></span>
  <span></span>
</button>

<!-- Sidebar for Recent Topics -->
<div id="sidebar" class="sidebar">
  <div class="sidebar-header">
    <h3>Recent Topics</h3>
    <button id="close-sidebar" class="close-sidebar">&times;</button>
  </div>
  <div class="sidebar-content">
    <div id="recent-topics-list" class="recent-topics-list">
      <p class="no-topics">No recent topics yet</p>
    </div>
  </div>
</div>

<!-- Overlay for sidebar -->
<div id="sidebar-overlay" class="sidebar-overlay"></div>
```

#### Topic Template (`templates/topic.html`)
The hamburger menu is positioned next to the site name in the header.

#### Index Template (`templates/index.html`)
The hamburger menu is positioned at the top-left corner, separate from the centered site name.

### JavaScript Implementation

#### Core Functions

```javascript
// Toggle sidebar visibility
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

// Update the display of recent topics
function updateRecentTopicsDisplay() {
    const recentTopics = JSON.parse(localStorage.getItem(RECENT_TOPICS_KEY) || '[]');
    const $list = $('#recent-topics-list');
    
    if (recentTopics.length === 0) {
        $list.html('<p class="no-topics">No recent topics yet</p>');
        return;
    }
    
    let html = '';
    recentTopics.forEach(function(item) {
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
```

#### Event Handlers

```javascript
// Hamburger menu click
$('#hamburger-menu').click(function(e) {
    e.preventDefault();
    e.stopPropagation();
    toggleSidebar();
});

// Close sidebar
$('#close-sidebar').click(function(e) {
    e.preventDefault();
    closeSidebar();
});

// Overlay click to close
$('#sidebar-overlay').click(function(e) {
    e.preventDefault();
    closeSidebar();
});

// Escape key to close
$(document).keydown(function(e) {
    if (e.key === 'Escape' && $('#sidebar').hasClass('open')) {
        closeSidebar();
    }
});
```

### CSS Styling

#### Z-Index Layering

The hamburger menu uses a layered z-index system:

- **Sidebar**: `z-index: 1003` (highest priority)
- **Sidebar Overlay**: `z-index: 1002`
- **Hamburger Button (normal)**: `z-index: 1002`
- **Hamburger Button (when sidebar open)**: `z-index: 1001` (covered by sidebar)

This ensures the sidebar covers the hamburger button when open, preventing accidental clicks.

#### Responsive Design

The hamburger menu is designed to work on all screen sizes:

- **Desktop**: Full sidebar with 300px width
- **Mobile**: Same functionality, optimized for touch
- **Tablet**: Responsive layout that adapts to screen size

## Browser Compatibility

### Supported Browsers

- **Chrome**: 60+
- **Firefox**: 55+
- **Safari**: 12+
- **Edge**: 79+

### Required Features

- **localStorage**: For storing recent topics
- **CSS3 Transitions**: For smooth animations
- **ES6 Features**: Arrow functions, const/let
- **jQuery**: For DOM manipulation

## Performance Considerations

### Local Storage Limits

- **Storage Capacity**: Typically 5-10MB per domain
- **Recent Topics Limit**: 20 topics maximum
- **Data Size**: ~1KB per topic entry
- **Total Usage**: ~20KB for full recent topics list

### Memory Usage

- **JavaScript Objects**: Minimal memory footprint
- **DOM Elements**: Lightweight sidebar structure
- **Event Listeners**: Efficient event delegation

## Accessibility

### Keyboard Navigation

- **Tab Navigation**: Hamburger button is focusable
- **Enter/Space**: Activates hamburger button
- **Escape**: Closes sidebar
- **Focus Management**: Focus returns to hamburger button when closed

### Screen Reader Support

- **ARIA Labels**: Hamburger button has descriptive title
- **Semantic HTML**: Proper button and heading elements
- **Focus Indicators**: Visible focus states

### Visual Accessibility

- **High Contrast**: Dark sidebar with light text
- **Large Touch Targets**: 30px minimum button size
- **Clear Visual States**: Obvious open/closed states

## Troubleshooting

### Common Issues

#### Topics Not Saving
- **Cause**: JavaScript disabled or localStorage blocked
- **Solution**: Enable JavaScript and allow localStorage

#### Menu Not Opening
- **Cause**: JavaScript errors or missing dependencies
- **Solution**: Check browser console for errors

#### Styling Issues
- **Cause**: CSS not loading or conflicts
- **Solution**: Check CSS file loading and z-index conflicts

### Debug Information

Enable debug logging by opening browser console:

```javascript
// Check recent topics storage
console.log(localStorage.getItem('encycloped_ai_recent_topics'));

// Check if sidebar elements exist
console.log($('#sidebar').length);
console.log($('#hamburger-menu').length);
```

## Future Enhancements

### Planned Features

1. **Search in Recent Topics**: Filter recent topics by name
2. **Topic Categories**: Group topics by type or subject
3. **Export/Import**: Backup and restore recent topics
4. **Sync Across Devices**: Cloud storage integration
5. **Customizable Limit**: User-configurable topic limit

### Potential Improvements

1. **Keyboard Shortcuts**: Customizable hotkeys
2. **Drag and Drop**: Reorder recent topics
3. **Topic Previews**: Hover to see topic content
4. **Favorites**: Mark important topics
5. **History Analytics**: Usage statistics and insights

## API Reference

### JavaScript Functions

#### `saveTopicToRecent(topic)`
Saves a topic to the recent topics list.

**Parameters:**
- `topic` (string): The topic name to save

**Returns:** `undefined`

#### `updateRecentTopicsDisplay()`
Updates the sidebar display with current recent topics.

**Parameters:** None

**Returns:** `undefined`

#### `toggleSidebar()`
Toggles the sidebar open/closed state.

**Parameters:** None

**Returns:** `undefined`

#### `closeSidebar()`
Closes the sidebar.

**Parameters:** None

**Returns:** `undefined`

#### `getTimeAgo(timestamp)`
Converts timestamp to human-readable time ago string.

**Parameters:**
- `timestamp` (number): Unix timestamp in milliseconds

**Returns:** `string` - Human-readable time ago string

### CSS Classes

#### `.hamburger-menu`
Main hamburger button styling.

#### `.hamburger-menu.active`
Active state when sidebar is open.

#### `.sidebar`
Main sidebar container.

#### `.sidebar.open`
Open state of the sidebar.

#### `.recent-topic-item`
Individual topic item in the list.

#### `.sidebar-overlay`
Background overlay when sidebar is open.

## Conclusion

The hamburger menu provides an intuitive way for users to navigate their recent browsing history within the encycloped.ai website. It's implemented using modern web technologies and follows accessibility best practices, ensuring a good user experience across all devices and browsers.

For technical implementation details, see the [Developer Guide](DEVELOPER_GUIDE.md#hamburger-menu-implementation).
